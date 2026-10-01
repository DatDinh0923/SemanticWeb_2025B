import unittest

from pyshacl import validate
from rdflib import OWL, Graph, RDF

from convert_to_rdf import DEFAULT_INPUT_DIR, DEFAULT_LINKS, FOOT, build_graph
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

    def test_complete_dataset_conforms(self) -> None:
        graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)
        self.assertTrue(self.validate(graph))

    def test_missing_home_team_is_rejected(self) -> None:
        graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)
        match = next(graph.subjects(RDF.type, FOOT.FootballMatch))
        graph.remove((match, FOOT.homeTeam, None))
        self.assertFalse(self.validate(graph))

    def test_missing_external_link_is_rejected(self) -> None:
        graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)
        team = next(graph.subjects(RDF.type, FOOT.FootballTeam))
        external_link = next(graph.objects(team, OWL.sameAs))
        graph.remove((team, OWL.sameAs, external_link))
        self.assertFalse(self.validate(graph))


if __name__ == "__main__":
    unittest.main()
