"""Convert the normalized tables and reviewed identity mappings to RDF."""
import json
import re
from datetime import date

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, XSD

from common import BASE, FB, RES, ROOT, RDF_DIR, ontology, rows, write_graph


def indexed(path, key):
    result = {}
    for row in rows(path):
        if row[key] in result:
            raise ValueError(f"{path}: duplicate {key}: {row[key]}")
        result[row[key]] = row
    return result


def build_data(processed=ROOT / "data/processed"):
    graph = Graph()
    competitions = indexed(processed / "competitions.csv", "competition_id")
    seasons = indexed(processed / "seasons.csv", "season_id")
    teams = indexed(processed / "teams.csv", "team_id")
    matches = indexed(processed / "matches.csv", "match_id")
    for key, row in competitions.items():
        subject = RES[f"competition/{key}"]
        graph.add((subject, RDF.type, FB.Competition))
        graph.add((subject, RDFS.label, Literal(row["name"], lang="en")))
        graph.add((subject, DCTERMS.spatial, Literal(row["country"], lang="en")))
    for key, row in teams.items():
        subject = RES[f"team/{key}"]
        graph.add((subject, RDF.type, FB.Team))
        graph.add((subject, RDFS.label, Literal(row["name"], lang="en")))
    for key, row in seasons.items():
        if row["competition_id"] not in competitions:
            raise ValueError(f"Unknown competition in season {key}")
        subject = RES[f"season/{key}"]
        graph.add((subject, RDF.type, FB.Season))
        graph.add((subject, RDFS.label, Literal("Premier League " + row["label"], lang="en")))
        graph.add((subject, FB.seasonLabel, Literal(row["label"], datatype=XSD.string)))
        graph.add((subject, FB.seasonOf, RES[f"competition/{row['competition_id']}"]))
        for prop, column in ((FB.startDate, "start_date"), (FB.endDate, "end_date")):
            graph.add((subject, prop, Literal(date.fromisoformat(row[column]), datatype=XSD.date)))
    for key, row in matches.items():
        season_id, home, away = row["season_id"], row["home_team_id"], row["away_team_id"]
        if season_id not in seasons or home not in teams or away not in teams:
            raise ValueError(f"Unknown season/team in match {key}")
        if row["competition_id"] != seasons[season_id]["competition_id"]:
            raise ValueError(f"Competition disagrees with season: {key}")
        subject = RES[f"match/{key}"]
        graph.add((subject, RDF.type, FB.Match))
        graph.add((subject, FB.inSeason, RES[f"season/{season_id}"]))
        graph.add((subject, FB.homeTeam, RES[f"team/{home}"]))
        graph.add((subject, FB.awayTeam, RES[f"team/{away}"]))
        graph.add((subject, FB.matchDate, Literal(date.fromisoformat(row["match_date"]), datatype=XSD.date)))
        for prop, column, datatype in (
            (FB.roundNumber, "round", XSD.positiveInteger),
            (FB.homeGoals, "home_goals", XSD.nonNegativeInteger),
            (FB.awayGoals, "away_goals", XSD.nonNegativeInteger),
            (FB.sourceLine, "source_line", XSD.positiveInteger),
        ):
            graph.add((subject, prop, Literal(int(row[column]), datatype=datatype)))
        graph.add((subject, FB.sourceFile, Literal(row["source_file"], datatype=XSD.string)))
        source_uri = "https://github.com/footballcsv/england/blob/master/" + row["source_file"].removeprefix("england_csv/")
        graph.add((subject, DCTERMS.source, URIRef(source_uri)))
        hg, ag = int(row["home_goals"]), int(row["away_goals"])
        if hg != ag:
            winner, loser = (home, away) if hg > ag else (away, home)
            graph.add((subject, FB.winner, RES[f"team/{winner}"]))
            graph.add((subject, FB.loser, RES[f"team/{loser}"]))
    dataset = URIRef(BASE + "dataset")
    graph.add((dataset, RDF.type, URIRef("http://www.w3.org/ns/dcat#Dataset")))
    graph.add((dataset, DCTERMS.title, Literal("Premier League 2011/12–2020/21 — phongph5", lang="en")))
    graph.add((dataset, DCTERMS.description, Literal("Full-time results for ten seasons; local coursework dataset.", lang="en")))
    graph.add((dataset, DCTERMS.temporal, Literal("2011/12–2020/21")))
    graph.add((dataset, DCTERMS.source, URIRef("https://github.com/footballcsv/england")))
    graph.add((dataset, DCTERMS.license, URIRef("https://creativecommons.org/publicdomain/zero/1.0/")))
    return graph


def build_links(data, mapping_path=ROOT / "data/links/entity-links.csv"):
    expected = {str(s): kind for cls, kind in ((FB.Team, "team"), (FB.Competition, "competition")) for s in data.subjects(RDF.type, cls)}
    graph, seen, targets = Graph(), set(), set()
    for row in rows(mapping_path):
        local = str(RES[f"{row['entity_type']}/{row['entity_id']}"])
        if local not in expected or local in seen:
            raise ValueError(f"Unknown or duplicate mapping: {local}")
        if row["status"] != "verified":
            raise ValueError(f"Mapping not verified: {local}")
        date.fromisoformat(row["verified_on"])
        wd, db = row["wikidata_uri"], row["dbpedia_uri"]
        if not re.fullmatch(r"http://www\.wikidata\.org/entity/Q[1-9][0-9]*", wd) or not db.startswith("http://dbpedia.org/resource/") or any(c.isspace() for c in db):
            raise ValueError(f"Invalid external URI: {local}")
        evidence_path = (ROOT / row["evidence"]).resolve()
        if not evidence_path.is_relative_to(ROOT / "data/links/evidence"):
            raise ValueError("Evidence must be inside data/links/evidence")
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        if evidence["wikidata_uri"] != wd or evidence["dbpedia_uri"] != db or not evidence["dbpedia_links_to_wikidata"] or evidence["checked_on"] != row["verified_on"]:
            raise ValueError(f"Evidence disagrees with mapping: {local}")
        for uri in (wd, db):
            if uri in targets:
                raise ValueError(f"External identity reused: {uri}")
            targets.add(uri)
            graph.add((URIRef(local), OWL.sameAs, URIRef(uri)))
        seen.add(local)
    if seen != set(expected):
        raise ValueError(f"Missing mappings: {sorted(set(expected) - seen)}")
    return graph


def convert():
    data = build_data()
    links = build_links(data)
    # Finish validation of all inputs before replacing any output.
    write_graph(data, RDF_DIR / "football.ttl")
    write_graph(links, RDF_DIR / "links.ttl")
    write_graph(ontology(), RDF_DIR / "ontology.ttl")
    print(f"RDF: {len(data)} data triples, {len(links)} external links", flush=True)
    return data + links + ontology()


if __name__ == "__main__":
    try:
        convert()
    except (ValueError, OSError, KeyError) as exc:
        raise SystemExit(f"RDF conversion failed: {exc}") from exc
