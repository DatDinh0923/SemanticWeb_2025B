"""Shared paths and the single configurable RDF namespace."""
import csv
import json
from pathlib import Path

from rdflib import Graph, Namespace

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config/project.json").read_text(encoding="utf-8"))
BASE = CONFIG["base_uri"]
if not BASE.startswith(("http://", "https://")) or not BASE.endswith("/"):
    raise ValueError("base_uri must be an HTTP(S) URI ending in /")
FB = Namespace(BASE + "ontology#")
RES = Namespace(BASE + "resource/")
RDF_DIR = ROOT / "data/rdf"


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def template(path):
    return Path(path).read_text(encoding="utf-8").replace("http://example.org/phongph5/", BASE)


def ontology():
    return Graph().parse(data=template(ROOT / "ontology/football.ttl"), format="turtle")


def write_graph(graph, path):
    """Sorted N-Triples is a deterministic subset of Turtle (no blank nodes here)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(sorted(graph.serialize(format="nt").splitlines())) + "\n", encoding="utf-8")


def load_graph():
    graph = ontology()
    for filename in ("football.ttl", "links.ttl"):
        graph.parse(RDF_DIR / filename, format="turtle")
    return graph
