#!/usr/bin/env python3
"""Print every number the project report cites, computed from the repository.

Numbers in the report are copied by hand, so they drift when the data, the
ontology or the site changes. Run this after any change and compare its output
with the report instead of trusting old figures.

    python3 src/report_numbers.py               # fast: about 10 s
    python3 src/report_numbers.py --reasoning   # adds the OWL 2 RL figures (~45 s)

The ontology metrics (axiom counts, expressivity, profile) come from ROBOT, an
external Java tool; the command is printed at the end.
"""

from __future__ import annotations

import argparse
import csv
import re
import unittest
from collections import Counter
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF

from convert_to_rdf import BASE_URL, FOOT
from run_sparql import DEFAULT_DATA, DEFAULT_ONTOLOGY, DEFAULT_QUERY_DIR, query_files


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SHAPES = PROJECT_ROOT / "shapes/football-shapes.ttl"
ALIASES = PROJECT_ROOT / "config/team-aliases.csv"
SH_SPARQL = URIRef("http://www.w3.org/ns/shacl#sparql")


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def row(label: str, value: object, where: str = "") -> None:
    shown = f"{value:,}" if isinstance(value, int) else str(value)
    print(f"{label:52} {shown:>12}   {where}")


def query(graph: Graph, name: str) -> list:
    return list(graph.query((DEFAULT_QUERY_DIR / name).read_text(encoding="utf-8")))


def site_pages(graph: Graph) -> Counter:
    """Pages build_site.py writes: one per local subject, grouped by URI area."""
    areas = Counter()
    for subject in {s for s in graph.subjects() if isinstance(s, URIRef)}:
        if not str(subject).startswith(BASE_URL):
            continue
        path = str(subject)[len(BASE_URL):]
        area = path.split("/", 2)[1] if path.startswith("resource/") else path.split("/", 1)[0]
        areas[area or "home"] += 1
    return areas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--reasoning", action="store_true", help="Also run the OWL 2 RL closure.")
    args = parser.parse_args()

    data = Graph().parse(DEFAULT_DATA, format="turtle")
    ontology = Graph().parse(DEFAULT_ONTOLOGY, format="turtle")
    graph = data + ontology

    section("Triples (abstract, ch6, ch10)")
    row("Instance-data triples", len(data), "abstract, ch6, ch10")
    row("Ontology triples", len(ontology))
    row("Data + ontology triples", len(graph), "ch6")

    section("Entities (abstract, ch5, ch6, ch10)")
    for label, cls in (
        ("Competitions", FOOT.Competition),
        ("Seasons", FOOT.Season),
        ("Clubs", FOOT.FootballTeam),
        ("Matches", FOOT.FootballMatch),
        ("Drawn matches", FOOT.Draw),
    ):
        row(label, len(set(data.subjects(RDF.type, cls))))
    with ALIASES.open(encoding="utf-8", newline="") as source:
        aliases = list(csv.DictReader(source))
    row("Club spellings in the alias table", len(aliases), "ch5")
    row("Reviewed club IDs", len({a["team_id"] for a in aliases}), "ch5")

    section("Links (abstract, ch7, ch10)")
    links = list(data.subject_objects(OWL.sameAs))
    row("owl:sameAs links", len(links), "abstract, ch7, ch10")
    row("Linked entities", len({s for s, _ in links}), "ch7, ch10")

    section("Site pages (ch9, ch10)")
    pages = site_pages(graph)
    entity = sum(pages[a] for a in ("competition", "season", "team", "match"))
    row("Entity pages (competition, seasons, clubs, matches)", entity, "ch9")
    row("Ontology pages (ontology + its terms)", pages["ontology"], "ch9")
    row("Dataset description pages", pages["dataset"], "ch9")
    row("All pages written by build_site.py", sum(pages.values()), "ch9, ch10")

    section("Ontology terms (ch3, ch10)")
    own = {s for s in ontology.subjects() if isinstance(s, URIRef) and str(s).startswith(str(FOOT)) and s != URIRef(str(FOOT))}
    for label, kind in (("classes", OWL.Class), ("object properties", OWL.ObjectProperty), ("datatype properties", OWL.DatatypeProperty)):
        row(f"Own {label}", len({s for s in own if (s, RDF.type, kind) in ontology}), "ch10")
    used = set()
    for path in [*query_files(DEFAULT_QUERY_DIR), *sorted((DEFAULT_QUERY_DIR / "federated").glob("*.rq"))]:
        code = "\n".join(line.split("#", 1)[0] for line in path.read_text(encoding="utf-8").splitlines())
        used |= {FOOT[name] for name in re.findall(r"foot:(\w+)", code)}
    used &= own
    row("Own terms used by at least one CQ query", f"{len(used)} of {len(own)}", "ch3, ch10")
    row("Saved offline queries (+ federated)", f"{len(query_files(DEFAULT_QUERY_DIR))} + 1", "ch9")

    section("Validation (abstract, ch8)")
    shapes = Graph().parse(SHAPES, format="turtle")
    row("SHACL-SPARQL constraints", len(list(shapes.objects(None, SH_SPARQL))), "ch8")
    tests = unittest.defaultTestLoader.discover(str(PROJECT_ROOT / "src"), pattern="test_*.py")
    row("Unit tests", tests.countTestCases(), "abstract, ch8, ch9 figure")

    section("Query results (ch9)")
    for r in query(graph, "14-season-champions.rq"):
        row(f"CQ14 {r.seasonLabel} {r.championName}", f"{r.points} pts, GD {r.goalDifference}", "Table champions")
    for r in query(graph, "13-season-statistics.rq"):
        row(f"CQ13 {r.seasonLabel} goals/home/draw/away", f"{float(r.goalsPerMatch):.2f} {r.homeWinPercent} {r.drawPercent} {r.awayWinPercent}", "Table stats")
    for r in query(graph, "03-highest-scoring-matches.rq"):
        row(f"CQ3 {r.label}", f"{r.totalGoals} goals", "ch9")
    for r in query(graph, "16-ontology-reasoning.rq"):
        row(f"CQ16 {str(r.term).rsplit('/', 1)[-1]}", int(r.resources), "ch9")

    if args.reasoning:
        from check_reasoning import MEASURES, count, load, reason, remove_match_competitions

        section("Reasoning (ch4 table, docs/ontology.md)")
        asserted = load(DEFAULT_DATA, DEFAULT_ONTOLOGY)
        removed = remove_match_competitions(asserted)
        inferred = Graph()
        for triple in asserted:
            inferred.add(triple)
        errors = reason(inferred)
        row("Asserted match competitions removed", removed, "ch4")
        row("Triples before the closure", len(asserted), "ch4")
        row("Triples after the closure", len(inferred), "ch4")
        row("Inconsistencies in the published graph", len(errors), "ch4")
        for label, text in MEASURES:
            row(label, f"{count(asserted, text)} -> {count(inferred, text):,}", "ch4 table")

    print(
        "\nOntology metrics (ch4 table): java -jar robot.jar measure "
        "--input ontology/football.ttl --metrics extended --format tsv --output metrics.tsv"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
