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
DEFAULT_INPUT = PROJECT_ROOT / "england_csv/2010s/2018-19/eng.1.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data/processed"

REQUIRED_SOURCE_COLUMNS = {"Round", "Date", "Team 1", "FT", "Team 2"}
SCORE_PATTERN = re.compile(r"^(\d+)\s*[-\u2013\u2014]\s*(\d+)$")
DATE_PATTERN = re.compile(
    r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+"
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+"
    r"(\d{1,2})\s+(\d{4})(?:\s*\([^)]*\))?$"
)
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


@dataclass(frozen=True)
class Team:
    team_id: str
    name: str


@dataclass(frozen=True)
class Competition:
    competition_id: str
    name: str
    country: str


@dataclass(frozen=True)
class Season:
    season_id: str
    label: str
    competition_id: str
    start_date: str
    end_date: str


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


def load_matches(
    input_path: Path,
    competition_id: str,
    season_id: str,
) -> tuple[list[Match], list[Team]]:
    matches: list[Match] = []
    team_names_by_id: dict[str, str] = {}
    seen_match_ids: set[str] = set()

    try:
        source_file = input_path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise DataValidationError(f"Cannot open input file {input_path}: {exc}") from exc

    with source_file:
        reader = csv.DictReader(source_file)
        source_columns = {column.strip() for column in (reader.fieldnames or [])}
        missing_columns = REQUIRED_SOURCE_COLUMNS - source_columns
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise DataValidationError(f"Source CSV is missing columns: {missing}")

        for line_number, row in enumerate(reader, start=2):
            try:
                round_number = parse_positive_int(row["Round"], "Round")
                match_date = parse_source_date(row["Date"])
                home_name = compact_whitespace(row["Team 1"])
                away_name = compact_whitespace(row["Team 2"])
                home_goals, away_goals = parse_score(row["FT"])

                if not home_name or not away_name:
                    raise DataValidationError("Team names cannot be empty")
                if home_name == away_name:
                    raise DataValidationError("Home and away teams cannot be identical")

                home_team_id = slugify_team_name(home_name)
                away_team_id = slugify_team_name(away_name)
                if home_team_id == away_team_id:
                    raise DataValidationError("Home and away team IDs cannot be identical")

                for team_id, team_name in (
                    (home_team_id, home_name),
                    (away_team_id, away_name),
                ):
                    previous_name = team_names_by_id.setdefault(team_id, team_name)
                    if previous_name != team_name:
                        raise DataValidationError(
                            f"Team ID collision for {team_id!r}: "
                            f"{previous_name!r} and {team_name!r}"
                        )

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
                    )
                )
            except (KeyError, TypeError, DataValidationError) as exc:
                raise DataValidationError(f"Line {line_number}: {exc}") from exc

    if not matches:
        raise DataValidationError("Source CSV contains no matches")

    teams = [
        Team(team_id=team_id, name=name)
        for team_id, name in sorted(team_names_by_id.items())
    ]
    return matches, teams


def validate_dataset(
    matches: Sequence[Match],
    teams: Sequence[Team],
    expected_matches: int | None,
    expected_teams: int | None,
) -> None:
    if expected_matches is not None and len(matches) != expected_matches:
        raise DataValidationError(
            f"Expected {expected_matches} matches, found {len(matches)}"
        )
    if expected_teams is not None and len(teams) != expected_teams:
        raise DataValidationError(f"Expected {expected_teams} teams, found {len(teams)}")

    known_team_ids = {team.team_id for team in teams}
    appearances: Counter[str] = Counter()
    for match in matches:
        if match.home_team_id not in known_team_ids:
            raise DataValidationError(f"Unknown home team: {match.home_team_id}")
        if match.away_team_id not in known_team_ids:
            raise DataValidationError(f"Unknown away team: {match.away_team_id}")
        appearances.update((match.home_team_id, match.away_team_id))

    unused_teams = known_team_ids - appearances.keys()
    if unused_teams:
        raise DataValidationError(f"Teams without matches: {sorted(unused_teams)}")


def write_csv(path: Path, rows: Iterable[object], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def clean_dataset(
    input_path: Path,
    output_dir: Path,
    competition_id: str,
    competition_name: str,
    country: str,
    season_id: str,
    season_label: str,
    expected_matches: int | None,
    expected_teams: int | None,
) -> tuple[int, int]:
    matches, teams = load_matches(input_path, competition_id, season_id)
    validate_dataset(matches, teams, expected_matches, expected_teams)

    match_dates = [date.fromisoformat(match.match_date) for match in matches]
    competitions = [Competition(competition_id, competition_name, country)]
    seasons = [
        Season(
            season_id=season_id,
            label=season_label,
            competition_id=competition_id,
            start_date=min(match_dates).isoformat(),
            end_date=max(match_dates).isoformat(),
        )
    ]

    write_csv(
        output_dir / "matches.csv",
        matches,
        tuple(Match.__dataclass_fields__),
    )
    write_csv(
        output_dir / "teams.csv",
        teams,
        tuple(Team.__dataclass_fields__),
    )
    write_csv(
        output_dir / "competitions.csv",
        competitions,
        tuple(Competition.__dataclass_fields__),
    )
    write_csv(
        output_dir / "seasons.csv",
        seasons,
        tuple(Season.__dataclass_fields__),
    )
    return len(matches), len(teams)


def optional_positive_count(value: str) -> int | None:
    count = int(value)
    if count < 0:
        raise argparse.ArgumentTypeError("count cannot be negative")
    return count or None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Clean an OpenFootball league CSV into ontology-ready tables."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--competition-id", default="premier-league")
    parser.add_argument("--competition-name", default="English Premier League")
    parser.add_argument("--country", default="England")
    parser.add_argument("--season-id", default="2018-19")
    parser.add_argument("--season-label", default="2018/19")
    parser.add_argument(
        "--expected-matches",
        type=optional_positive_count,
        default=380,
        help="Expected match count; use 0 to disable this check (default: 380).",
    )
    parser.add_argument(
        "--expected-teams",
        type=optional_positive_count,
        default=20,
        help="Expected team count; use 0 to disable this check (default: 20).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        match_count, team_count = clean_dataset(
            input_path=args.input,
            output_dir=args.output_dir,
            competition_id=args.competition_id,
            competition_name=args.competition_name,
            country=args.country,
            season_id=args.season_id,
            season_label=args.season_label,
            expected_matches=args.expected_matches,
            expected_teams=args.expected_teams,
        )
    except DataValidationError as exc:
        raise SystemExit(f"Data validation failed: {exc}") from exc

    print(f"Cleaned {match_count} matches and {team_count} teams.")
    print(f"Wrote ontology-ready CSV files to {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
