import tempfile
import unittest
from pathlib import Path

from rdflib import DCAT, OWL, RDF, XSD, Graph, Literal, URIRef

from convert_to_rdf import (
    DEFAULT_INPUT_DIR,
    DEFAULT_LINKS,
    COMPETITION,
    DATASET,
    FOOT,
    MATCH,
    PROV,
    TEAM,
    VOID,
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
        self.assertEqual(self.stats["draws"], 71)
        self.assertEqual(self.stats["decisive_matches"], 309)
        self.assertEqual(self.stats["linked_entities"], 22)

    def test_expected_rdf_types_and_relationships(self) -> None:
        arsenal = TEAM["arsenal"]
        match = MATCH["2018-08-10-manchester-united-leicester-city"]
        self.assertIn((arsenal, RDF.type, FOOT.FootballTeam), self.graph)
        self.assertIn((match, RDF.type, FOOT.FootballMatch), self.graph)
        self.assertIn((match, FOOT.homeTeam, TEAM["manchester-united"]), self.graph)
        self.assertIn((match, FOOT.awayTeam, TEAM["leicester-city"]), self.graph)
        self.assertIn((match, FOOT.winner, TEAM["manchester-united"]), self.graph)
        self.assertIn((match, FOOT.loser, TEAM["leicester-city"]), self.graph)

    def test_competition_is_a_first_tier_league(self) -> None:
        competition = COMPETITION["premier-league"]
        self.assertIn((competition, RDF.type, FOOT.Competition), self.graph)
        self.assertIn((competition, RDF.type, FOOT.League), self.graph)
        self.assertIn(
            (
                competition,
                FOOT.tier,
                Literal(1, datatype=XSD.positiveInteger),
            ),
            self.graph,
        )

    def test_draws_and_decisive_results_have_consistent_outcomes(self) -> None:
        draws = set(self.graph.subjects(RDF.type, FOOT.Draw))
        matches = set(self.graph.subjects(RDF.type, FOOT.FootballMatch))
        self.assertEqual(len(draws), 71)
        self.assertEqual(len(matches - draws), 309)

        for match in draws:
            self.assertEqual(list(self.graph.objects(match, FOOT.winner)), [])
            self.assertEqual(list(self.graph.objects(match, FOOT.loser)), [])
        for match in matches - draws:
            self.assertEqual(len(list(self.graph.objects(match, FOOT.winner))), 1)
            self.assertEqual(len(list(self.graph.objects(match, FOOT.loser))), 1)

    def test_every_team_has_two_external_links(self) -> None:
        for team in self.graph.subjects(RDF.type, FOOT.FootballTeam):
            self.assertEqual(len(set(self.graph.objects(team, OWL.sameAs))), 2)

    def test_dataset_has_distribution_linksets_and_provenance(self) -> None:
        dataset = DATASET["premier-league-2018-19"]
        distributions = set(self.graph.objects(dataset, DCAT.distribution))
        linksets = set(self.graph.objects(dataset, VOID.subset))
        activities = set(self.graph.objects(dataset, PROV.wasGeneratedBy))

        self.assertEqual(len(distributions), 1)
        self.assertTrue(
            all(
                (distribution, RDF.type, DCAT.Distribution) in self.graph
                for distribution in distributions
            )
        )
        self.assertEqual(len(linksets), 2)
        self.assertTrue(
            all(
                (linkset, RDF.type, VOID.Linkset) in self.graph
                for linkset in linksets
            )
        )
        self.assertEqual(len(activities), 1)
        self.assertTrue(
            all(
                (activity, RDF.type, PROV.Activity) in self.graph
                for activity in activities
            )
        )
        self.assertIn(
            (
                dataset,
                DCAT.landingPage,
                URIRef("https://datdinh0923.github.io/SemanticWeb_2025B/"),
            ),
            self.graph,
        )

    def test_serialized_graph_can_be_parsed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "football-data.ttl"
            self.graph.serialize(destination=output, format="turtle")
            parsed = Graph().parse(output, format="turtle")
            self.assertEqual(len(parsed), len(self.graph))


if __name__ == "__main__":
    unittest.main()
