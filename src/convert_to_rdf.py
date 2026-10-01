#!/usr/bin/env python3
"""Convert normalized football CSV tables into a linked RDF dataset."""

from __future__ import annotations

import argparse
import csv
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from rdflib import DCAT, OWL, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data/processed"
DEFAULT_LINKS = PROJECT_ROOT / "data/links/entity-links.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/rdf/football-data.ttl"

BASE_URL = "https://datdinh0923.github.io/SemanticWeb_2025B/"
FOOT = Namespace(f"{BASE_URL}ontology/")
DATASET = Namespace(f"{BASE_URL}dataset/")
TEAM = Namespace(f"{BASE_URL}resource/team/")
MATCH = Namespace(f"{BASE_URL}resource/match/")
SEASON = Namespace(f"{BASE_URL}resource/season/")
COMPETITION = Namespace(f"{BASE_URL}resource/competition/")
SCHEMA = Namespace("https://schema.org/")
VOID = Namespace("http://rdfs.org/ns/void#")
PROV = Namespace("http://www.w3.org/ns/prov#")

SOURCE_DATA_URL = URIRef(
    "https://github.com/footballcsv/england/blob/master/"
    "2010s/2018-19/eng.1.csv"
)
CC0_LICENSE = URIRef("https://creativecommons.org/publicdomain/zero/1.0/")
REPOSITORY_URL = URIRef("https://github.com/DatDinh0923/SemanticWeb_2025B")
PUBLISHER_URL = URIRef("https://github.com/DatDinh0923")
PUBLIC_DATA_URL = URIRef(f"{BASE_URL}download/football-data.ttl")
PUBLIC_ONTOLOGY_URL = URIRef(f"{BASE_URL}ontology/football.ttl")

WIKIDATA_PATTERN = re.compile(r"^http://www\.wikidata\.org/entity/Q[1-9][0-9]*$")
DBPEDIA_PATTERN = re.compile(r"^http://dbpedia\.org/resource/\S+$")


class ConversionError(ValueError):
    """Raised when normalized data cannot be safely converted to RDF."""


def read_csv(path: Path, required_columns: set[str]) -> list[dict[str, str]]:
    try:
        source = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise ConversionError(f"Cannot open {path}: {exc}") from exc

    with source:
        reader = csv.DictReader(source)
        columns = set(reader.fieldnames or [])
        missing = required_columns - columns
        if missing:
            raise ConversionError(
                f"{path} is missing columns: {', '.join(sorted(missing))}"
            )
        rows = [dict(row) for row in reader]

    if not rows:
        raise ConversionError(f"{path} contains no data rows")
    return rows


def index_rows(
    rows: list[dict[str, str]], id_column: str, entity_name: str
) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        entity_id = row[id_column].strip()
        if not entity_id:
            raise ConversionError(f"{entity_name} has an empty {id_column}")
        if entity_id in indexed:
            raise ConversionError(f"Duplicate {entity_name} ID: {entity_id}")
        indexed[entity_id] = row
    return indexed


def parse_iso_date(value: str, field_name: str) -> Literal:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ConversionError(f"Invalid {field_name}: {value!r}") from exc
    return Literal(parsed.isoformat(), datatype=XSD.date)


def parse_non_negative_integer(value: str, field_name: str) -> Literal:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ConversionError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 0:
        raise ConversionError(f"{field_name} cannot be negative: {value!r}")
    return Literal(parsed, datatype=XSD.nonNegativeInteger)


def parse_positive_integer(value: str, field_name: str) -> Literal:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ConversionError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ConversionError(f"{field_name} must be positive: {value!r}")
    return Literal(parsed, datatype=XSD.positiveInteger)


def external_uri(value: str, field_name: str) -> URIRef:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ConversionError(f"Invalid {field_name}: {value!r}")
    return URIRef(value)


def bind_namespaces(graph: Graph) -> None:
    graph.bind("foot", FOOT)
    graph.bind("dataset", DATASET)
    graph.bind("team", TEAM)
    graph.bind("match", MATCH)
    graph.bind("season", SEASON)
    graph.bind("competition", COMPETITION)
    graph.bind("schema", SCHEMA)
    graph.bind("dcat", DCAT)
    graph.bind("dcterms", DCTERMS)
    graph.bind("owl", OWL)
    graph.bind("prov", PROV)
    graph.bind("void", VOID)
    graph.bind("xsd", XSD)


