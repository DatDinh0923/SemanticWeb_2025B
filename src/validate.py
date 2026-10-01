#!/usr/bin/env python3
"""Validate the generated RDF against the SHACL shapes; exit 1 if it does not conform."""

from __future__ import annotations

from pathlib import Path

from pyshacl import validate
from rdflib import Graph

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# the ontology is included so sh:class sees League/Cup as subclasses of Competition
DATA_FILES = ("ontology/football.ttl", "data/rdf/football.ttl", "data/rdf/links.ttl")
SHAPES = PROJECT_ROOT / "shapes/football-shapes.ttl"


def check(data: Graph) -> tuple[bool, str]:
    conforms, _, report = validate(data, shacl_graph=Graph().parse(SHAPES))
    return conforms, report


def main() -> int:
    data = Graph()
    for name in DATA_FILES:
        data.parse(PROJECT_ROOT / name)
    conforms, report = check(data)
    print(report)
    return 0 if conforms else 1


if __name__ == "__main__":
    raise SystemExit(main())
