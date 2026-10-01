#!/usr/bin/env python3
"""Run a SPARQL query from the terminal and print the result as a table.

  python src/query.py queries/01_standings.rq          # against Fuseki
  python src/query.py "SELECT * WHERE {?s ?p ?o} LIMIT 5"
  python src/query.py queries/01_standings.rq --local  # no server: rdflib in-process
"""

from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENDPOINT = "http://localhost:3030/football/sparql"
LOCAL_FILES = ("ontology/football.ttl", "data/rdf/football.ttl", "data/rdf/links.ttl")


def run_remote(query: str, endpoint: str) -> tuple[list[str], list[list[str]]]:
    request = urllib.request.Request(
        endpoint,
        data=urllib.parse.urlencode({"query": query}).encode(),
        headers={"Accept": "application/sparql-results+json"},
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        result = json.load(response)
    columns = result["head"]["vars"]
    rows = [[row.get(c, {}).get("value", "") for c in columns] for row in result["results"]["bindings"]]
    return columns, rows


def run_local(query: str) -> tuple[list[str], list[list[str]]]:
    from rdflib import Graph  # only needed in local mode

    graph = Graph()
    for name in LOCAL_FILES:
        graph.parse(PROJECT_ROOT / name)
    result = graph.query(query)
    columns = [str(v) for v in result.vars]
    return columns, [["" if v is None else str(v) for v in row] for row in result]


def shorten(value: str) -> str:
    for prefix in (
        "http://example.org/football/resource/",
        "http://example.org/football/ontology#",
        "http://www.wikidata.org/entity/",
    ):
        if value.startswith(prefix):
            return value[len(prefix):]
    return value


def print_table(columns: list[str], rows: list[list[str]]) -> None:
    cells = [[shorten(v) for v in row] for row in rows]
    widths = [max([len(c)] + [len(r[i]) for r in cells]) for i, c in enumerate(columns)]
    line = "+".join("-" * (w + 2) for w in widths)
    print(" | ".join(c.ljust(w) for c, w in zip(columns, widths)))
    print(line)
    for row in cells:
        print(" | ".join(v.ljust(w) for v, w in zip(row, widths)))
    print(f"({len(rows)} rows)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("query", help="path to a .rq file, or the query text itself")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--local", action="store_true", help="query the Turtle files with rdflib")
    args = parser.parse_args()

    path = Path(args.query)
    query = path.read_text(encoding="utf-8") if path.suffix == ".rq" and path.is_file() else args.query
    columns, rows = run_local(query) if args.local else run_remote(query, args.endpoint)
    print_table(columns, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