def add_external_links(
    graph: Graph,
    link_rows: list[dict[str, str]],
    local_resources: dict[tuple[str, str], URIRef],
) -> int:
    linked_entities: set[tuple[str, str]] = set()
    external_targets: dict[str, set[URIRef]] = {
        "wikidata_uri": set(),
        "dbpedia_uri": set(),
    }
    for row in link_rows:
        key = (row["entity_type"].strip(), row["entity_id"].strip())
        if key in linked_entities:
            raise ConversionError(f"Duplicate external-link row: {key}")
        if key not in local_resources:
            raise ConversionError(f"External link refers to unknown entity: {key}")

        local_resource = local_resources[key]
        wikidata_uri = external_uri(row["wikidata_uri"], "wikidata_uri")
        dbpedia_uri = external_uri(row["dbpedia_uri"], "dbpedia_uri")
        if not WIKIDATA_PATTERN.fullmatch(str(wikidata_uri)):
            raise ConversionError(f"Invalid Wikidata entity URI: {wikidata_uri}")
        if not DBPEDIA_PATTERN.fullmatch(str(dbpedia_uri)):
            raise ConversionError(f"Invalid DBpedia resource URI: {dbpedia_uri}")

        for column, target in (
            ("wikidata_uri", wikidata_uri),
            ("dbpedia_uri", dbpedia_uri),
        ):
            if target in external_targets[column]:
                raise ConversionError(f"Duplicate {column} target: {target}")
            external_targets[column].add(target)
            graph.add((local_resource, OWL.sameAs, target))
        linked_entities.add(key)

    missing_links = set(local_resources) - linked_entities
    if missing_links:
        missing = ", ".join(
            f"{entity_type}:{entity_id}"
            for entity_type, entity_id in sorted(missing_links)
        )
        raise ConversionError(f"Entities without external links: {missing}")
    return len(linked_entities)


