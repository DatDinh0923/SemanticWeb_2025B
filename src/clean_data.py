#!/usr/bin/env python3
"""Clean every OpenFootball England CSV into ontology-ready entity tables."""

from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = PROJECT_ROOT / "england_csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data/processed"

REQUIRED_SOURCE_COLUMNS = {"Round", "Date", "Team 1", "FT", "Team 2"}
SCORE_PATTERN = re.compile(r"^(\d+)\s*[-–—]\s*(\d+)$")
SEASON_DIR_PATTERN = re.compile(r"^(\d{4})-(\d{2})$")

# Short or nickname spellings used by some source files.
TEAM_ALIASES = {
    "Brighton": "Brighton & Hove Albion FC",
    "Manchester Utd": "Manchester United FC",
    "Newcastle Utd": "Newcastle United FC",
    "Sheffield Utd": "Sheffield United FC",
    "Tottenham": "Tottenham Hotspur FC",
    "West Brom": "West Bromwich Albion FC",
    "West Ham": "West Ham United FC",
    "Wolves": "Wolverhampton Wanderers FC",
}
# Clubs whose generic slug would collide with a different club.
TEAM_ID_OVERRIDES = {
    "AFC Wimbledon": "afc-wimbledon",  # founded 2002, not Wimbledon FC
}


class DataValidationError(ValueError):
    """Raised when a source row or the complete dataset is invalid."""


@dataclass(frozen=True)
class Match:
    match_id: str
    competition_id: str
    season_id: str
    round: str
    match_date: str
    home_team_id: str
    away_team_id: str
    home_goals: int
    away_goals: int


@dataclass(frozen=True)
class Team:
    team_id: str
    name: str


@dataclass(frozen=True)
class Competition:
    competition_id: str
    name: str
    tier: int | None  # None for knockout cups


@dataclass(frozen=True)
class Season:
    season_id: str
    label: str
    competition_id: str
    start_date: str
    end_date: str


COMPETITIONS = {
    c.competition_id: c
    for c in (
        Competition("premier-league", "Premier League", 1),
        Competition("first-division", "Football League First Division", 2),
        Competition("second-division", "Football League Second Division", 3),
        Competition("third-division", "Football League Third Division", 4),
        Competition("championship", "EFL Championship", 2),
        Competition("league-one", "EFL League One", 3),
        Competition("league-two", "EFL League Two", 4),
        Competition("national-league", "National League", 5),
        Competition("fa-cup", "FA Cup", None),
    )
}


def competition_id_for(file_stem: str, start_year: int) -> str:
    """Map an OpenFootball file name to a competition, respecting the 2004 rename."""
    renamed = start_year >= 2004
    by_stem = {
        "eng.1": "premier-league",
        "eng.2": "championship" if renamed else "first-division",
        "eng.3": "league-one" if renamed else "second-division",
        "eng.4": "league-two" if renamed else "third-division",
        "eng.5": "national-league",
        "eng.cup": "fa-cup",
    }
    if file_stem not in by_stem:
        raise DataValidationError(f"Unknown competition file: {file_stem}")
    return by_stem[file_stem]


def compact_whitespace(value: str) -> str:
    return " ".join(value.strip().split())


def canonical_team_name(name: str) -> str:
    """Resolve aliases and drop disambiguation notes such as '(1992-2011)'."""
    name = compact_whitespace(name)
    name = TEAM_ALIASES.get(name, name)
    return compact_whitespace(re.sub(r"\([^)]*\)", "", name))


def slugify_team_name(name: str) -> str:
    """Create a stable URI-safe ID while dropping common club abbreviations."""
    if name in TEAM_ID_OVERRIDES:
        return TEAM_ID_OVERRIDES[name]
    normalized = unicodedata.normalize("NFKD", compact_whitespace(name))
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_name = ascii_name.replace("&", " and ")
    tokens = re.findall(r"[a-z0-9]+", ascii_name)
    tokens = [token for token in tokens if token not in {"afc", "fc"}]
    if not tokens:
        raise DataValidationError(f"Cannot generate a team ID from {name!r}")
    return "-".join(tokens)


