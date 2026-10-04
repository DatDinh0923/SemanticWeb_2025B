import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from rdflib import DCAT, OWL, RDF, XSD, Graph, Literal, URIRef

from convert_to_rdf import (
    COMPETITION,
    DATASET,
    DEFAULT_EVIDENCE_ROOT,
    DEFAULT_INPUT_DIR,
    DEFAULT_LINKS,
    DEFAULT_OUTPUT,
    FOOT,
    MATCH,
    PROV,
    SEASON,
    TEAM,
    VOID,
    ConversionError,
    build_graph,
)


class RdfConversionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.graph, cls.stats = build_graph(DEFAULT_INPUT_DIR, DEFAULT_LINKS)

    def test_expected_entity_counts(self) -> None:
        self.assertEqual(self.stats["competitions"], 1)
        self.assertEqual(self.stats["seasons"], 10)
        self.assertEqual(self.stats["teams"], 35)
        self.assertEqual(self.stats["matches"], 3800)
        self.assertEqual(self.stats["draws"], 908)
        self.assertEqual(self.stats["decisive_matches"], 2892)
        self.assertEqual(self.stats["linked_entities"], 46)

    def test_expected_rdf_types_and_relationships(self) -> None:
        match = MATCH["2018-08-10-manchester-united-leicester-city"]
        self.assertIn((TEAM["arsenal"], RDF.type, FOOT.FootballTeam), self.graph)
        self.assertIn((match, RDF.type, FOOT.FootballMatch), self.graph)
        self.assertIn((match, FOOT.homeTeam, TEAM["manchester-united"]), self.graph)
        self.assertIn((match, FOOT.awayTeam, TEAM["leicester-city"]), self.graph)
        self.assertIn((match, FOOT.winner, TEAM["manchester-united"]), self.graph)
        self.assertIn((match, FOOT.loser, TEAM["leicester-city"]), self.graph)
        self.assertIn(
            (match, FOOT.playedInSeason, SEASON["premier-league-2018-19"]), self.graph
        )

    def test_matches_record_their_source_row(self) -> None:
        match = MATCH["2018-08-10-manchester-united-leicester-city"]
        source = URIRef(
            "https://github.com/footballcsv/england/blob/master/2010s/2018-19/eng.1.csv"
        )
        self.assertIn((match, PROV.wasDerivedFrom, source), self.graph)
        self.assertIn(
            (match, FOOT.sourceLine, Literal(2, datatype=XSD.positiveInteger)),
            self.graph,
        )
        self.assertIn(
            (SEASON["premier-league-2018-19"], PROV.wasDerivedFrom, source), self.graph
        )

    def test_seasons_have_names_and_short_labels(self) -> None:
        season = SEASON["premier-league-2019-20"]
        self.assertIn((season, FOOT.seasonLabel, Literal("2019/20")), self.graph)
        self.assertEqual(
            str(self.graph.value(season, URIRef("https://schema.org/name"))),
            "English Premier League 2019/20",
        )

    def test_competition_is_a_first_tier_league(self) -> None:
        competition = COMPETITION["premier-league"]
        self.assertIn((competition, RDF.type, FOOT.League), self.graph)
        self.assertIn(
            (competition, FOOT.tier, Literal(1, datatype=XSD.positiveInteger)),
            self.graph,
        )

    def test_draws_and_decisive_results_have_consistent_outcomes(self) -> None:
        draws = set(self.graph.subjects(RDF.type, FOOT.Draw))
        matches = set(self.graph.subjects(RDF.type, FOOT.FootballMatch))
        self.assertEqual(len(draws), 908)
        for match in draws:
            self.assertIsNone(self.graph.value(match, FOOT.winner))
            self.assertIsNone(self.graph.value(match, FOOT.loser))
        for match in matches - draws:
            self.assertEqual(len(list(self.graph.objects(match, FOOT.winner))), 1)
            self.assertEqual(len(list(self.graph.objects(match, FOOT.loser))), 1)

    def test_every_linked_entity_has_one_wikidata_and_one_dbpedia_link(self) -> None:
        for entity_class in (FOOT.FootballTeam, FOOT.Season, FOOT.Competition):
            for entity in self.graph.subjects(RDF.type, entity_class):
                targets = {str(target) for target in self.graph.objects(entity, OWL.sameAs)}
                self.assertEqual(len(targets), 2, entity)
                self.assertEqual(
                    sum(target.startswith("http://www.wikidata.org/") for target in targets),
                    1,
                )

    def test_dataset_has_distribution_linksets_partitions_and_provenance(self) -> None:
        dataset = DATASET["premier-league"]
        self.assertEqual(len(set(self.graph.objects(dataset, DCAT.distribution))), 1)
        linksets = set(self.graph.objects(dataset, VOID.subset))
        self.assertEqual(len(linksets), 2)
        for linkset in linksets:
            self.assertEqual(int(self.graph.value(linkset, VOID.triples)), 46)
        self.assertEqual(len(set(self.graph.objects(dataset, VOID.classPartition))), 5)
        self.assertEqual(int(self.graph.value(dataset, VOID.triples)), len(self.graph))

        activity = self.graph.value(dataset, PROV.wasGeneratedBy)
        self.assertIn((activity, RDF.type, PROV.Activity), self.graph)
        self.assertEqual(len(set(self.graph.objects(activity, PROV.used))), 10)

    def test_conversion_reproduces_the_committed_turtle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "football-data.ttl"
            self.graph.serialize(destination=output, format="turtle")
            self.assertEqual(output.read_bytes(), DEFAULT_OUTPUT.read_bytes())
            self.assertEqual(len(Graph().parse(output, format="turtle")), len(self.graph))


