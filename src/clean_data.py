#!/usr/bin/env python3
"""Clean OpenFootball CSV data into ontology-ready entity tables."""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT_ROOT / "config/seasons.csv"
DEFAULT_ALIASES = PROJECT_ROOT / "config/team-aliases.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data/processed"

REQUIRED_SOURCE_COLUMNS = {"Round", "Date", "Team 1", "FT", "Team 2"}
REQUIRED_MANIFEST_COLUMNS = {
    "season_id",
    "label",
    "source_file",
    "expected_matches",
    "expected_teams",
}
REQUIRED_ALIAS_COLUMNS = {"source_name", "team_id", "name"}
SCORE_PATTERN = re.compile(r"^(\d+)\s*[-–—]\s*(\d+)$")
DATE_PATTERN = re.compile(
    r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+"
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+"
    r"(\d{1,2})\s+(\d{4})(?:\s*\([^)]*\))?$"
)
SEASON_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


class DataValidationError(ValueError):
    """Raised when a source row or the complete dataset is invalid."""


@dataclass(frozen=True)
class Match:
    match_id: str
    competition_id: str
    season_id: str
    round: int
    match_date: str
    home_team_id: str
    away_team_id: str
    home_goals: int
    away_goals: int
    source_file: str
    source_line: int


@dataclass(frozen=True)
class Team:
    team_id: str
    name: str


@dataclass(frozen=True)
class Competition:
    competition_id: str
    name: str
    country: str
    competition_type: str
    tier: int


@dataclass(frozen=True)
class Season:
    season_id: str
    label: str
    competition_id: str
    start_date: str
    end_date: str
    source_file: str


@dataclass(frozen=True)
class SeasonSource:
    season_id: str
    label: str
    source_file: str
    expected_matches: int
    expected_teams: int


def compact_whitespace(value: str) -> str:
    return " ".join(value.strip().split())


def slugify_team_name(name: str) -> str:
    """Create a stable URI-safe ID while dropping common club abbreviations."""
    normalized = unicodedata.normalize("NFKD", compact_whitespace(name))
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_name = ascii_name.replace("&", " and ")
    tokens = re.findall(r"[a-z0-9]+", ascii_name)
    tokens = [token for token in tokens if token not in {"afc", "fc"}]
    if not tokens:
        raise DataValidationError(f"Cannot generate a team ID from {name!r}")
    return "-".join(tokens)


def parse_source_date(value: str) -> date:
    cleaned = compact_whitespace(value)
    match = DATE_PATTERN.fullmatch(cleaned)
    if not match:
        raise DataValidationError(f"Unsupported date format: {value!r}")

    weekday, month_name, day_text, year_text = match.groups()
    try:
        parsed = date(int(year_text), MONTHS[month_name], int(day_text))
    except ValueError as exc:
        raise DataValidationError(f"Invalid date: {value!r}") from exc

    if parsed.strftime("%a") != weekday:
        raise DataValidationError(f"Incorrect weekday in date: {value!r}")
    return parsed


def parse_score(value: str) -> tuple[int, int]:
    match = SCORE_PATTERN.fullmatch(compact_whitespace(value))
    if not match:
        raise DataValidationError(f"Unsupported full-time score: {value!r}")
    return int(match.group(1)), int(match.group(2))


def parse_positive_int(value: str, field_name: str) -> int:
    try:
        number = int(value.strip())
    except (AttributeError, ValueError) as exc:
        raise DataValidationError(f"{field_name} must be an integer: {value!r}") from exc
    if number < 1:
        raise DataValidationError(f"{field_name} must be positive: {value!r}")
    return number


def read_table(path: Path, required_columns: set[str]) -> list[dict[str, str]]:
    try:
        source = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise DataValidationError(f"Cannot open {path}: {exc}") from exc

    with source:
        reader = csv.DictReader(source)
        columns = {column.strip() for column in (reader.fieldnames or [])}
        missing = required_columns - columns
        if missing:
            raise DataValidationError(
                f"{path.name} is missing columns: {', '.join(sorted(missing))}"
            )
        rows = [
            {key.strip(): (value or "").strip() for key, value in row.items()}
            for row in reader
        ]
    if not rows:
        raise DataValidationError(f"{path.name} contains no rows")
    return rows


def load_manifest(path: Path) -> list[SeasonSource]:
    """Read the checked list of source files, one complete league season each."""
    sources: list[SeasonSource] = []
    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    for line_number, row in enumerate(
        read_table(path, REQUIRED_MANIFEST_COLUMNS), start=2
    ):
        try:
            season_id = row["season_id"]
            if not SEASON_ID_PATTERN.fullmatch(season_id):
                raise DataValidationError(f"Invalid season_id: {season_id!r}")
            if season_id in seen_ids:
                raise DataValidationError(f"Duplicate season_id: {season_id}")
            if row["source_file"] in seen_files:
                raise DataValidationError(f"Duplicate source_file: {row['source_file']}")
            if not row["label"]:
                raise DataValidationError("Season label cannot be empty")
            seen_ids.add(season_id)
            seen_files.add(row["source_file"])
            sources.append(
                SeasonSource(
                    season_id=season_id,
                    label=row["label"],
                    source_file=row["source_file"],
                    expected_matches=parse_positive_int(
                        row["expected_matches"], "expected_matches"
                    ),
                    expected_teams=parse_positive_int(
                        row["expected_teams"], "expected_teams"
                    ),
                )
            )
        except DataValidationError as exc:
            raise DataValidationError(f"{path.name}: line {line_number}: {exc}") from exc
    return sources


