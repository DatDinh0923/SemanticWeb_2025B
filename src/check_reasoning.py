#!/usr/bin/env python3
"""Check what an OWL 2 RL reasoner adds to the football graph, and what it catches.

The published data asserts every fact that the queries need, so SPARQL works
without a reasoner. This script shows what the ontology contributes on its own:

1. Entailment: the asserted match competitions are removed, the OWL 2 RL
   closure is computed with owlrl, and the same plain SPARQL counts are
   compared before and after reasoning.
2. Inconsistency: deliberate errors are added to one real match and the
   reasoner must report each of them, except a second home team, which OWL's
   open-world semantics cannot reject (SHACL does).
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF

try:
    import owlrl
    from owlrl.Namespaces import ERRNS
except ImportError as exc:  # pragma: no cover - dependency message
    raise SystemExit(
        "owlrl is required. Install dependencies with "
        "'python -m pip install -r requirements.txt'."
    ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = PROJECT_ROOT / "data/rdf/football-data.ttl"
DEFAULT_ONTOLOGY = PROJECT_ROOT / "ontology/football.ttl"
CQ16_QUERY = PROJECT_ROOT / "queries/16-ontology-reasoning.rq"

FOOT = Namespace("https://datdinh0923.github.io/SemanticWeb_2025B/ontology/")
TEAM = Namespace("https://datdinh0923.github.io/SemanticWeb_2025B/resource/team/")
MATCH = Namespace("https://datdinh0923.github.io/SemanticWeb_2025B/resource/match/")

PREFIXES = """
PREFIX foot: <https://datdinh0923.github.io/SemanticWeb_2025B/ontology/>
PREFIX schema: <https://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
"""
LOCAL = 'STRSTARTS(STR(?x), "https://datdinh0923.github.io/SemanticWeb_2025B/resource/")'
WIKIDATA = 'STRSTARTS(STR(?x), "http://www.wikidata.org/entity/")'
DBPEDIA = 'STRSTARTS(STR(?y), "http://dbpedia.org/resource/")'

# Plain SPARQL (no property paths): each count only changes if a reasoner
# materializes the triples it looks for. The first group counts our own
# resources; the second shows what owl:sameAs adds about the linked URIs.
MEASURES = [
    (
        "Matches with a competition (property chain)",
        "SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x a foot:FootballMatch ; foot:partOfCompetition ?c }",
    ),
    (
        "Local resources typed schema:SportsEvent",
        f"SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE {{ ?x a schema:SportsEvent FILTER({LOCAL}) }}",
    ),
    (
        "Local resources typed schema:SportsTeam",
        f"SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE {{ ?x a schema:SportsTeam FILTER({LOCAL}) }}",
    ),
    (
        "Local resources typed schema:EventSeries",
        f"SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE {{ ?x a schema:EventSeries FILTER({LOCAL}) }}",
    ),
    (
        "Matches with a schema:competitor",
        "SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x schema:competitor ?t }",
    ),
    (
        "Matches dcterms:isPartOf a season",
        "SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x a foot:FootballMatch ; dcterms:isPartOf ?s . ?s a foot:Season }",
    ),
    (
        "Wikidata URIs typed foot:FootballTeam (owl:sameAs)",
        f"SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE {{ ?x a foot:FootballTeam FILTER({WIKIDATA}) }}",
    ),
    (
        "Matches whose home team is a Wikidata URI (owl:sameAs)",
        f"SELECT (COUNT(DISTINCT ?m) AS ?n) WHERE {{ ?m foot:homeTeam ?x FILTER({WIKIDATA}) }}",
    ),
    (
        "Wikidata owl:sameAs DBpedia pairs (owl:sameAs)",
        f"SELECT (COUNT(*) AS ?n) WHERE {{ ?x owl:sameAs ?y FILTER({WIKIDATA} && {DBPEDIA}) }}",
    ),
]

# A real drawn match and a real decisive match from the 2018/19 season.
DRAWN_MATCH = MATCH["2018-08-11-wolverhampton-wanderers-everton"]
DECISIVE_MATCH = MATCH["2018-08-10-manchester-united-leicester-city"]


@dataclass(frozen=True)
class Injection:
    name: str
    match: URIRef
    remove: list[tuple]
    add: list[tuple]
    expect_inconsistent: bool


INJECTIONS = [
    Injection(
        "Drawn match given a winner",
        DRAWN_MATCH,
        remove=[],
        add=[(DRAWN_MATCH, FOOT.winner, TEAM["everton"])],
        expect_inconsistent=True,
    ),
    Injection(
        "Team plays itself (away team = home team)",
        DECISIVE_MATCH,
        remove=[(DECISIVE_MATCH, FOOT.awayTeam, None)],
        add=[(DECISIVE_MATCH, FOOT.awayTeam, TEAM["manchester-united"])],
        expect_inconsistent=True,
    ),
    Injection(
        "Same team is winner and loser",
        DECISIVE_MATCH,
        remove=[(DECISIVE_MATCH, FOOT.loser, None)],
        add=[(DECISIVE_MATCH, FOOT.loser, TEAM["manchester-united"])],
        expect_inconsistent=True,
    ),
    Injection(
        "Match also typed as a team (disjoint classes)",
        DECISIVE_MATCH,
        remove=[],
        add=[(DECISIVE_MATCH, RDF.type, FOOT.FootballTeam)],
        expect_inconsistent=True,
    ),
    # Open world, no unique-name assumption: a second value of a functional
    # property makes the reasoner infer that the two clubs are the same.
    Injection(
        "Match given a second home team",
        DECISIVE_MATCH,
        remove=[],
        add=[(DECISIVE_MATCH, FOOT.homeTeam, TEAM["arsenal"])],
        expect_inconsistent=False,
    ),
]


def load(data_path: Path, ontology_path: Path) -> Graph:
    graph = Graph().parse(data_path, format="turtle")
    graph.parse(ontology_path, format="turtle")
    return graph


def remove_match_competitions(graph: Graph) -> int:
    """Drop the asserted competition of every match, which the chain should re-infer."""
    asserted = [
        (match, FOOT.partOfCompetition, competition)
        for match in graph.subjects(RDF.type, FOOT.FootballMatch)
        for competition in graph.objects(match, FOOT.partOfCompetition)
    ]
    for triple in asserted:
        graph.remove(triple)
    return len(asserted)


def reason(graph: Graph) -> list[str]:
    """Expand the graph in place with the OWL 2 RL closure; return inconsistencies."""
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(graph)
    errors = sorted(str(message) for message in graph.objects(None, ERRNS.error))
    for node in list(graph.subjects(RDF.type, ERRNS.ErrorMessage)):
        graph.remove((node, None, None))
    return errors


def short(message: str) -> str:
    """Write the project's URIs as prefixed names in reasoner messages."""
    for prefix, namespace in (("foot:", FOOT), ("team:", TEAM), ("match:", MATCH)):
        message = message.replace(str(namespace), prefix)
    return message