class LinkEvidenceGateTests(unittest.TestCase):
    """Only verified mappings backed by passing evidence may become owl:sameAs."""

    def setUp(self) -> None:
        with DEFAULT_LINKS.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            self.fieldnames = list(reader.fieldnames or [])
            self.rows = [dict(row) for row in reader]
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        shutil.copytree(
            DEFAULT_EVIDENCE_ROOT / "data/links/evidence",
            self.root / "data/links/evidence",
        )

    def tearDown(self) -> None:
        self.directory.cleanup()

    def build_with(self, rows: list[dict[str, str]]) -> None:
        links = self.root / "links.csv"
        with links.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        build_graph(DEFAULT_INPUT_DIR, links, evidence_root=self.root)

    def test_copied_mapping_and_evidence_are_accepted(self) -> None:
        self.build_with(self.rows)

    def test_unverified_mapping_is_rejected(self) -> None:
        self.rows[0]["status"] = "candidate"
        with self.assertRaisesRegex(ConversionError, "not verified"):
            self.build_with(self.rows)

    def test_missing_or_duplicate_mapping_is_rejected(self) -> None:
        for rows in (self.rows[:-1], self.rows + [self.rows[0]]):
            with self.subTest(rows=len(rows)), self.assertRaises(ConversionError):
                self.build_with(rows)

    def test_evidence_for_another_entity_is_rejected(self) -> None:
        arsenal = next(row for row in self.rows if row["entity_id"] == "arsenal")
        arsenal["wikidata_uri"] = "http://www.wikidata.org/entity/Q18741"
        with self.assertRaisesRegex(ConversionError, "does not match"):
            self.build_with(self.rows)

    def test_failed_identity_check_is_rejected(self) -> None:
        arsenal = next(row for row in self.rows if row["entity_id"] == "arsenal")
        evidence_path = self.root / arsenal["evidence"]
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["checks"]["dbpedia_links_to_wikidata"] = False
        evidence["passed"] = False
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        with self.assertRaisesRegex(ConversionError, "failed identity check"):
            self.build_with(self.rows)

    def test_missing_evidence_file_is_rejected(self) -> None:
        (self.root / self.rows[0]["evidence"]).unlink()
        with self.assertRaisesRegex(ConversionError, "Cannot read link evidence"):
            self.build_with(self.rows)


if __name__ == "__main__":
    unittest.main()
