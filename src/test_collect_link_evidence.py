import unittest
from unittest.mock import patch

import collect_link_evidence
from collect_link_evidence import collect


def wikidata_entity(qid: str, title: str, instance_of: list[str], **claims: list[str]):
    def claim(value: str) -> dict:
        return {"mainsnak": {"datavalue": {"value": {"id": value}}}}

    all_claims = {"P31": instance_of, "P641": ["Q2736"], **claims}
    return {
        "entities": {
            qid: {
                "lastrevid": 1,
                "labels": {"en": {"value": title}},
                "descriptions": {"en": {"value": "test entity"}},
                "sitelinks": {"enwiki": {"title": title}},
                "claims": {
                    name: [claim(value) for value in values]
                    for name, values in all_claims.items()
                },
            }
        }
    }


def dbpedia_same_as(*targets: str) -> dict:
    return {
        "results": {
            "bindings": [
                {
                    "p": {"value": collect_link_evidence.SAME_AS},
                    "o": {"value": target},
                }
                for target in targets
            ]
        }
    }


class EvidenceCheckTests(unittest.TestCase):
    def run_collect(self, row: dict[str, str], entity: dict, dbpedia: dict) -> dict:
        def fake_fetch(url: str, accept: str = "application/json") -> dict:
            return entity if "wikidata.org" in url else dbpedia

        with patch.object(collect_link_evidence, "fetch_json", side_effect=fake_fetch):
            return collect(row)

    def season_row(self, qid: str) -> dict[str, str]:
        return {
            "entity_type": "season",
            "entity_id": "premier-league-2018-19",
            "wikidata_uri": f"http://www.wikidata.org/entity/{qid}",
            "dbpedia_uri": "http://dbpedia.org/resource/2018–19_Premier_League",
        }

    def test_premier_league_season_passes(self) -> None:
        evidence = self.run_collect(
            self.season_row("Q39052816"),
            wikidata_entity(
                "Q39052816", "2018–19 Premier League", ["Q27020041"], P3450=["Q9448"]
            ),
            dbpedia_same_as("http://www.wikidata.org/entity/Q39052816"),
        )
        self.assertTrue(evidence["passed"], evidence["checks"])

    def test_season_of_another_premier_league_fails(self) -> None:
        # Same label pattern, different league (Bosnia and Herzegovina).
        evidence = self.run_collect(
            self.season_row("Q54841887"),
            wikidata_entity(
                "Q54841887",
                "2018–19 Premier League",
                ["Q27020041"],
                P3450=["Q1201418"],
            ),
            dbpedia_same_as("http://www.wikidata.org/entity/Q54841887"),
        )
        self.assertFalse(evidence["passed"])
        self.assertFalse(evidence["checks"]["wikidata_season_of_premier_league"])

    def test_disambiguation_page_fails(self) -> None:
        evidence = self.run_collect(
            self.season_row("Q104635361"),
            wikidata_entity("Q104635361", "2020–21 Premier League", ["Q4167410"]),
            dbpedia_same_as(),
        )
        self.assertFalse(evidence["passed"])
        self.assertFalse(evidence["checks"]["wikidata_type_matches"])
        self.assertFalse(evidence["checks"]["dbpedia_links_to_wikidata"])

    def test_mens_team_type_is_accepted_for_clubs(self) -> None:
        row = {
            "entity_type": "team",
            "entity_id": "chelsea",
            "wikidata_uri": "http://www.wikidata.org/entity/Q9616",
            "dbpedia_uri": "http://dbpedia.org/resource/Chelsea_F.C.",
        }
        evidence = self.run_collect(
            row,
            wikidata_entity("Q9616", "Chelsea F.C.", ["Q103229495"]),
            dbpedia_same_as("http://www.wikidata.org/entity/Q9616"),
        )
        self.assertTrue(evidence["passed"], evidence["checks"])


if __name__ == "__main__":
    unittest.main()
