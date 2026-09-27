import tempfile
import unittest
from pathlib import Path

from rdflib import OWL, RDF, Graph

from convert_to_rdf import (
    DEFAULT_INPUT_DIR,
    DEFAULT_LINKS,
    FOOT,
    MATCH,
    TEAM,
    build_graph,
)


class RdfConversionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.graph, cls.stats = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)

    def test_expected_entity_counts(self) -> None:
        self.assertEqual(self.stats["competitions"], 1)
        self.assertEqual(self.stats["seasons"], 1)
        self.assertEqual(self.stats["teams"], 20)
        self.assertEqual(self.stats["matches"], 380)
        self.assertEqual(self.stats["linked_entities"], 22)

    def test_expected_rdf_types_and_relationships(self) -> None:
        arsenal = TEAM["arsenal"]
        match = MATCH["2018-08-10-manchester-united-leicester-city"]
        self.assertIn((arsenal, RDF.type, FOOT.FootballTeam), self.graph)
        self.assertIn((match, RDF.type, FOOT.FootballMatch), self.graph)
        self.assertIn((match, FOOT.homeTeam, TEAM["manchester-united"]), self.graph)
        self.assertIn((match, FOOT.awayTeam, TEAM["leicester-city"]), self.graph)

    def test_every_team_has_two_external_links(self) -> None:
        for team in self.graph.subjects(RDF.type, FOOT.FootballTeam):
            self.assertEqual(len(set(self.graph.objects(team, OWL.sameAs))), 2)

    def test_serialized_graph_can_be_parsed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "football-data.ttl"
            self.graph.serialize(destination=output, format="turtle")
            parsed = Graph().parse(output, format="turtle")
            self.assertEqual(len(parsed), len(self.graph))


if __name__ == "__main__":
    unittest.main()
