#!/usr/bin/env python3
"""Find the Wikidata item and DBpedia resource of every team.

Uses the Wikidata Action API (wbsearchentities + wbgetentities), which is far
less rate-limited than the public SPARQL endpoint. Results are written to
data/links/team_links.csv; rows that already have a Wikidata ID are kept, so the
script can be re-run to resume, and wrong matches can be corrected by hand.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEAMS = PROJECT_ROOT / "data/processed/teams.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/links/team_links.csv"

API_URL = "https://www.wikidata.org/w/api.php"
USER_AGENT = "HUST-SemanticWeb-football-linker/1.0 (student project)"
FIELDS = ("team_id", "name", "wikidata", "wikidata_label", "dbpedia")

# Wikidata classes accepted as "this item is a football club".
CLUB_CLASSES = {
    "Q476028",  # association football club
    "Q103229495",  # men's association football team
    "Q847017",  # sports club
}


def call_api(params: dict[str, str], retries: int = 6) -> dict:
    """GET the Action API, backing off on rate limits and transient errors."""
    query = urllib.parse.urlencode({**params, "format": "json", "maxlag": "5"})
    request = urllib.request.Request(f"{API_URL}?{query}", headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.load(response)
            if payload.get("error", {}).get("code") != "maxlag":
                return payload
            wait = 5
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504):
                raise
            wait = int(exc.headers.get("Retry-After") or 2 ** (attempt + 2))
        except urllib.error.URLError:
            wait = 2 ** (attempt + 2)
        print(f"  rate limited / unavailable, retrying in {wait}s")
        time.sleep(wait)
    raise RuntimeError(f"Wikidata API failed after {retries} attempts: {params}")


def search_queries(name: str) -> list[str]:
    """'Arsenal FC' -> ['Arsenal FC', 'Arsenal F.C.']; Wikipedia titles use 'F.C.'."""
    queries = [name]
    dotted = name.replace("AFC", "A.F.C.").replace("FC", "F.C.")
    if dotted != name:
        queries.append(dotted)
    return queries


def find_club(name: str) -> dict[str, str] | None:
    for query in search_queries(name):
        hits = call_api(
            {"action": "wbsearchentities", "search": query, "language": "en", "type": "item", "limit": "7"}
        ).get("search", [])
        if not hits:
            continue
        ids = [hit["id"] for hit in hits]
        entities = call_api(
            {
                "action": "wbgetentities",
                "ids": "|".join(ids),
                "props": "claims|sitelinks|labels",
                "sitefilter": "enwiki",
                "languages": "en",
            }
        )["entities"]
        for item_id in ids:  # keep search ranking
            entity = entities.get(item_id, {})
            classes = {
                claim["mainsnak"].get("datavalue", {}).get("value", {}).get("id")
                for claim in entity.get("claims", {}).get("P31", [])
            }
            if classes & CLUB_CLASSES:
                title = entity.get("sitelinks", {}).get("enwiki", {}).get("title", "")
                return {
                    "wikidata": item_id,
                    "wikidata_label": entity.get("labels", {}).get("en", {}).get("value", ""),
                    "dbpedia": title.replace(" ", "_"),
                }
    return None


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def write_links(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--teams", type=Path, default=DEFAULT_TEAMS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between teams")
    args = parser.parse_args()

    existing = {row["team_id"]: row for row in read_csv(args.output) if row.get("wikidata")}
    rows = []
    for team in read_csv(args.teams):
        if team["team_id"] in existing:
            rows.append(existing[team["team_id"]])
            continue
        match = find_club(team["name"])
        row = {"team_id": team["team_id"], "name": team["name"], **(match or {})}
        rows.append({field: row.get(field, "") for field in FIELDS})
        print(f"{team['name']:35} -> {row.get('wikidata') or 'NOT FOUND'} {row.get('wikidata_label', '')}")
        write_links(args.output, rows)  # save progress after every team
        time.sleep(args.delay)

    write_links(args.output, rows)
    linked = sum(1 for row in rows if row["wikidata"])
    print(f"Linked {linked}/{len(rows)} teams -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
