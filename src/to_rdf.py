#!/usr/bin/env python3
"""Convert the cleaned CSV tables (and external links) into RDF Turtle."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROCESSED_DIR = PROJECT_ROOT / "data/processed"
DEFAULT_LINKS_DIR = PROJECT_ROOT / "data/links"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data/rdf"

FB = Namespace("http://example.org/football/ontology#")
RES = Namespace("http://example.org/football/resource/")
SCHEMA = Namespace("https://schema.org/")
WD = Namespace("http://www.wikidata.org/entity/")
DBR = Namespace("http://dbpedia.org/resource/")
ENGLAND = WD.Q21


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def new_graph() -> Graph:
    graph = Graph()
    for prefix, namespace in (
        ("fb", FB),
        ("res", RES),
        ("schema", SCHEMA),
        ("wd", WD),
        ("dbr", DBR),
        ("owl", OWL),
    ):
        graph.bind(prefix, namespace)
    return graph


def uri(kind: str, entity_id: str) -> URIRef:
    """e.g. uri("team", "arsenal") -> .../resource/team/arsenal"""
    return RES[f"{kind}/{entity_id}"]


def build_data_graph(processed_dir: Path) -> Graph:
    graph = new_graph()

    for row in read_rows(processed_dir / "competitions.csv"):
        node = uri("competition", row["competition_id"])
        graph.add((node, RDFS.label, Literal(row["name"], lang="en")))
        if row["tier"]:
            graph.add((node, RDF.type, FB.League))
            graph.add((node, FB.tier, Literal(int(row["tier"]), datatype=XSD.positiveInteger)))
        else:
            graph.add((node, RDF.type, FB.Cup))

    for row in read_rows(processed_dir / "seasons.csv"):
        node = uri("season", row["season_id"])
        competition = uri("competition", row["competition_id"])
        graph.add((node, RDF.type, FB.Season))
        graph.add((node, FB.seasonOf, competition))
        graph.add((node, FB.seasonLabel, Literal(row["label"])))
        graph.add((node, FB.startDate, Literal(row["start_date"], datatype=XSD.date)))
        graph.add((node, FB.endDate, Literal(row["end_date"], datatype=XSD.date)))
        competition_name = graph.value(competition, RDFS.label)
        graph.add((node, RDFS.label, Literal(f"{competition_name} {row['label']}", lang="en")))

    for row in read_rows(processed_dir / "teams.csv"):
        node = uri("team", row["team_id"])
        graph.add((node, RDF.type, FB.Team))
        graph.add((node, RDFS.label, Literal(row["name"], lang="en")))

    for row in read_rows(processed_dir / "matches.csv"):
        node = uri("match", row["match_id"])
        home, away = uri("team", row["home_team_id"]), uri("team", row["away_team_id"])
        home_goals, away_goals = int(row["home_goals"]), int(row["away_goals"])

        graph.add((node, RDF.type, FB.Match))
        graph.add((node, FB.inSeason, uri("season", row["season_id"])))
        graph.add((node, FB.homeTeam, home))
        graph.add((node, FB.awayTeam, away))
        graph.add((node, FB.homeGoals, Literal(home_goals, datatype=XSD.nonNegativeInteger)))
        graph.add((node, FB.awayGoals, Literal(away_goals, datatype=XSD.nonNegativeInteger)))
        graph.add((node, FB.matchDate, Literal(row["match_date"], datatype=XSD.date)))
        if row["round"].isdigit():
            graph.add((node, FB.matchday, Literal(int(row["round"]), datatype=XSD.positiveInteger)))
        else:
            graph.add((node, FB.stage, Literal(row["round"])))

        if home_goals == away_goals:
            graph.add((node, RDF.type, FB.Draw))
        else:
            winner, loser = (home, away) if home_goals > away_goals else (away, home)
            graph.add((node, FB.winner, winner))
            graph.add((node, FB.loser, loser))

    return graph


def build_links_graph(processed_dir: Path, links_dir: Path) -> Graph:
    """owl:sameAs links to Wikidata/DBpedia: the step from 4-star to 5-star data."""
    graph = new_graph()

    for row in read_rows(processed_dir / "competitions.csv"):
        graph.add((uri("competition", row["competition_id"]), SCHEMA.location, ENGLAND))

    for kind in ("competition", "team"):
        path = links_dir / f"{kind}_links.csv"
        if not path.is_file():
            print(f"Skipping missing {path}")
            continue
        for row in read_rows(path):
            subject = uri(kind, row[f"{kind}_id"])
            if row.get("wikidata"):
                graph.add((subject, OWL.sameAs, WD[row["wikidata"]]))
            if row.get("dbpedia"):
                graph.add((subject, OWL.sameAs, DBR[row["dbpedia"]]))

    return graph


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--links-dir", type=Path, default=DEFAULT_LINKS_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, graph in (
        ("football.ttl", build_data_graph(args.processed_dir)),
        ("links.ttl", build_links_graph(args.processed_dir, args.links_dir)),
    ):
        output = args.output_dir / name
        graph.serialize(output, format="turtle", encoding="utf-8")
        print(f"Wrote {len(graph)} triples to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
