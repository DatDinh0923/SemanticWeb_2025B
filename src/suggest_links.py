#!/usr/bin/env python3
"""Suggest Wikidata candidates without changing verified entity links."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data/processed"
VERIFIED_LINKS = PROJECT_ROOT / "data/links/entity-links.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/links/wikidata-suggestions.csv"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "SemanticWeb-2025B-link-suggester/1.0 (educational project)"

OUTPUT_FIELDS = (
    "entity_type",
    "entity_id",
    "local_label",
    "rank",
    "wikidata_uri",
    "candidate_label",
    "candidate_description",
    "verification_status",
    "notes",
)


class SuggestionError(ValueError):
    """Raised when link candidates cannot be produced safely."""


@dataclass(frozen=True)
class LocalEntity:
    entity_type: str
    entity_id: str
    label: str


def read_entity_table(
    path: Path,
    entity_type: str,
    id_column: str,
    label_column: str,
) -> list[LocalEntity]:
    try:
        source = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise SuggestionError(f"Cannot open {path}: {exc}") from exc

    with source:
        reader = csv.DictReader(source)
        required = {id_column, label_column}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SuggestionError(
                f"{path} is missing columns: {', '.join(sorted(missing))}"
            )
        entities = [
            LocalEntity(
                entity_type=entity_type,
                entity_id=row[id_column].strip(),
                label=row[label_column].strip(),
            )
            for row in reader
        ]

    if any(not entity.entity_id or not entity.label for entity in entities):
        raise SuggestionError(f"{path} contains an empty entity ID or label")
    return entities


def load_entities(input_dir: Path) -> list[LocalEntity]:
    entities = []
    entities.extend(
        read_entity_table(
            input_dir / "competitions.csv",
            "competition",
            "competition_id",
            "name",
        )
    )
    entities.extend(
        read_entity_table(
            input_dir / "seasons.csv",
            "season",
            "season_id",
            "label",
        )
    )
    entities.extend(
        read_entity_table(input_dir / "teams.csv", "team", "team_id", "name")
    )
    return sorted(entities, key=lambda entity: (entity.entity_type, entity.entity_id))


def search_wikidata(label: str, limit: int, timeout: float) -> list[dict[str, str]]:
    parameters = urlencode(
        {
            "action": "wbsearchentities",
            "search": label,
            "language": "en",
            "uselang": "en",
            "type": "item",
            "limit": limit,
            "format": "json",
        }
    )
    request = Request(f"{WIKIDATA_API}?{parameters}", headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (OSError, URLError, json.JSONDecodeError) as exc:
        raise SuggestionError(f"Wikidata search failed for {label!r}: {exc}") from exc

    results = payload.get("search")
    if not isinstance(results, list):
        raise SuggestionError(f"Unexpected Wikidata response for {label!r}")
    return [candidate for candidate in results if isinstance(candidate, dict)]


def collect_suggestions(
    entities: list[LocalEntity],
    limit: int,
    timeout: float,
    searcher: Callable[[str, int, float], list[dict[str, str]]] = search_wikidata,
) -> list[dict[str, object]]:
    suggestions: list[dict[str, object]] = []
    for entity in entities:
        candidates = searcher(entity.label, limit, timeout)
        for rank, candidate in enumerate(candidates, start=1):
            candidate_id = str(candidate.get("id", ""))
            if not candidate_id.startswith("Q") or not candidate_id[1:].isdigit():
                continue
            suggestions.append(
                {
                    "entity_type": entity.entity_type,
                    "entity_id": entity.entity_id,
                    "local_label": entity.label,
                    "rank": rank,
                    "wikidata_uri": f"http://www.wikidata.org/entity/{candidate_id}",
                    "candidate_label": str(candidate.get("label", "")),
                    "candidate_description": str(candidate.get("description", "")),
                    "verification_status": "unverified",
                    "notes": "",
                }
            )
    return suggestions


def write_suggestions(
    output_path: Path,
    rows: list[dict[str, object]],
    force: bool,
) -> None:
    if output_path.resolve() == VERIFIED_LINKS.resolve():
        raise SuggestionError(
            "Refusing to overwrite the manually verified entity-links.csv file"
        )
    if output_path.exists() and not force:
        raise SuggestionError(
            f"Output already exists: {output_path}; use --force to replace suggestions"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Search Wikidata for candidate mappings. Results remain unverified and "
            "never replace data/links/entity-links.csv."
        )
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, choices=range(1, 11), default=3)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing suggestions file, never the verified mapping file.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        entities = load_entities(args.input_dir)
        suggestions = collect_suggestions(
            entities,
            limit=args.limit,
            timeout=args.timeout,
        )
        write_suggestions(args.output, suggestions, args.force)
    except SuggestionError as exc:
        raise SystemExit(f"Link suggestion failed: {exc}") from exc

    print(f"Wrote {len(suggestions)} unverified candidates to {args.output.resolve()}")
    print("Manually verify identity before copying any URI to entity-links.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