def parse_source_date(value: str) -> date:
    """Parse 'Sat Aug 15 1992', ignoring notes like '(P)' for postponed matches."""
    cleaned = compact_whitespace(re.sub(r"\([^)]*\)", "", value))
    try:
        parsed = datetime.strptime(cleaned, "%a %b %d %Y").date()
    except ValueError as exc:
        raise DataValidationError(f"Unsupported date: {value!r}") from exc
    if parsed.strftime("%a") != cleaned[:3]:  # strptime does not check the weekday
        raise DataValidationError(f"Incorrect weekday in date: {value!r}")
    return parsed


def parse_score(value: str) -> tuple[int, int]:
    match = SCORE_PATTERN.fullmatch(compact_whitespace(value))
    if not match:
        raise DataValidationError(f"Unsupported full-time score: {value!r}")
    return int(match.group(1)), int(match.group(2))


def parse_round(value: str, is_cup: bool) -> str:
    """League rounds are matchday numbers; cup rounds are named stages."""
    cleaned = compact_whitespace(value)
    if is_cup:
        if not cleaned:
            raise DataValidationError("Cup round cannot be empty")
        return cleaned
    try:
        number = int(cleaned)
    except ValueError as exc:
        raise DataValidationError(f"Round must be an integer: {value!r}") from exc
    if number < 1:
        raise DataValidationError(f"Round must be positive: {value!r}")
    return str(number)


def load_matches(
    input_path: Path,
    competition_id: str,
    season_id: str,
    team_names: dict[str, str],
) -> tuple[list[Match], int]:
    """Parse one source file. Returns played matches and the count of unplayed rows.

    `team_names` is shared across files so every team gets one ID and one name.
    """
    matches: list[Match] = []
    skipped = 0
    is_cup = COMPETITIONS[competition_id].tier is None

    with input_path.open(encoding="utf-8-sig", newline="") as source_file:
        reader = csv.DictReader(source_file)
        source_columns = {column.strip() for column in (reader.fieldnames or [])}
        missing_columns = REQUIRED_SOURCE_COLUMNS - source_columns
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise DataValidationError(f"Source CSV is missing columns: {missing}")

        for line_number, row in enumerate(reader, start=2):
            try:
                # Fixtures without a result: postponed, cancelled (2019-20 COVID
                # curtailment) or not yet played when the source was exported.
                if not compact_whitespace(row["FT"]):
                    skipped += 1
                    continue

                round_label = parse_round(row["Round"], is_cup)
                match_date = parse_source_date(row["Date"])
                home_name = canonical_team_name(row["Team 1"])
                away_name = canonical_team_name(row["Team 2"])
                home_goals, away_goals = parse_score(row["FT"])

                if not home_name or not away_name:
                    raise DataValidationError("Team names cannot be empty")

                home_team_id = slugify_team_name(home_name)
                away_team_id = slugify_team_name(away_name)
                if home_team_id == away_team_id:
                    raise DataValidationError("Home and away team IDs cannot be identical")

                for team_id, team_name in (
                    (home_team_id, home_name),
                    (away_team_id, away_name),
                ):
                    # "Arsenal" and "Arsenal FC" share an ID; keep the fuller name.
                    previous = team_names.get(team_id, "")
                    if len(team_name) > len(previous):
                        team_names[team_id] = team_name

                matches.append(
                    Match(
                        match_id=f"{match_date.isoformat()}-{home_team_id}-{away_team_id}",
                        competition_id=competition_id,
                        season_id=season_id,
                        round=round_label,
                        match_date=match_date.isoformat(),
                        home_team_id=home_team_id,
                        away_team_id=away_team_id,
                        home_goals=home_goals,
                        away_goals=away_goals,
                    )
                )
            except (KeyError, TypeError, DataValidationError) as exc:
                raise DataValidationError(f"{input_path} line {line_number}: {exc}") from exc

    return matches, skipped


