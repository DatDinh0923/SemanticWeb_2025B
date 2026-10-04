import csv
import re
import unittest
from collections import defaultdict
from pathlib import Path

from rdflib import Graph

from run_sparql import (
    DEFAULT_DATA,
    DEFAULT_ONTOLOGY,
    DEFAULT_QUERY_DIR,
    load_graph,
    query_files,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEAM_PREFIX = "https://datdinh0923.github.io/SemanticWeb_2025B/resource/team/"
SCORE = re.compile(r"^(\d+)\s*[-–]\s*(\d+)$")

# Real-world champions, an external check on the champions query.
CHAMPIONS = {
    "2011/12": "Manchester City FC",
    "2012/13": "Manchester United FC",
    "2013/14": "Manchester City FC",
    "2014/15": "Chelsea FC",
    "2015/16": "Leicester City FC",
    "2016/17": "Chelsea FC",
    "2017/18": "Manchester City FC",
    "2018/19": "Manchester City FC",
    "2019/20": "Liverpool FC",
    "2020/21": "Manchester City FC",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def independent_table(source_file: str) -> list[tuple]:
    """Compute a league table straight from an original CSV, without the pipeline."""
    aliases = {
        row["source_name"]: row["team_id"]
        for row in read_rows(PROJECT_ROOT / "config/team-aliases.csv")
    }
    totals = defaultdict(lambda: [0, 0, 0, 0, 0, 0])  # P W D L GF GA
    for row in read_rows(PROJECT_ROOT / source_file):
        home_goals, away_goals = map(int, SCORE.fullmatch(row["FT"].strip()).groups())
        for team, scored, conceded in (
            (aliases[row["Team 1"].strip()], home_goals, away_goals),
            (aliases[row["Team 2"].strip()], away_goals, home_goals),
        ):
            record = totals[team]
            record[0] += 1
            record[1] += scored > conceded
            record[2] += scored == conceded
            record[3] += scored < conceded
            record[4] += scored
            record[5] += conceded
    table = [
        (team, p, w, d, l, gf, ga, gf - ga, 3 * w + d)
        for team, (p, w, d, l, gf, ga) in totals.items()
    ]
    return sorted(table, key=lambda row: (-row[8], -row[7], -row[5], row[0]))


class SparqlQueryTests(unittest.TestCase):
    EXPECTED_ROW_COUNTS = {
        "01-list-teams.rq": 20,
        "02-team-matches.rq": 38,
        "03-highest-scoring-matches.rq": 3,
        "04-drawn-matches.rq": 71,
        "05-home-goals-by-team.rq": 20,
        "06-matches-per-round.rq": 38,
        "07-january-2019-matches.rq": 40,
        "08-match-season-competition.rq": 10,
        "09-season-dates.rq": 10,
        "10-external-links.rq": 92,
        "11-season-standings.rq": 20,
        "12-head-to-head.rq": 20,
        "13-season-statistics.rq": 10,
        "14-season-champions.rq": 10,
        "15-team-participation.rq": 35,
        "16-ontology-reasoning.rq": 5,
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = load_graph(DEFAULT_DATA, DEFAULT_ONTOLOGY)

    def run_query(self, name: str, text: str | None = None) -> list:
        query = text or (DEFAULT_QUERY_DIR / name).read_text(encoding="utf-8")
        return list(self.graph.query(query))

    def test_every_saved_query_returns_the_expected_number_of_rows(self) -> None:
        paths = query_files(DEFAULT_QUERY_DIR)
        self.assertEqual({path.name for path in paths}, set(self.EXPECTED_ROW_COUNTS))
        for path in paths:
            with self.subTest(query=path.name):
                self.assertEqual(
                    len(self.run_query(path.name)), self.EXPECTED_ROW_COUNTS[path.name]
                )

    def test_every_query_is_valid_strict_sparql(self) -> None:
        """Jena rejects re-binding an in-scope variable with AS; rdflib does not."""
        for path in query_files(DEFAULT_QUERY_DIR):
            text = path.read_text(encoding="utf-8")
            for expression, variable in re.findall(r"\((\w+\([^()]*\))\s+AS\s+(\?\w+)\)", text):
                with self.subTest(query=path.name, variable=variable):
                    self.assertNotIn(variable, expression)

    def test_standings_match_an_independent_calculation_for_every_season(self) -> None:
        template = (DEFAULT_QUERY_DIR / "11-season-standings.rq").read_text(encoding="utf-8")
        self.assertIn("season:premier-league-2018-19", template)
        for season in read_rows(PROJECT_ROOT / "config/seasons.csv"):
            with self.subTest(season=season["season_id"]):
                query = template.replace(
                    "season:premier-league-2018-19", f"season:{season['season_id']}"
                )
                rows = self.run_query("11-season-standings.rq", query)
                actual = [
                    (
                        str(row.team).removeprefix(TEAM_PREFIX),
                        *(int(row[name]) for name in (
                            "played", "won", "drawn", "lost", "goalsFor",
                            "goalsAgainst", "goalDifference", "points",
                        )),
                    )
                    for row in rows
                ]
                self.assertEqual(actual, independent_table(season["source_file"]))

    def test_highest_scoring_query_returns_all_ten_goal_ties(self) -> None:
        rows = self.run_query("03-highest-scoring-matches.rq")
        self.assertEqual({int(row.totalGoals) for row in rows}, {10})
        self.assertIn("Manchester United FC 8–2 Arsenal FC", {str(row.label) for row in rows})

    def test_champions_query_names_every_real_champion(self) -> None:
        rows = self.run_query("14-season-champions.rq")
        self.assertEqual(
            {str(row.seasonLabel): str(row.championName) for row in rows}, CHAMPIONS
        )
        # 2011/12 was level on points and decided on goal difference.
        first = next(row for row in rows if str(row.seasonLabel) == "2011/12")
        self.assertEqual((int(first.points), int(first.goalDifference)), (89, 64))

    def test_head_to_head_spans_all_seasons(self) -> None:
        rows = self.run_query("12-head-to-head.rq")
        self.assertEqual(len({str(row.seasonLabel) for row in rows}), 10)
        outcomes = [str(row.outcome) for row in rows]
        self.assertEqual(outcomes.count("Arsenal FC"), 7)
        self.assertEqual(outcomes.count("Tottenham Hotspur FC"), 7)
        self.assertEqual(outcomes.count("Draw"), 6)

    def test_season_statistics_count_every_match_and_goal(self) -> None:
        rows = self.run_query("13-season-statistics.rq")
        self.assertTrue(all(int(row.matches) == 380 for row in rows))
        self.assertEqual(sum(int(row.goals) for row in rows), 10394)

    def test_reasoning_query_needs_the_ontology(self) -> None:
        rows = {
            str(row.term).rsplit("/", 1)[-1]: int(row.resources)
            for row in self.run_query("16-ontology-reasoning.rq")
        }
        self.assertEqual(rows["SportsEvent"], 3810)
        self.assertEqual(rows["SportsTeam"], 35)
        self.assertEqual(rows["competitor"], 3800)

        data_only = Graph().parse(DEFAULT_DATA, format="turtle")
        text = (DEFAULT_QUERY_DIR / "16-ontology-reasoning.rq").read_text(encoding="utf-8")
        self.assertEqual(list(data_only.query(text)), [])


if __name__ == "__main__":
    unittest.main()
