import unittest

from pyshacl import validate
from rdflib import OWL, Graph, RDF

from convert_to_rdf import (
    COMPETITION,
    DATASET,
    DEFAULT_INPUT_DIR,
    DEFAULT_LINKS,
    FOOT,
    build_graph,
)
from validate_rdf import DEFAULT_ONTOLOGY, DEFAULT_SHAPES


class ShaclValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ontology = Graph().parse(DEFAULT_ONTOLOGY, format="turtle")
        cls.shapes = Graph().parse(DEFAULT_SHAPES, format="turtle")

    def validate(self, graph: Graph) -> bool:
        conforms, _, _ = validate(
            graph,
            shacl_graph=self.shapes,
            ont_graph=self.ontology,
            inference="rdfs",
            abort_on_first=False,
        )
        return bool(conforms)

    def match_fixture(self, graph: Graph, match: object) -> Graph:
        """Keep one match plus the resources required by every targeted shape."""
        fixture = Graph()
        for prefix, namespace in graph.namespaces():
            fixture.bind(prefix, namespace)

        subjects = {
            match,
            graph.value(match, FOOT.homeTeam),
            graph.value(match, FOOT.awayTeam),
            graph.value(match, FOOT.playedInSeason),
            graph.value(match, FOOT.partOfCompetition),
            DATASET["premier-league-2018-19"],
        }
        for subject in subjects:
            for triple in graph.triples((subject, None, None)):
                fixture.add(triple)

        dataset = DATASET["premier-league-2018-19"]
        for obj in fixture.objects(dataset, None):
            for triple in graph.triples((obj, RDF.type, None)):
                fixture.add(triple)
        return fixture

    def test_complete_dataset_conforms(self) -> None:
        graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)
        self.assertTrue(self.validate(graph))

    def test_missing_home_team_is_rejected(self) -> None:
        full_graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)
        match = next(full_graph.subjects(RDF.type, FOOT.FootballMatch))
        graph = self.match_fixture(full_graph, match)
        graph.remove((match, FOOT.homeTeam, None))
        self.assertFalse(self.validate(graph))

    def test_missing_external_link_is_rejected(self) -> None:
        full_graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)
        match = next(full_graph.subjects(RDF.type, FOOT.FootballMatch))
        graph = self.match_fixture(full_graph, match)
        team = next(graph.subjects(RDF.type, FOOT.FootballTeam))
        external_link = next(graph.objects(team, OWL.sameAs))
        graph.remove((team, OWL.sameAs, external_link))
        self.assertFalse(self.validate(graph))

    def test_missing_league_tier_is_rejected(self) -> None:
        full_graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)
        match = next(full_graph.subjects(RDF.type, FOOT.FootballMatch))
        graph = self.match_fixture(full_graph, match)
        graph.remove((COMPETITION["premier-league"], FOOT.tier, None))
        self.assertFalse(self.validate(graph))

    def test_draw_with_a_winner_is_rejected(self) -> None:
        full_graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)
        match = next(full_graph.subjects(RDF.type, FOOT.Draw))
        graph = self.match_fixture(full_graph, match)
        home_team = next(graph.objects(match, FOOT.homeTeam))
        graph.add((match, FOOT.winner, home_team))
        self.assertFalse(self.validate(graph))

    def test_equal_score_without_draw_type_is_rejected(self) -> None:
        full_graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)
        match = next(full_graph.subjects(RDF.type, FOOT.Draw))
        graph = self.match_fixture(full_graph, match)
        graph.remove((match, RDF.type, FOOT.Draw))
        self.assertFalse(self.validate(graph))

    def test_decisive_match_without_winner_is_rejected(self) -> None:
        full_graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)
        match = next(full_graph.subjects(FOOT.winner, None))
        graph = self.match_fixture(full_graph, match)
        graph.remove((match, FOOT.winner, None))
        self.assertFalse(self.validate(graph))

    def test_incorrect_winner_is_rejected(self) -> None:
        full_graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)
        match = next(full_graph.subjects(FOOT.winner, None))
        graph = self.match_fixture(full_graph, match)
        winner = next(graph.objects(match, FOOT.winner))
        loser = next(graph.objects(match, FOOT.loser))
        graph.set((match, FOOT.winner, loser))
        graph.set((match, FOOT.loser, winner))
        self.assertFalse(self.validate(graph))


if __name__ == "__main__":
    unittest.main()
