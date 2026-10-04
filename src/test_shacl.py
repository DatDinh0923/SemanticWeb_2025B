import unittest

from pyshacl import validate
from rdflib import OWL, RDF, XSD, Graph, Literal, URIRef

from convert_to_rdf import (
    COMPETITION,
    DATASET,
    DEFAULT_INPUT_DIR,
    DEFAULT_LINKS,
    FOOT,
    MATCH,
    PROV,
    TEAM,
    build_graph,
)
from validate_rdf import DEFAULT_ONTOLOGY, DEFAULT_SHAPES


SCHEMA_START_DATE = URIRef("https://schema.org/startDate")


class ShaclValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ontology = Graph().parse(DEFAULT_ONTOLOGY, format="turtle")
        cls.shapes = Graph().parse(DEFAULT_SHAPES, format="turtle")
        cls.full_graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)
        cls.decisive = MATCH["2018-08-10-manchester-united-leicester-city"]
        cls.draw = next(cls.full_graph.subjects(RDF.type, FOOT.Draw))

    def validate(self, graph: Graph) -> tuple[bool, str]:
        conforms, _, report = validate(
            graph,
            shacl_graph=self.shapes,
            ont_graph=self.ontology,
            inference="rdfs",
            abort_on_first=False,
        )
        return bool(conforms), report

    def fixture(self, *matches: URIRef) -> Graph:
        """Keep some matches plus every resource the targeted shapes need."""
        graph = self.full_graph
        fixture = Graph()
        for prefix, namespace in graph.namespaces():
            fixture.bind(prefix, namespace)

        dataset = DATASET["premier-league"]
        subjects = {dataset, *graph.objects(dataset, None)}
        for match in matches:
            subjects |= {
                match,
                graph.value(match, FOOT.homeTeam),
                graph.value(match, FOOT.awayTeam),
                graph.value(match, FOOT.playedInSeason),
                graph.value(match, FOOT.partOfCompetition),
            }
        for subject in subjects:
            for triple in graph.triples((subject, None, None)):
                fixture.add(triple)
        return fixture

    def assert_rejected(self, graph: Graph, expected: str) -> None:
        """Fail unless validation fails with the expected rule's report text."""
        conforms, report = self.validate(graph)
        self.assertFalse(conforms)
        self.assertIn(expected, report)

    def test_complete_dataset_conforms(self) -> None:
        self.assertTrue(self.validate(self.full_graph)[0])

    def test_valid_fixtures_conform(self) -> None:
        self.assertTrue(self.validate(self.fixture(self.decisive, self.draw))[0])

    def test_missing_home_team_is_rejected(self) -> None:
        graph = self.fixture(self.decisive)
        graph.remove((self.decisive, FOOT.homeTeam, None))
        self.assert_rejected(graph, "MinCountConstraintComponent")

    def test_same_home_and_away_team_is_rejected(self) -> None:
        graph = self.fixture(self.decisive)
        graph.set((self.decisive, FOOT.awayTeam, TEAM["manchester-united"]))
        self.assert_rejected(graph, "The home and away teams must be different.")

    def test_negative_or_untyped_goals_are_rejected(self) -> None:
        for value in (Literal(-1, datatype=XSD.integer), Literal("two")):
            with self.subTest(value=value):
                graph = self.fixture(self.decisive)
                graph.set((self.decisive, FOOT.homeGoals, value))
                self.assert_rejected(graph, "DatatypeConstraintComponent")

    def test_round_outside_the_season_is_rejected(self) -> None:
        graph = self.fixture(self.decisive)
        graph.set(
            (self.decisive, FOOT.roundNumber, Literal(39, datatype=XSD.positiveInteger))
        )
        self.assert_rejected(graph, "MaxInclusiveConstraintComponent")

    def test_match_date_outside_its_season_is_rejected(self) -> None:
        graph = self.fixture(self.decisive)
        season = graph.value(self.decisive, FOOT.playedInSeason)
        graph.set(
            (season, SCHEMA_START_DATE, Literal("2018-08-11", datatype=XSD.date))
        )
        self.assert_rejected(graph, "must fall within its season dates")

    def test_missing_external_link_is_rejected(self) -> None:
        graph = self.fixture(self.decisive)
        team = TEAM["manchester-united"]
        graph.remove((team, OWL.sameAs, next(graph.objects(team, OWL.sameAs))))
        self.assert_rejected(graph, "owl:sameAs")

    def test_missing_league_tier_is_rejected(self) -> None:
        graph = self.fixture(self.decisive)
        graph.remove((COMPETITION["premier-league"], FOOT.tier, None))
        self.assert_rejected(graph, "foot:tier")

    def test_draw_with_a_winner_is_rejected(self) -> None:
        graph = self.fixture(self.draw)
        graph.add((self.draw, FOOT.winner, graph.value(self.draw, FOOT.homeTeam)))
        self.assert_rejected(graph, "MaxCountConstraintComponent")

    def test_equal_score_without_draw_type_is_rejected(self) -> None:
        graph = self.fixture(self.draw)
        graph.remove((self.draw, RDF.type, FOOT.Draw))
        self.assert_rejected(graph, "Draw typing must agree")

    def test_decisive_match_without_winner_is_rejected(self) -> None:
        graph = self.fixture(self.decisive)
        graph.remove((self.decisive, FOOT.winner, None))
        self.assert_rejected(graph, "must have the score's winner and loser")

    def test_incorrect_winner_is_rejected(self) -> None:
        graph = self.fixture(self.decisive)
        graph.set((self.decisive, FOOT.winner, TEAM["leicester-city"]))
        graph.set((self.decisive, FOOT.loser, TEAM["manchester-united"]))
        self.assert_rejected(graph, "must have the score's winner and loser")

    def test_missing_source_line_is_rejected(self) -> None:
        graph = self.fixture(self.decisive)
        graph.remove((self.decisive, FOOT.sourceLine, None))
        self.assert_rejected(graph, "foot:sourceLine")

    def test_source_file_that_differs_from_the_season_is_rejected(self) -> None:
        graph = self.fixture(self.decisive)
        graph.set(
            (
                self.decisive,
                PROV.wasDerivedFrom,
                URIRef("https://github.com/footballcsv/england/blob/master/other.csv"),
            )
        )
        self.assert_rejected(graph, "same source file as its season")

    def test_repeated_fixture_in_a_season_is_rejected(self) -> None:
        graph = self.fixture(self.decisive)
        replay = MATCH["2018-08-11-manchester-united-leicester-city"]
        for _, predicate, obj in list(graph.triples((self.decisive, None, None))):
            graph.add((replay, predicate, obj))
        graph.set((replay, FOOT.matchDate, Literal("2018-08-11", datatype=XSD.date)))
        self.assert_rejected(graph, "same home/away fixture twice")


if __name__ == "__main__":
    unittest.main()
