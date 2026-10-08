import unittest

from rdflib import OWL, Graph

from check_reasoning import (
    DEFAULT_DATA,
    DEFAULT_ONTOLOGY,
    DECISIVE_MATCH,
    FOOT,
    INJECTIONS,
    TEAM,
    match_subgraph,
    reason,
    remove_match_competitions,
    run_injection,
)


class ReasoningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = Graph().parse(DEFAULT_DATA, format="turtle")

    def test_unmodified_match_is_consistent(self) -> None:
        graph = match_subgraph(self.data, DEFAULT_ONTOLOGY, DECISIVE_MATCH)
        self.assertEqual(reason(graph), [])

    def test_property_chain_infers_the_match_competition(self) -> None:
        graph = match_subgraph(self.data, DEFAULT_ONTOLOGY, DECISIVE_MATCH)
        season = graph.value(DECISIVE_MATCH, FOOT.playedInSeason)
        competition = self.data.value(season, FOOT.partOfCompetition)
        graph.add((season, FOOT.partOfCompetition, competition))
        self.assertEqual(remove_match_competitions(graph), 1)
        self.assertIsNone(graph.value(DECISIVE_MATCH, FOOT.partOfCompetition))

        reason(graph)
        self.assertEqual(graph.value(DECISIVE_MATCH, FOOT.partOfCompetition), competition)

    def test_each_deliberate_error_has_the_expected_verdict(self) -> None:
        for injection in INJECTIONS:
            with self.subTest(injection=injection.name):
                errors, _ = run_injection(self.data, DEFAULT_ONTOLOGY, injection)
                self.assertEqual(bool(errors), injection.expect_inconsistent)

    def test_second_home_team_is_merged_with_the_first_instead_of_rejected(self) -> None:
        injection = next(i for i in INJECTIONS if not i.expect_inconsistent)
        _, closure = run_injection(self.data, DEFAULT_ONTOLOGY, injection)
        self.assertIn(
            (TEAM["manchester-united"], OWL.sameAs, TEAM["arsenal"]), closure
        )


if __name__ == "__main__":
    unittest.main()
