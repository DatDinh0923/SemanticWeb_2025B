#!/usr/bin/env python3
"""Run the project's saved SPARQL queries against the generated RDF data."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from rdflib import Graph


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = PROJECT_ROOT / "data/rdf/football-data.ttl"
DEFAULT_QUERY_DIR = PROJECT_ROOT / "queries"


def query_files(query_dir: Path) -> list[Path]:
    return sorted(query_dir.glob("*.rq"))


def printable(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).replace("\t", " ").replace("\n", " ")


def print_results(query_path: Path, variables: Iterable[object], rows: list[object]) -> None:
    print(f"\n=== {query_path.name} ===")
    print("\t".join(str(variable) for variable in variables))
    for row in rows:
        print("\t".join(printable(value) for value in row))
    print(f"Rows: {len(rows)}")


def run_query(graph: Graph, query_path: Path) -> int:
    result = graph.query(query_path.read_text(encoding="utf-8"))
    rows = list(result)
    print_results(query_path, result.vars or [], rows)
    return len(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run saved SPARQL queries locally.")
    parser.add_argument("query", nargs="?", type=Path, help="Path to one .rq file.")
    parser.add_argument("--all", action="store_true", help="Run every query in queries/.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--query-dir", type=Path, default=DEFAULT_QUERY_DIR)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.all == (args.query is not None):
        raise SystemExit("Choose either one query path or --all.")

    graph = Graph().parse(args.data, format="turtle")
    selected_queries = query_files(args.query_dir) if args.all else [args.query]
    if not selected_queries:
        raise SystemExit(f"No SPARQL queries found in {args.query_dir}")

    for query_path in selected_queries:
        if query_path is None or not query_path.is_file():
            raise SystemExit(f"Query file not found: {query_path}")
        run_query(graph, query_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
