#!/usr/bin/env python3
"""Validate the generated football dataset with SHACL."""

from __future__ import annotations

import argparse
from pathlib import Path

from rdflib import Graph


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = PROJECT_ROOT / "data/rdf/football-data.ttl"
DEFAULT_ONTOLOGY = PROJECT_ROOT / "ontology/football.ttl"
DEFAULT_SHAPES = PROJECT_ROOT / "shapes/football-shapes.ttl"
DEFAULT_REPORT = PROJECT_ROOT / "data/rdf/validation-report.ttl"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate football RDF using SHACL.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--ontology", type=Path, default=DEFAULT_ONTOLOGY)
    parser.add_argument("--shapes", type=Path, default=DEFAULT_SHAPES)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser


def main() -> int:
    try:
        from pyshacl import validate
    except ImportError as exc:
        raise SystemExit(
            "pyshacl is required. Install dependencies with "
            "'python -m pip install -r requirements.txt'."
        ) from exc

    args = build_parser().parse_args()
    data_graph = Graph().parse(args.data, format="turtle")
    ontology_graph = Graph().parse(args.ontology, format="turtle")
    shapes_graph = Graph().parse(args.shapes, format="turtle")

    conforms, report_graph, report_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        ont_graph=ontology_graph,
        inference="rdfs",
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
    )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    report_graph.serialize(destination=args.report, format="turtle")
    print(report_text.strip())
    print(f"Validation report: {args.report.resolve()}")
    return 0 if conforms else 1


if __name__ == "__main__":
    raise SystemExit(main())