def league_season_warnings(matches: Sequence[Match]) -> list[str]:
    """A complete double round-robin has n*(n-1) matches, each team n-1 at home.

    Deviations are reported, not fatal: the source has a few known errors
    (e.g. Bury v Brentford listed twice at Bury in 2000-01).
    """
    home_counts = Counter(match.home_team_id for match in matches)
    away_counts = Counter(match.away_team_id for match in matches)
    team_count = len(home_counts.keys() | away_counts.keys())
    season_id = matches[0].season_id
    warnings = []
    expected = team_count * (team_count - 1)
    if len(matches) != expected:
        warnings.append(f"{season_id}: expected {expected} matches, found {len(matches)}")
    uneven = {t: n for t, n in home_counts.items() if n != team_count - 1}
    if uneven:
        warnings.append(f"{season_id}: uneven home fixtures {uneven}")
    return warnings


def find_source_files(source_root: Path) -> list[tuple[Path, str, int]]:
    """Return (path, season folder name, season start year) for every data file."""
    sources = []
    for path in sorted(source_root.glob("*/*/eng.*.csv")):
        season_match = SEASON_DIR_PATTERN.fullmatch(path.parent.name)
        if not season_match:
            raise DataValidationError(f"Unexpected season folder: {path.parent}")
        sources.append((path, path.parent.name, int(season_match.group(1))))
    if not sources:
        raise DataValidationError(f"No eng.*.csv files found under {source_root}")
    return sources


def write_csv(path: Path, rows: Iterable[object], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def clean_all(source_root: Path, output_dir: Path) -> dict[str, int]:
    team_names: dict[str, str] = {}
    all_matches: list[Match] = []
    seasons: list[Season] = []
    skipped_total = 0

    for path, season_name, start_year in find_source_files(source_root):
        competition_id = competition_id_for(path.stem, start_year)
        season_id = f"{competition_id}-{season_name}"
        matches, skipped = load_matches(path, competition_id, season_id, team_names)
        skipped_total += skipped
        if not matches:
            continue
        if skipped == 0 and COMPETITIONS[competition_id].tier is not None:
            for warning in league_season_warnings(matches):
                print(f"WARNING {warning}", file=sys.stderr)

        match_dates = [match.match_date for match in matches]
        seasons.append(
            Season(
                season_id=season_id,
                label=f"{season_name[:4]}/{season_name[5:]}",
                competition_id=competition_id,
                start_date=min(match_dates),
                end_date=max(match_dates),
            )
        )
        all_matches.extend(matches)

    duplicates = [i for i, n in Counter(m.match_id for m in all_matches).items() if n > 1]
    if duplicates:
        raise DataValidationError(f"Duplicate match IDs: {duplicates[:5]}")
    teams = [Team(team_id, name) for team_id, name in sorted(team_names.items())]
    used_competitions = {season.competition_id for season in seasons}
    competitions = [c for c in COMPETITIONS.values() if c.competition_id in used_competitions]

    write_csv(output_dir / "matches.csv", all_matches, tuple(Match.__dataclass_fields__))
    write_csv(output_dir / "teams.csv", teams, tuple(Team.__dataclass_fields__))
    write_csv(
        output_dir / "competitions.csv",
        competitions,
        tuple(Competition.__dataclass_fields__),
    )
    write_csv(output_dir / "seasons.csv", seasons, tuple(Season.__dataclass_fields__))
    return {
        "matches": len(all_matches),
        "teams": len(teams),
        "seasons": len(seasons),
        "competitions": len(competitions),
        "skipped_unplayed": skipped_total,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    try:
        counts = clean_all(args.source_root, args.output_dir)
    except DataValidationError as exc:
        raise SystemExit(f"Data validation failed: {exc}") from exc

    print(", ".join(f"{key}={value}" for key, value in counts.items()))
    print(f"Wrote ontology-ready CSV files to {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
