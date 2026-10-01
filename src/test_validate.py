import unittest

from rdflib import Graph

from validate import PROJECT_ROOT, check

VALID = """
@prefix fb: <http://example.org/football/ontology#> .
@prefix r: <http://example.org/football/resource/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

r:pl a fb:League ; rdfs:label "PL" ; fb:tier "1"^^xsd:positiveInteger ;
    owl:sameAs <http://www.wikidata.org/entity/Q9448> .
r:s a fb:Season ; fb:seasonOf r:pl ; fb:seasonLabel "2018/19" ;
    fb:startDate "2018-08-10"^^xsd:date ; fb:endDate "2019-05-12"^^xsd:date .
r:a a fb:Team ; rdfs:label "A" ; owl:sameAs <http://www.wikidata.org/entity/Q1> .
r:b a fb:Team ; rdfs:label "B" ; owl:sameAs <http://www.wikidata.org/entity/Q2> .
r:m a fb:Match ; fb:inSeason r:s ; fb:homeTeam r:a ; fb:awayTeam r:b ;
    fb:homeGoals "2"^^xsd:nonNegativeInteger ; fb:awayGoals "1"^^xsd:nonNegativeInteger ;
    fb:matchDate "2018-08-10"^^xsd:date ; fb:matchday "1"^^xsd:positiveInteger ;
    fb:winner r:a ; fb:loser r:b .
"""


def graph(extra: str = "") -> Graph:
    data = Graph().parse(PROJECT_ROOT / "ontology/football.ttl")
    return data.parse(data=VALID + extra, format="turtle")


class ShapeTests(unittest.TestCase):
    def test_valid_data_conforms(self) -> None:
        conforms, report = check(graph())
        self.assertTrue(conforms, report)

    def test_violations_are_reported(self) -> None:
        for broken in (
            'r:m fb:stage "Final" .',  # matchday and stage together
            "r:m a fb:Draw .",  # a draw that also has a winner
            "r:m fb:awayTeam r:a .",  # second away team, same as home team
            "r:c a fb:Team ; rdfs:label \"C\" .",  # team without a Wikidata link
        ):
            with self.subTest(broken=broken):
                self.assertFalse(check(graph(broken))[0])


if __name__ == "__main__":
    unittest.main()
