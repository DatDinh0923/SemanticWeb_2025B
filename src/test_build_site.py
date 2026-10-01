import tempfile
import unittest
from pathlib import Path

from rdflib import URIRef, Graph

from build_site import DEFAULT_DATA, DEFAULT_ONTOLOGY, build_site, local_output_path
from convert_to_rdf import BASE_URL


class StaticSiteTests(unittest.TestCase):
    def test_site_contains_downloads_and_every_local_resource(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            custom_data = temporary_path / "custom-data.ttl"
            custom_ontology = temporary_path / "custom-ontology.ttl"
            custom_data.write_text(
                DEFAULT_DATA.read_text(encoding="utf-8") + "\n# custom data input\n",
                encoding="utf-8",
            )
            custom_ontology.write_text(
                DEFAULT_ONTOLOGY.read_text(encoding="utf-8")
                + "\n# custom ontology input\n",
                encoding="utf-8",
            )

            output = temporary_path / "site"
            page_count = build_site(custom_data, custom_ontology, output)

            graph = Graph().parse(DEFAULT_DATA, format="turtle")
            graph += Graph().parse(DEFAULT_ONTOLOGY, format="turtle")
            local_subjects = {
                subject
                for subject in graph.subjects()
                if isinstance(subject, URIRef) and str(subject).startswith(BASE_URL)
            }

            self.assertEqual(page_count, len(local_subjects))
            self.assertTrue((output / "index.html").is_file())
            self.assertTrue((output / "download/football-data.ttl").is_file())
            self.assertTrue((output / "download/csv/matches.csv").is_file())
            self.assertTrue((output / "ontology/football.ttl").is_file())
            self.assertTrue((output / "resource/team/arsenal/index.html").is_file())
            self.assertTrue((output / "resource/team/arsenal/data.ttl").is_file())
            self.assertEqual(
                (output / "download/football-data.ttl").read_bytes(),
                custom_data.read_bytes(),
            )
            self.assertEqual(
                (output / "ontology/football.ttl").read_bytes(),
                custom_ontology.read_bytes(),
            )
            arsenal_page = (output / "resource/team/arsenal/index.html").read_text(
                encoding="utf-8"
            )
            self.assertIn('href="../../../assets/style.css"', arsenal_page)
            self.assertIn('rel="alternate" type="text/turtle"', arsenal_page)
            self.assertNotIn(f'href="{BASE_URL}assets/style.css"', arsenal_page)
            for subject in local_subjects:
                self.assertTrue(local_output_path(output, subject).is_file())

            second_output = temporary_path / "second-site"
            build_site(custom_data, custom_ontology, second_output)
            first_files = sorted(
                path.relative_to(output) for path in output.rglob("*") if path.is_file()
            )
            second_files = sorted(
                path.relative_to(second_output)
                for path in second_output.rglob("*")
                if path.is_file()
            )
            self.assertEqual(first_files, second_files)
            for relative_path in first_files:
                self.assertEqual(
                    (output / relative_path).read_bytes(),
                    (second_output / relative_path).read_bytes(),
                    relative_path.as_posix(),
                )


if __name__ == "__main__":
    unittest.main()
