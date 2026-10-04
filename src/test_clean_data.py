import csv
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from clean_data import (
    DEFAULT_ALIASES,
    DEFAULT_MANIFEST,
    DEFAULT_OUTPUT_DIR,
    PROJECT_ROOT,
    DataValidationError,
    clean_dataset,
    load_aliases,
    load_manifest,
    load_matches,
    parse_score,
    parse_source_date,
    slugify_team_name,
    validate_season,
)


SOURCE_HEADER = "Round,Date,Team 1,FT,Team 2\n"
SOURCE_ROW = "1,Fri Aug 10 2018,Manchester United FC,2-1,Leicester City FC\n"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


class CleanerUnitTests(unittest.TestCase):
    def test_slugify_team_name_removes_club_abbreviations(self) -> None:
        self.assertEqual(slugify_team_name("Manchester United FC"), "manchester-united")
        self.assertEqual(slugify_team_name("AFC Bournemouth"), "bournemouth")
        self.assertEqual(
            slugify_team_name("Brighton & Hove Albion FC"),
            "brighton-and-hove-albion",
        )

    def test_parse_score_accepts_ascii_and_unicode_dashes(self) -> None:
        self.assertEqual(parse_score("2-1"), (2, 1))
        self.assertEqual(parse_score("0–3"), (0, 3))

    def test_parse_source_date_accepts_postponed_annotation(self) -> None:
        self.assertEqual(parse_source_date("Fri Aug 10 2018").isoformat(), "2018-08-10")
        self.assertEqual(
            parse_source_date("Tue Jan 12 2021(P)").isoformat(),
            "2021-01-12",
        )

    def test_parse_source_date_rejects_wrong_weekday(self) -> None:
        with self.assertRaises(DataValidationError):
            parse_source_date("Mon Aug 10 2018")


class AliasAndManifestTests(unittest.TestCase):
    def test_source_spellings_share_one_reviewed_identity(self) -> None:
        aliases = load_aliases(DEFAULT_ALIASES)
        self.assertEqual(aliases["Manchester Utd"], aliases["Manchester United FC"])
        self.assertEqual(aliases["Wolves"], aliases["Wolverhampton Wanderers FC"])
        self.assertEqual(aliases["Tottenham"].team_id, "tottenham-hotspur")
        self.assertEqual(len({team.team_id for team in aliases.values()}), 35)

    def test_alias_id_must_match_its_canonical_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "aliases.csv"
            path.write_text(
                "source_name,team_id,name\nArsenal,gunners,Arsenal FC\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(DataValidationError, "line 2"):
                load_aliases(path)

    def test_manifest_lists_ten_premier_league_seasons(self) -> None:
        sources = load_manifest(DEFAULT_MANIFEST)
        self.assertEqual(len(sources), 10)
        self.assertEqual(sources[0].season_id, "premier-league-2011-12")
        self.assertEqual(sources[-1].season_id, "premier-league-2020-21")
        for source in sources:
            self.assertTrue((PROJECT_ROOT / source.source_file).is_file())


class SourceRowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.aliases = load_aliases(DEFAULT_ALIASES)

    def load_text(self, text: str):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.csv"
            path.write_text(SOURCE_HEADER + text, encoding="utf-8")
            return load_matches(path, "premier-league", "test-season", self.aliases)

    def test_rows_keep_their_source_line(self) -> None:
        matches = self.load_text(SOURCE_ROW)
        self.assertEqual(matches[0].match_id, "2018-08-10-manchester-united-leicester-city")
        self.assertEqual(matches[0].source_line, 2)

    def test_bad_rows_are_reported_with_file_and_line(self) -> None:
        for text in (
            SOURCE_ROW.replace("2-1", ""),
            SOURCE_ROW.replace("Manchester United FC", "Unknown Town FC"),
            SOURCE_ROW + SOURCE_ROW,
            SOURCE_ROW.replace("Leicester City FC", "Manchester Utd"),
        ):
            with self.subTest(text=text):
                with self.assertRaisesRegex(DataValidationError, r"source.csv: line [23]"):
                    self.load_text(text)


class SeasonIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        aliases = load_aliases(DEFAULT_ALIASES)
        cls.matches = load_matches(
            PROJECT_ROOT / "england_csv/2010s/2018-19/eng.1.csv",
            "premier-league",
            "premier-league-2018-19",
            aliases,
        )

    def test_complete_season_is_a_double_round_robin(self) -> None:
        self.assertEqual(len(validate_season(self.matches, 380, 20)), 20)

    def test_missing_match_is_rejected(self) -> None:
        with self.assertRaises(DataValidationError):
            validate_season(self.matches[:-1], 380, 20)

    def test_repeated_fixture_is_rejected(self) -> None:
        corrupt = list(self.matches[:-1]) + [
            replace(self.matches[0], match_id="replayed", round=38)
        ]
        with self.assertRaisesRegex(DataValidationError, "Duplicate home/away"):
            validate_season(corrupt, 380, 20)

    def test_moved_round_is_rejected(self) -> None:
        corrupt = [replace(self.matches[0], round=2)] + list(self.matches[1:])
        with self.assertRaisesRegex(DataValidationError, "wrong match count"):
            validate_season(corrupt, 380, 20)


class FullCleanTests(unittest.TestCase):
    def test_cleaning_reproduces_the_committed_tables(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            counts = clean_dataset(
                manifest_path=DEFAULT_MANIFEST,
                aliases_path=DEFAULT_ALIASES,
                output_dir=output_dir,
                competition_id="premier-league",
                competition_name="English Premier League",
                country="England",
                tier=1,
            )
            self.assertEqual(counts, (3800, 35, 10))
            for name in ("matches.csv", "teams.csv", "competitions.csv", "seasons.csv"):
                with self.subTest(table=name):
                    self.assertEqual(
                        (output_dir / name).read_bytes(),
                        (DEFAULT_OUTPUT_DIR / name).read_bytes(),
                    )

            matches = read_rows(output_dir / "matches.csv")
            self.assertEqual(len({row["match_id"] for row in matches}), 3800)
            for row in matches:
                self.assertTrue((PROJECT_ROOT / row["source_file"]).is_file())
                self.assertGreaterEqual(int(row["source_line"]), 2)


if __name__ == "__main__":
    unittest.main()
