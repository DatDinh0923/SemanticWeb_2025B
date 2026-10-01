import tempfile
import unittest
from pathlib import Path

from rdflib.namespace import OWL, RDF, VOID

from to_rdf import FB, WD, build_data_graph, build_links_graph, build_void_graph, uri


TABLES = {
    "competitions.csv": "competition_id,name,tier\n"
    "premier-league,Premier League,1\nfa-cup,FA Cup,\n",
    "seasons.csv": "season_id,label,competition_id,start_date,end_date\n"
    "premier-league-2018-19,2018/19,premier-league,2018-08-10,2018-08-11\n",
    "teams.csv": "team_id,name\narsenal,Arsenal FC\nchelsea,Chelsea FC\n",
    "matches.csv": "match_id,competition_id,season_id,round,match_date,home_team_id,away_team_id,home_goals,away_goals\n"
    "m1,premier-league,premier-league-2018-19,1,2018-08-10,arsenal,chelsea,0,2\n"
    "m2,premier-league,premier-league-2018-19,2,2018-08-11,chelsea,arsenal,1,1\n",
}


class ToRdfTests(unittest.TestCase):
    def test_results_competitions_and_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            for name, content in TABLES.items():
                (directory / name).write_text(content, encoding="utf-8")
            (directory / "team_links.csv").write_text(
                "team_id,name,wikidata,wikidata_label,dbpedia\narsenal,Arsenal FC,Q9617,,Arsenal_F.C.\n",
                encoding="utf-8",
            )

            data = build_data_graph(directory)
            links = build_links_graph(directory, directory)

        self.assertEqual(data.value(uri("match", "m1"), FB.winner), uri("team", "chelsea"))
        self.assertEqual(data.value(uri("match", "m1"), FB.loser), uri("team", "arsenal"))
        self.assertIn((uri("match", "m2"), RDF.type, FB.Draw), data)
        self.assertIsNone(data.value(uri("match", "m2"), FB.winner))
        self.assertEqual(data.value(uri("match", "m1"), FB.matchday).toPython(), 1)
        self.assertEqual(len(list(data.subjects(RDF.type, FB.Cup))), 1)
        self.assertIn((uri("team", "arsenal"), OWL.sameAs, WD.Q9617), links)

        void = build_void_graph(data, links)
        linkset = uri("dataset", "linkset-wikidata")
        self.assertEqual(void.value(linkset, VOID.triples).toPython(), 1)
        self.assertEqual(void.value(uri("dataset", "Match"), VOID.entities).toPython(), 2)


if __name__ == "__main__":
    unittest.main()
