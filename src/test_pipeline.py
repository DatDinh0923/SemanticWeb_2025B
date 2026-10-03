"""Acceptance tests, including independent calculations from ORIGINAL CSVs."""
import csv
import subprocess
import sys
import tempfile
import unittest
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from rdflib import Graph, Literal
from rdflib.namespace import RDF, OWL, XSD

from clean_data import (DataValidationError, clean_all, load_aliases, load_matches,
                        validate_dataset)
from common import FB, RES, ROOT, ontology, rows, write_graph
from convert_to_rdf import build_data, build_links
from query import render_query, run_local, run_remote, equivalent
from validate_rdf import validate_graph


class DataTests(unittest.TestCase):
    def test_ten_seasons_and_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(clean_all(target), (3800, 35))
            matches = rows(target / "matches.csv")
            self.assertEqual(len({m["match_id"] for m in matches}), 3800)
            self.assertEqual(len(rows(target / "seasons.csv")), 10)
            for row in matches:
                self.assertTrue((ROOT / row["source_file"]).is_file())
                self.assertGreaterEqual(int(row["source_line"]), 2)
            for filename in ("matches.csv", "seasons.csv", "teams.csv", "competitions.csv"):
                self.assertEqual(rows(target / filename), rows(ROOT / "data/processed" / filename))
        aliases = load_aliases()
        self.assertEqual(aliases["Manchester Utd"], aliases["Manchester United FC"])
        self.assertEqual(aliases["Wolves"], aliases["Wolverhampton Wanderers FC"])

    def test_bad_source_rows_report_source_and_line(self):
        header = "Round,Date,Team 1,FT,Team 2\n"
        valid = "1,Fri Aug 10 2018,Manchester United FC,2-1,Leicester City FC\n"
        for text in (valid.replace("2-1", ""), valid.replace("Manchester United FC", "Unknown FC"), valid + valid):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "invalid.csv"
                path.write_text(header + text, encoding="utf-8")
                with self.assertRaisesRegex(DataValidationError, r"invalid.csv: line [23]"):
                    load_matches(path, "premier-league", "2018-19")

    def test_fixture_and_appearance_integrity(self):
        source = ROOT / "england_csv/2010s/2018-19/eng.1.csv"
        matches, teams = load_matches(source, "premier-league", "2018-19")
        validate_dataset(matches, teams, 380, 20)
        with self.assertRaises(DataValidationError):
            validate_dataset(matches[:-1], teams, 380, 20)
        corrupt = matches[:-1] + [replace(matches[0], match_id="different", round=38)]
        with self.assertRaisesRegex(DataValidationError, "Duplicate home/away"):
            validate_dataset(corrupt, teams, 380, 20)


class GraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_data()
        cls.graph = cls.data + build_links(cls.data) + ontology()

    def test_counts_links_and_determinism(self):
        for kind, count in ((FB.Match, 3800), (FB.Team, 35), (FB.Season, 10), (FB.Competition, 1)):
            self.assertEqual(len(set(self.graph.subjects(RDF.type, kind))), count)
        self.assertEqual(len(list(self.graph.triples((None, OWL.sameAs, None)))), 72)
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / "a.ttl", Path(directory) / "b.ttl"
            write_graph(self.data, a)
            write_graph(build_data(), b)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(set(Graph().parse(a)), set(self.data))

    def test_unverified_duplicate_or_missing_mappings_rejected(self):
        original = rows(ROOT / "data/links/entity-links.csv")
        unverified = [dict(row) for row in original]
        unverified[0]["status"] = "unverified"
        for mapping in (unverified, original[:-1], original + [original[0]]):
            with self.subTest(size=len(mapping)), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "links.csv"
                with path.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=original[0].keys())
                    writer.writeheader()
                    writer.writerows(mapping)
                with self.assertRaises(ValueError):
                    build_links(self.data, path)

    def sample_graph(self):
        match = RES["match/premier-league-2018-19-r01-manchester-united-leicester-city"]
        graph = Graph()
        # Describe one match, its participants, its season and its competition.
        subjects = {match}
        subjects.update(self.data.objects(match, FB.homeTeam))
        subjects.update(self.data.objects(match, FB.awayTeam))
        season = self.data.value(match, FB.inSeason)
        subjects.add(season)
        subjects.add(self.data.value(season, FB.seasonOf))
        for subject in subjects:
            for triple in self.data.triples((subject, None, None)):
                graph.add(triple)
        return graph, match

    def test_shacl_valid_and_invalid_fixtures(self):
        graph, match = self.sample_graph()
        self.assertTrue(validate_graph(graph)[0])
        home, away = graph.value(match, FB.homeTeam), graph.value(match, FB.awayTeam)
        for predicate, value in (
            (FB.homeTeam, away), (FB.homeGoals, Literal(-1, datatype=XSD.nonNegativeInteger)),
            (FB.homeGoals, Literal("two")), (FB.winner, away),
            (FB.homeTeam, RES["team/not-in-dataset"]), (FB.matchDate, Literal("not-a-date")),
            (FB.roundNumber, Literal(39, datatype=XSD.positiveInteger)),
        ):
            with self.subTest(predicate=predicate, value=value):
                bad = Graph() + graph
                bad.set((match, predicate, value))
                self.assertFalse(validate_graph(bad)[0])
        missing = Graph() + graph
        missing.remove((match, FB.winner, None))
        self.assertFalse(validate_graph(missing)[0])
        draw = Graph() + graph
        draw.set((match, FB.homeGoals, Literal(1, datatype=XSD.nonNegativeInteger)))
        self.assertFalse(validate_graph(draw)[0])
        draw.remove((match, FB.winner, None))
        draw.remove((match, FB.loser, None))
        self.assertTrue(validate_graph(draw)[0])


class QueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = build_data()
        cls.graph = data + build_links(data) + ontology()
        aliases = {r["source_name"]: r["team_id"] for r in rows(ROOT / "config/team-aliases.csv")}
        cls.reference, cls.raw = {}, {}
        for manifest in rows(ROOT / "config/seasons.csv"):
            label = manifest["label"]
            table = defaultdict(lambda: dict(played=0, won=0, drawn=0, lost=0, goalsFor=0, goalsAgainst=0, goalDifference=0, points=0))
            games = []
            for row in rows(ROOT / manifest["source_file"]):
                # Independent score parsing/calculation, not cleaner/RDF helpers.
                score = row["FT"].replace("\u2013", "-").replace("\u2014", "-")
                hg, ag = (int(v.strip()) for v in score.split("-"))
                home, away = aliases[row["Team 1"]], aliases[row["Team 2"]]
                games.append((home, away, hg, ag))
                for team, gf, ga in ((home, hg, ag), (away, ag, hg)):
                    line = table[team]
                    line["played"] += 1
                    line["won"] += int(gf > ga)
                    line["drawn"] += int(gf == ga)
                    line["lost"] += int(gf < ga)
                    line["goalsFor"] += gf
                    line["goalsAgainst"] += ga
                    line["goalDifference"] += gf - ga
                    line["points"] += 3 if gf > ga else 1 if gf == ga else 0
            cls.reference[label], cls.raw[label] = table, games

    def query(self, filename, season="2018-19"):
        columns, result = run_local(self.graph, render_query(ROOT / "queries" / filename, season))
        return [dict(zip(columns, row)) for row in result]

    def test_standings_against_original_csv_all_ten_seasons(self):
        for season, expected in self.reference.items():
            with self.subTest(season=season):
                result = self.query("03-standings.rq", season)
                self.assertEqual(len(result), 20)
                for row in result:
                    team = str(row["team"]).rsplit("/", 1)[1]
                    self.assertEqual({k: int(row[k]) for k in expected[team]}, expected[team])
                ranking = [(int(r["points"]), int(r["goalDifference"]), int(r["goalsFor"])) for r in result]
                self.assertEqual(ranking, sorted(ranking, reverse=True))
        result = self.query("03-standings.rq")
        self.assertEqual(str(result[0]["team"]), str(RES["team/manchester-city"]))
        self.assertEqual(int(result[0]["points"]), 98)
        self.assertEqual(int(result[1]["points"]), 97)

    def test_statistics_against_original_csv(self):
        result = self.query("08-season-statistics.rq")
        self.assertEqual(len(result), 10)
        for row in result:
            games = self.raw[str(row["seasonLabel"])]
            goals = sum(hg + ag for _, _, hg, ag in games)
            self.assertEqual(int(row["matches"]), len(games))
            self.assertEqual(int(row["goals"]), goals)
            self.assertAlmostEqual(float(row["averageGoals"]), goals / len(games))

    def test_remaining_competency_questions(self):
        games = self.raw["2018-19"]
        self.assertEqual(len(self.query("01-teams.rq")), 20)
        self.assertEqual(len(self.query("02-team-matches.rq")), 38)
        highest = max(hg + ag for _, _, hg, ag in games)
        result = self.query("04-highest-scoring.rq")
        self.assertEqual(len(result), sum(hg + ag == highest for _, _, hg, ag in games))
        self.assertTrue(all(int(r["total"]) == highest for r in result))
        self.assertEqual(len(self.query("05-draws.rq")), sum(hg == ag for _, _, hg, ag in games))
        self.assertEqual(len(self.query("06-head-to-head.rq")), 20)
        for row in self.query("07-home-away-goals.rq"):
            team = str(row["team"]).rsplit("/", 1)[1]
            self.assertEqual(int(row["homeGoals"]), sum(hg for h, _, hg, _ in games if h == team))
            self.assertEqual(int(row["awayGoals"]), sum(ag for _, a, _, ag in games if a == team))
        for row in self.query("09-season-participation.rq"):
            team = str(row["team"]).rsplit("/", 1)[1]
            self.assertEqual(int(row["seasons"]), sum(team in table for table in self.reference.values()))
        self.assertEqual(len(self.query("10-external-links.rq")), 70)

    def test_bad_query_and_parameters_fail(self):
        self.assertTrue(equivalent((["s"], [[Literal("2018-19", datatype=XSD.string)]]),
                                   (["s"], [[Literal("2018-19")]])))
        self.assertFalse(equivalent((["s"], [[Literal("2018-19", lang="en")]]),
                                    (["s"], [[Literal("2018-19")]])))
        with self.assertRaises(Exception):
            run_local(self.graph, "SELECT broken query")
        with self.assertRaises(ValueError):
            render_query(ROOT / "queries/01-teams.rq", season="2018-19> } UNION {")
        with patch("query.urlopen", side_effect=URLError("connection refused")):
            with self.assertRaises(URLError):
                run_remote("ASK { ?s ?p ?o }")

    def test_cli_reports_errors_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.rq"
            path.write_text("SELECT broken query", encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "src/query.py"), str(path)],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Query failed:", result.stderr)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