def build_graph(input_dir: Path, links_path: Path) -> tuple[Graph, dict[str, int]]:
    competition_rows = read_csv(
        input_dir / "competitions.csv",
        {"competition_id", "name", "country", "competition_type", "tier"},
    )
    season_rows = read_csv(
        input_dir / "seasons.csv",
        {"season_id", "label", "competition_id", "start_date", "end_date"},
    )
    team_rows = read_csv(input_dir / "teams.csv", {"team_id", "name"})
    match_rows = read_csv(
        input_dir / "matches.csv",
        {
            "match_id",
            "competition_id",
            "season_id",
            "round",
            "match_date",
            "home_team_id",
            "away_team_id",
            "home_goals",
            "away_goals",
        },
    )
    link_rows = read_csv(
        links_path,
        {"entity_type", "entity_id", "wikidata_uri", "dbpedia_uri"},
    )

    competitions = index_rows(competition_rows, "competition_id", "competition")
    seasons = index_rows(season_rows, "season_id", "season")
    teams = index_rows(team_rows, "team_id", "team")
    matches = index_rows(match_rows, "match_id", "match")

    graph = Graph()
    bind_namespaces(graph)
    local_resources: dict[tuple[str, str], URIRef] = {}
    draw_count = 0

    dataset_uri = DATASET["premier-league-2018-19"]
    distribution_uri = DATASET["premier-league-2018-19/turtle"]
    activity_uri = DATASET["premier-league-2018-19/transformation"]
    graph.add((dataset_uri, RDF.type, DCAT.Dataset))
    graph.add((dataset_uri, RDF.type, VOID.Dataset))
    graph.add(
        (
            dataset_uri,
            DCTERMS.title,
            Literal("Premier League 2018/19 Linked Open Dataset", lang="en"),
        )
    )
    graph.add(
        (
            dataset_uri,
            DCTERMS.description,
            Literal(
                "Linked data describing teams and match results from the "
                "2018/19 English Premier League season.",
                lang="en",
            ),
        )
    )
    graph.add((dataset_uri, DCTERMS.source, SOURCE_DATA_URL))
    graph.add((dataset_uri, DCTERMS.license, CC0_LICENSE))
    graph.add((dataset_uri, DCTERMS.language, Literal("en")))
    graph.add((dataset_uri, DCTERMS.creator, PUBLISHER_URL))
    graph.add((dataset_uri, DCTERMS.publisher, PUBLISHER_URL))
    graph.add((dataset_uri, DCTERMS.issued, Literal("2026-09-27", datatype=XSD.date)))
    graph.add((dataset_uri, DCTERMS.modified, Literal("2026-10-02", datatype=XSD.date)))
    graph.add((dataset_uri, DCAT.landingPage, URIRef(BASE_URL)))
    graph.add((dataset_uri, DCAT.distribution, distribution_uri))
    graph.add((dataset_uri, VOID.dataDump, PUBLIC_DATA_URL))
    graph.add((dataset_uri, VOID.uriSpace, Literal(f"{BASE_URL}resource/")))
    graph.add((dataset_uri, PROV.wasGeneratedBy, activity_uri))

    graph.add((distribution_uri, RDF.type, DCAT.Distribution))
    graph.add(
        (
            distribution_uri,
            DCTERMS.title,
            Literal("Premier League 2018/19 RDF distribution", lang="en"),
        )
    )
    graph.add((distribution_uri, DCTERMS.license, CC0_LICENSE))
    graph.add((distribution_uri, DCAT.downloadURL, PUBLIC_DATA_URL))
    graph.add((distribution_uri, DCAT.mediaType, Literal("text/turtle")))

    graph.add((SOURCE_DATA_URL, RDF.type, PROV.Entity))
    graph.add((activity_uri, RDF.type, PROV.Activity))
    graph.add((activity_uri, PROV.used, SOURCE_DATA_URL))
    graph.add((activity_uri, PROV.generated, dataset_uri))
    graph.add((activity_uri, PROV.wasAssociatedWith, PUBLISHER_URL))
    graph.add(
        (
            activity_uri,
            PROV.endedAtTime,
            Literal("2026-10-02T00:00:00+07:00", datatype=XSD.dateTime),
        )
    )
    graph.add((URIRef(f"{BASE_URL}ontology/"), RDFS.seeAlso, PUBLIC_ONTOLOGY_URL))
    graph.add((dataset_uri, RDFS.seeAlso, REPOSITORY_URL))

    for competition_id, row in competitions.items():
        resource = COMPETITION[competition_id]
        competition_type = row["competition_type"].strip().lower()
        local_resources[("competition", competition_id)] = resource
        graph.add((resource, RDF.type, FOOT.Competition))
        if competition_type == "league":
            graph.add((resource, RDF.type, FOOT.League))
            graph.add(
                (
                    resource,
                    FOOT.tier,
                    parse_positive_integer(row["tier"], "tier"),
                )
            )
        elif competition_type == "cup":
            if row["tier"].strip():
                raise ConversionError(
                    f"Cup competition {competition_id} must not define a league tier"
                )
            graph.add((resource, RDF.type, FOOT.Cup))
        else:
            raise ConversionError(
                f"Unsupported competition_type for {competition_id}: "
                f"{competition_type!r}"
            )
        graph.add((resource, SCHEMA.name, Literal(row["name"].strip(), lang="en")))
        graph.add(
            (resource, SCHEMA.spatialCoverage, Literal(row["country"].strip(), lang="en"))
        )
        graph.add((dataset_uri, VOID.exampleResource, resource))

    for season_id, row in seasons.items():
        competition_id = row["competition_id"].strip()
        if competition_id not in competitions:
            raise ConversionError(
                f"Season {season_id} refers to unknown competition {competition_id}"
            )
        resource = SEASON[season_id]
        local_resources[("season", season_id)] = resource
        graph.add((resource, RDF.type, FOOT.Season))
        graph.add((resource, SCHEMA.name, Literal(row["label"].strip(), lang="en")))
        graph.add(
            (resource, SCHEMA.startDate, parse_iso_date(row["start_date"], "start_date"))
        )
        graph.add(
            (resource, SCHEMA.endDate, parse_iso_date(row["end_date"], "end_date"))
        )
        graph.add((resource, FOOT.partOfCompetition, COMPETITION[competition_id]))

    for team_id, row in teams.items():
        resource = TEAM[team_id]
        local_resources[("team", team_id)] = resource
        graph.add((resource, RDF.type, FOOT.FootballTeam))
        graph.add((resource, SCHEMA.name, Literal(row["name"].strip(), lang="en")))

    for match_id, row in matches.items():
        competition_id = row["competition_id"].strip()
        season_id = row["season_id"].strip()
        home_team_id = row["home_team_id"].strip()
        away_team_id = row["away_team_id"].strip()

        for entity_id, collection, label in (
            (competition_id, competitions, "competition"),
            (season_id, seasons, "season"),
            (home_team_id, teams, "home team"),
            (away_team_id, teams, "away team"),
        ):
            if entity_id not in collection:
                raise ConversionError(
                    f"Match {match_id} refers to unknown {label} {entity_id}"
                )
        if home_team_id == away_team_id:
            raise ConversionError(f"Match {match_id} uses the same team twice")

        resource = MATCH[match_id]
        home_goals = parse_non_negative_integer(row["home_goals"], "home_goals")
        away_goals = parse_non_negative_integer(row["away_goals"], "away_goals")
        label = (
            f"{teams[home_team_id]['name'].strip()} {home_goals}–{away_goals} "
            f"{teams[away_team_id]['name'].strip()}"
        )

        graph.add((resource, RDF.type, FOOT.FootballMatch))
        graph.add((resource, RDFS.label, Literal(label, lang="en")))
        graph.add((resource, FOOT.homeTeam, TEAM[home_team_id]))
        graph.add((resource, FOOT.awayTeam, TEAM[away_team_id]))
        graph.add((resource, FOOT.homeGoals, home_goals))
        graph.add((resource, FOOT.awayGoals, away_goals))
        graph.add((resource, FOOT.matchDate, parse_iso_date(row["match_date"], "match_date")))
        graph.add((resource, FOOT.roundNumber, parse_positive_integer(row["round"], "round")))
        graph.add((resource, FOOT.playedInSeason, SEASON[season_id]))
        graph.add((resource, FOOT.partOfCompetition, COMPETITION[competition_id]))
        home_goal_count = int(home_goals)
        away_goal_count = int(away_goals)
        if home_goal_count == away_goal_count:
            graph.add((resource, RDF.type, FOOT.Draw))
            draw_count += 1
        elif home_goal_count > away_goal_count:
            graph.add((resource, FOOT.winner, TEAM[home_team_id]))
            graph.add((resource, FOOT.loser, TEAM[away_team_id]))
        else:
            graph.add((resource, FOOT.winner, TEAM[away_team_id]))
            graph.add((resource, FOOT.loser, TEAM[home_team_id]))

    linked_entity_count = add_external_links(graph, link_rows, local_resources)
    for linkset_id, target_dataset in (
        ("wikidata", URIRef("https://www.wikidata.org/")),
        ("dbpedia", URIRef("https://dbpedia.org/")),
    ):
        linkset_uri = DATASET[f"premier-league-2018-19/linkset/{linkset_id}"]
        graph.add((linkset_uri, RDF.type, VOID.Linkset))
        graph.add((linkset_uri, VOID.subjectsTarget, dataset_uri))
        graph.add((linkset_uri, VOID.objectsTarget, target_dataset))
        graph.add((linkset_uri, VOID.linkPredicate, OWL.sameAs))
        graph.add((linkset_uri, VOID.triples, Literal(linked_entity_count)))
        graph.add((dataset_uri, VOID.subset, linkset_uri))
    graph.add((dataset_uri, VOID.entities, Literal(len(local_resources) + len(matches))))

    stats = {
        "competitions": len(competitions),
        "seasons": len(seasons),
        "teams": len(teams),
        "matches": len(matches),
        "draws": draw_count,
        "decisive_matches": len(matches) - draw_count,
        "linked_entities": linked_entity_count,
        "triples": len(graph),
    }
    return graph, stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert cleaned football CSV tables into linked RDF/Turtle."
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--links", type=Path, default=DEFAULT_LINKS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        graph, stats = build_graph(args.input_dir, args.links)
    except ConversionError as exc:
        raise SystemExit(f"RDF conversion failed: {exc}") from exc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=args.output, format="turtle")
    print(f"Wrote {stats['triples']} triples to {args.output.resolve()}")
    print(
        "Entities: "
        f"{stats['competitions']} competition, "
        f"{stats['seasons']} season, "
        f"{stats['teams']} teams, "
        f"{stats['matches']} matches; "
        f"{stats['linked_entities']} externally linked entities."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
