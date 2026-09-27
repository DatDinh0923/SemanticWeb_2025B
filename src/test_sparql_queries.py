import unittest

from convert_to_rdf import DEFAULT_INPUT_DIR, DEFAULT_LINKS, build_graph
from run_sparql import DEFAULT_QUERY_DIR, query_files


class SparqlQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.graph, _ = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)

    def test_every_saved_query_executes_and_returns_rows(self) -> None:
        paths = query_files(DEFAULT_QUERY_DIR)
        self.assertEqual(len(paths), 10)
        for path in paths:
            with self.subTest(query=path.name):
                result = list(self.graph.query(path.read_text(encoding="utf-8")))
                self.assertGreater(len(result), 0)


if __name__ == "__main__":
    unittest.main()
