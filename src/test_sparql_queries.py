import unittest

from convert_to_rdf import DEFAULT_INPUT_DIR, DEFAULT_LINKS, build_graph
from run_sparql import DEFAULT_QUERY_DIR, query_files


class SparqlQueryTests(unittest.TestCase):
    EXPECTED_ROW_COUNTS = {
        "01-list-teams.rq": 20,
        "02-arsenal-matches.rq": 38,
        "03-highest-scoring-matches.rq": 2,
        "04-drawn-matches.rq": 71,
        "05-home-goals-by-team.rq": 20,
        "06-matches-per-round.rq": 38,
        "07-january-2019-matches.rq": 40,
        "08-match-season-competition.rq": 380,
        "09-season-dates.rq": 1,
        "10-team-external-links.rq": 40,
        "11-season-standings.rq": 20,
        "12-arsenal-tottenham-head-to-head.rq": 2,
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)

    def test_every_saved_query_returns_the_expected_number_of_rows(self) -> None:
        paths = query_files(DEFAULT_QUERY_DIR)
        self.assertEqual({path.name for path in paths}, set(self.EXPECTED_ROW_COUNTS))
        for path in paths:
            with self.subTest(query=path.name):
                result = list(self.graph.query(path.read_text(encoding="utf-8")))
                self.assertEqual(len(result), self.EXPECTED_ROW_COUNTS[path.name])

    def test_highest_scoring_query_returns_all_maximum_ties(self) -> None:
        path = DEFAULT_QUERY_DIR / "03-highest-scoring-matches.rq"
        rows = list(self.graph.query(path.read_text(encoding="utf-8")))
        self.assertEqual({int(row.totalGoals) for row in rows}, {8})

    def test_standings_query_returns_the_expected_champion(self) -> None:
        path = DEFAULT_QUERY_DIR / "11-season-standings.rq"
        rows = list(self.graph.query(path.read_text(encoding="utf-8")))
        champion = rows[0]
        self.assertEqual(str(champion.teamName), "Manchester City FC")
        self.assertEqual(int(champion.played), 38)
        self.assertEqual(int(champion.won), 32)
        self.assertEqual(int(champion.drawn), 2)
        self.assertEqual(int(champion.lost), 4)
        self.assertEqual(int(champion.goalsFor), 95)
        self.assertEqual(int(champion.goalsAgainst), 23)
        self.assertEqual(int(champion.goalDifference), 72)
        self.assertEqual(int(champion.points), 98)

    def test_head_to_head_query_includes_a_win_and_a_draw(self) -> None:
        path = DEFAULT_QUERY_DIR / "12-arsenal-tottenham-head-to-head.rq"
        rows = list(self.graph.query(path.read_text(encoding="utf-8")))
        self.assertEqual(
            [str(row.date) for row in rows],
            ["2018-12-02", "2019-03-02"],
        )
        self.assertEqual({str(row.outcome) for row in rows}, {"Arsenal FC", "Draw"})


if __name__ == "__main__":
    unittest.main()