def count(graph: Graph, query: str) -> int:
    return int(next(iter(graph.query(PREFIXES + query)))[0])


def cq16_counts(graph: Graph) -> dict[str, int]:
    rows = graph.query(CQ16_QUERY.read_text(encoding="utf-8"))
    return {str(row.term).rsplit("/", 1)[-1]: int(row.resources) for row in rows}


def match_subgraph(data: Graph, ontology_path: Path, match: URIRef) -> Graph:
    """The ontology plus one match and the types of the resources it references."""
    if (match, RDF.type, FOOT.FootballMatch) not in data:
        raise SystemExit(f"Match not found in the data: {match}")
    graph = Graph().parse(ontology_path, format="turtle")
    for _, predicate, value in data.triples((match, None, None)):
        graph.add((match, predicate, value))
        for value_type in data.objects(value, RDF.type):
            graph.add((value, RDF.type, value_type))
    return graph


def run_injection(
    data: Graph, ontology_path: Path, injection: Injection
) -> tuple[list[str], Graph]:
    """Apply one deliberate error, reason, and return the errors and the closure."""
    graph = match_subgraph(data, ontology_path, injection.match)
    for pattern in injection.remove:
        graph.remove(pattern)
    for triple in injection.add:
        graph.add(triple)
    return reason(graph), graph


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare query results with and without OWL 2 RL reasoning."
    )
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--ontology", type=Path, default=DEFAULT_ONTOLOGY)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    failures: list[str] = []

    print("=== Entailment: plain SPARQL counts without and with OWL 2 RL ===")
    asserted = load(args.data, args.ontology)
    path_counts = cq16_counts(asserted)
    removed = remove_match_competitions(asserted)
    inferred = Graph()
    for triple in asserted:
        inferred.add(triple)
    print(f"Removed {removed} asserted match competitions before reasoning.")

    started = time.perf_counter()
    errors = reason(inferred)
    elapsed = time.perf_counter() - started
    print(
        f"Triples: {len(asserted):,} asserted -> {len(inferred):,} after the "
        f"closure ({elapsed:.0f} s)."
    )
    if errors:
        failures.append("the published graph is inconsistent")
        print("Inconsistencies:", *map(short, errors), sep="\n  ")
    else:
        print("Consistent: the reasoner reports no violation.")

    print(f"\n{'Measure':58} {'without':>8} {'with':>8}")
    results = {}
    for label, query in MEASURES:
        results[label] = (count(asserted, query), count(inferred, query))
        print(f"{label:58} {results[label][0]:>8,} {results[label][1]:>8,}")

    matches = results["Matches with a competition (property chain)"][1]
    if matches != removed:
        failures.append(f"the property chain re-inferred {matches} of {removed} competitions")

    # CQ16 emulates RDFS entailment with property paths; it must agree.
    materialized = {
        "SportsEvent": results["Local resources typed schema:SportsEvent"][1],
        "SportsTeam": results["Local resources typed schema:SportsTeam"][1],
        "EventSeries": results["Local resources typed schema:EventSeries"][1],
        "competitor": results["Matches with a schema:competitor"][1],
    }
    for term, value in materialized.items():
        if path_counts.get(term) != value:
            failures.append(f"CQ16 counts {path_counts.get(term)} {term}, reasoner {value}")
    print("\nCQ16 (property paths, no reasoner) agrees with the materialized counts:"
          f" {all(path_counts.get(t) == v for t, v in materialized.items())}")

    print("\n=== Inconsistency: deliberate errors added to one real match ===")
    data = Graph().parse(args.data, format="turtle")
    for injection in INJECTIONS:
        found, closure = run_injection(data, args.ontology, injection)
        verdict = "inconsistent" if found else "consistent"
        expected = "inconsistent" if injection.expect_inconsistent else "consistent"
        mark = "ok" if verdict == expected else "UNEXPECTED"
        print(f"[{mark}] {injection.name}: {verdict}")
        for message in found:
            print(f"       {short(message)}")
        if verdict != expected:
            failures.append(f"{injection.name}: expected {expected}, got {verdict}")

    # The last injection (a second home team) is consistent; show why.
    if (TEAM["manchester-united"], OWL.sameAs, TEAM["arsenal"]) in closure:
        print("       The reasoner instead infers team:manchester-united owl:sameAs "
              "team:arsenal; SHACL's sh:maxCount 1 rejects this data.")
    else:
        failures.append("a second home team did not produce an owl:sameAs inference")

    if failures:
        print("\nFAILED:", *failures, sep="\n  ")
        return 1
    print("\nAll reasoning checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
