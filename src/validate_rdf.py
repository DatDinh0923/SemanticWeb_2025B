"""Validate the generated RDF against the project's SHACL constraints."""
from rdflib import Graph
from pyshacl import validate

from common import ROOT, RDF_DIR, load_graph, template


def validate_graph(graph):
    shapes = Graph().parse(data=template(ROOT / "shapes/football-shapes.ttl"), format="turtle")
    return validate(graph, shacl_graph=shapes, inference="none", advanced=True)


def main():
    conforms, report, message = validate_graph(load_graph())
    report.serialize(destination=RDF_DIR / "validation-report.ttl", format="turtle")
    if not conforms:
        raise ValueError(message)
    print("SHACL conforms: true", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        raise SystemExit(f"Validation failed: {exc}") from exc
