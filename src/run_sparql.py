#!/usr/bin/env python3
"""Run SPARQL queries from the terminal, locally or against a SPARQL endpoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from rdflib import Graph


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = PROJECT_ROOT / "data/rdf/football-data.ttl"
DEFAULT_ONTOLOGY = PROJECT_ROOT / "ontology/football.ttl"
DEFAULT_QUERY_DIR = PROJECT_ROOT / "queries"
DEFAULT_ENDPOINT = "http://localhost:3030/football/sparql"


def query_files(query_dir: Path) -> list[Path]:
    """Return the offline query suite; federated queries live in a subfolder."""
    return sorted(query_dir.glob("*.rq"))


def load_graph(data_path: Path, ontology_path: Path | None) -> Graph:
    """Load the data with the ontology, matching what the Fuseki endpoint serves."""
    graph = Graph().parse(data_path, format="turtle")
    if ontology_path is not None:
        graph.parse(ontology_path, format="turtle")
    return graph


def printable(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).replace("\t", " ").replace("\n", " ")


def print_results(
    title: str, variables: Iterable[object], rows: list[Iterable[object]]
) -> None:
    print(f"\n=== {title} ===")
    print("\t".join(str(variable) for variable in variables))
    for row in rows:
        print("\t".join(printable(value) for value in row))
    print(f"Rows: {len(rows)}")


def run_local_query(graph: Graph, query_text: str) -> tuple[list[str], list[list[object]]]:
    result = graph.query(query_text)
    variables = [str(variable) for variable in (result.vars or [])]
    return variables, [list(row) for row in result]


def run_endpoint_query(
    endpoint: str, query_text: str, timeout: int = 120
) -> tuple[list[str], list[list[object]]]:
    request = Request(
        endpoint,
        data=urlencode({"query": query_text}).encode("utf-8"),
        method="POST",
        headers={
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        document = json.load(response)
    variables = document["head"].get("vars", [])
    rows = [
        [binding.get(variable, {}).get("value") for variable in variables]
        for binding in document["results"]["bindings"]
    ]
    return variables, rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run saved SPARQL queries.")
    parser.add_argument("query", nargs="?", type=Path, help="Path to one .rq file.")
    parser.add_argument("--all", action="store_true", help="Run every query in queries/.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--ontology", type=Path, default=DEFAULT_ONTOLOGY)
    parser.add_argument(
        "--no-ontology",
        action="store_true",
        help="Query the instance data without the ontology.",
    )
    parser.add_argument("--query-dir", type=Path, default=DEFAULT_QUERY_DIR)
    parser.add_argument(
        "--endpoint",
        nargs="?",
        const=DEFAULT_ENDPOINT,
        help=f"Send queries to a SPARQL endpoint instead (default: {DEFAULT_ENDPOINT}).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.all == (args.query is not None):
        raise SystemExit("Choose either one query path or --all.")

    selected_queries = query_files(args.query_dir) if args.all else [args.query]
    if not selected_queries:
        raise SystemExit(f"No SPARQL queries found in {args.query_dir}")
    for query_path in selected_queries:
        if query_path is None or not query_path.is_file():
            raise SystemExit(f"Query file not found: {query_path}")

    graph = None
    if args.endpoint is None:
        graph = load_graph(args.data, None if args.no_ontology else args.ontology)

    for query_path in selected_queries:
        query_text = query_path.read_text(encoding="utf-8")
        try:
            if graph is not None:
                variables, rows = run_local_query(graph, query_text)
            else:
                variables, rows = run_endpoint_query(args.endpoint, query_text)
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            raise SystemExit(f"{query_path.name} failed: {exc}") from exc
        print_results(query_path.name, variables, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