def load_aliases(path: Path) -> dict[str, Team]:
    """Map every source spelling of a club to one reviewed, persistent identity.

    The canonical display name must slugify to the team ID, so an ID can never
    silently drift away from the club it names. Unknown source spellings are
    rejected later instead of being guessed from their slug.
    """
    aliases: dict[str, Team] = {}
    names_by_id: dict[str, str] = {}
    for line_number, row in enumerate(read_table(path, REQUIRED_ALIAS_COLUMNS), start=2):
        try:
            source_name = compact_whitespace(row["source_name"])
            team = Team(team_id=row["team_id"], name=compact_whitespace(row["name"]))
            if not source_name or not team.team_id or not team.name:
                raise DataValidationError("Alias rows cannot contain empty values")
            if source_name in aliases:
                raise DataValidationError(f"Duplicate source_name: {source_name!r}")
            if slugify_team_name(team.name) != team.team_id:
                raise DataValidationError(
                    f"team_id {team.team_id!r} does not match name {team.name!r}"
                )
            previous_name = names_by_id.setdefault(team.team_id, team.name)
            if previous_name != team.name:
                raise DataValidationError(
                    f"team_id {team.team_id!r} has two names: "
                    f"{previous_name!r} and {team.name!r}"
                )
            aliases[source_name] = team
        except DataValidationError as exc:
            raise DataValidationError(f"{path.name}: line {line_number}: {exc}") from exc
    return aliases


def load_matches(
    input_path: Path,
    competition_id: str,
    season_id: str,
    aliases: dict[str, Team],
    source_file: str | None = None,
) -> list[Match]:
    matches: list[Match] = []
    seen_match_ids: set[str] = set()
    source_reference = source_file or input_path.as_posix()

    try:
        source = input_path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise DataValidationError(f"Cannot open input file {input_path}: {exc}") from exc

    with source:
        reader = csv.DictReader(source)
        source_columns = {column.strip() for column in (reader.fieldnames or [])}
        missing_columns = REQUIRED_SOURCE_COLUMNS - source_columns
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise DataValidationError(
                f"{input_path.name} is missing columns: {missing}"
            )

        for line_number, row in enumerate(reader, start=2):
            try:
                round_number = parse_positive_int(row["Round"], "Round")
                match_date = parse_source_date(row["Date"])
                home_name = compact_whitespace(row["Team 1"])
                away_name = compact_whitespace(row["Team 2"])
                home_goals, away_goals = parse_score(row["FT"])

                if not home_name or not away_name:
                    raise DataValidationError("Team names cannot be empty")
                for name in (home_name, away_name):
                    if name not in aliases:
                        raise DataValidationError(
                            f"Unknown team name {name!r}; review it and add it to "
                            f"the alias table (suggested ID: "
                            f"{slugify_team_name(name)!r})"
                        )
                home_team_id = aliases[home_name].team_id
                away_team_id = aliases[away_name].team_id
                if home_team_id == away_team_id:
                    raise DataValidationError("Home and away teams cannot be identical")

                match_id = f"{match_date.isoformat()}-{home_team_id}-{away_team_id}"
                if match_id in seen_match_ids:
                    raise DataValidationError(f"Duplicate match ID: {match_id}")
                seen_match_ids.add(match_id)

                matches.append(
                    Match(
                        match_id=match_id,
                        competition_id=competition_id,
                        season_id=season_id,
                        round=round_number,
                        match_date=match_date.isoformat(),
                        home_team_id=home_team_id,
                        away_team_id=away_team_id,
                        home_goals=home_goals,
                        away_goals=away_goals,
                        source_file=source_reference,
                        source_line=line_number,
                    )
                )
            except (KeyError, TypeError, AttributeError, DataValidationError) as exc:
                raise DataValidationError(
                    f"{input_path.name}: line {line_number}: {exc}"
                ) from exc

    if not matches:
        raise DataValidationError(f"{input_path.name} contains no matches")
    return matches


def validate_season(
    matches: Sequence[Match],
    expected_matches: int,
    expected_teams: int,
) -> set[str]:
    """Check that one league season is a complete double round-robin."""
    if len(matches) != expected_matches:
        raise DataValidationError(
            f"Expected {expected_matches} matches, found {len(matches)}"
        )

    team_ids = {match.home_team_id for match in matches} | {
        match.away_team_id for match in matches
    }
    if len(team_ids) != expected_teams:
        raise DataValidationError(f"Expected {expected_teams} teams, found {len(team_ids)}")

    fixtures = Counter((match.home_team_id, match.away_team_id) for match in matches)
    repeated = sorted(pair for pair, count in fixtures.items() if count > 1)
    if repeated:
        raise DataValidationError(f"Duplicate home/away fixtures: {repeated[:3]}")
    expected_fixtures = expected_teams * (expected_teams - 1)
    if len(fixtures) != expected_fixtures:
        raise DataValidationError(
            f"Expected {expected_fixtures} distinct home/away fixtures, "
            f"found {len(fixtures)}"
        )

    home_counts = Counter(match.home_team_id for match in matches)
    away_counts = Counter(match.away_team_id for match in matches)
    for team_id in sorted(team_ids):
        if home_counts[team_id] != expected_teams - 1:
            raise DataValidationError(
                f"{team_id} has {home_counts[team_id]} home matches"
            )
        if away_counts[team_id] != expected_teams - 1:
            raise DataValidationError(
                f"{team_id} has {away_counts[team_id]} away matches"
            )

    expected_rounds = 2 * (expected_teams - 1)
    round_counts = Counter(match.round for match in matches)
    if set(round_counts) != set(range(1, expected_rounds + 1)):
        raise DataValidationError(
            f"Expected rounds 1-{expected_rounds}, found {sorted(round_counts)}"
        )
    uneven_rounds = sorted(
        number
        for number, count in round_counts.items()
        if count != expected_teams // 2
    )
    if uneven_rounds:
        raise DataValidationError(f"Rounds with the wrong match count: {uneven_rounds}")
    return team_ids


def write_csv(path: Path, rows: Iterable[object], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def clean_dataset(
    manifest_path: Path,
    aliases_path: Path,
    output_dir: Path,
    competition_id: str,
    competition_name: str,
    country: str,
    tier: int,
    source_root: Path = PROJECT_ROOT,
) -> tuple[int, int, int]:
    if tier < 1:
        raise DataValidationError("League tier must be positive")

    aliases = load_aliases(aliases_path)
    teams_by_id = {team.team_id: team for team in aliases.values()}
    all_matches: list[Match] = []
    seasons: list[Season] = []
    used_team_ids: set[str] = set()
    seen_match_ids: set[str] = set()

    for source in load_manifest(manifest_path):
        matches = load_matches(
            source_root / source.source_file,
            competition_id,
            source.season_id,
            aliases,
            source_file=source.source_file,
        )
        try:
            used_team_ids |= validate_season(
                matches, source.expected_matches, source.expected_teams
            )
        except DataValidationError as exc:
            raise DataValidationError(f"{source.season_id}: {exc}") from exc

        for match in matches:
            if match.match_id in seen_match_ids:
                raise DataValidationError(f"Duplicate match ID: {match.match_id}")
            seen_match_ids.add(match.match_id)

        match_dates = [date.fromisoformat(match.match_date) for match in matches]
        seasons.append(
            Season(
                season_id=source.season_id,
                label=source.label,
                competition_id=competition_id,
                start_date=min(match_dates).isoformat(),
                end_date=max(match_dates).isoformat(),
                source_file=source.source_file,
            )
        )
        all_matches.extend(matches)

    unused_aliases = sorted(set(teams_by_id) - used_team_ids)
    if unused_aliases:
        raise DataValidationError(f"Alias table lists teams without matches: {unused_aliases}")

    teams = [teams_by_id[team_id] for team_id in sorted(used_team_ids)]
    competitions = [
        Competition(competition_id, competition_name, country, "league", tier)
    ]

    write_csv(output_dir / "matches.csv", all_matches, tuple(Match.__dataclass_fields__))
    write_csv(output_dir / "teams.csv", teams, tuple(Team.__dataclass_fields__))
    write_csv(
        output_dir / "competitions.csv",
        competitions,
        tuple(Competition.__dataclass_fields__),
    )
    write_csv(output_dir / "seasons.csv", seasons, tuple(Season.__dataclass_fields__))
    return len(all_matches), len(teams), len(seasons)


def parse_positive_int_arg(value: str) -> int:
    try:
        return parse_positive_int(value, "value")
    except DataValidationError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Clean the OpenFootball league seasons listed in the manifest."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--aliases", type=Path, default=DEFAULT_ALIASES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--competition-id", default="premier-league")
    parser.add_argument("--competition-name", default="English Premier League")
    parser.add_argument("--country", default="England")
    parser.add_argument("--tier", type=parse_positive_int_arg, default=1)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        match_count, team_count, season_count = clean_dataset(
            manifest_path=args.manifest,
            aliases_path=args.aliases,
            output_dir=args.output_dir,
            competition_id=args.competition_id,
            competition_name=args.competition_name,
            country=args.country,
            tier=args.tier,
        )
    except DataValidationError as exc:
        raise SystemExit(f"Data validation failed: {exc}") from exc

    print(
        f"Cleaned {match_count} matches, {team_count} teams "
        f"and {season_count} seasons."
    )
    print(f"Wrote ontology-ready CSV files to {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
