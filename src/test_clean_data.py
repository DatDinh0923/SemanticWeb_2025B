import tempfile
import unittest
from pathlib import Path

from clean_data import (
    DataValidationError,
    clean_dataset,
    parse_score,
    parse_source_date,
    slugify_team_name,
)


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

    def test_clean_dataset_writes_normalized_entity_tables(self) -> None:
        source = (
            "Round,Date,Team 1,FT,Team 2\n"
            "1,Fri Aug 10 2018,Manchester United FC,2-1,Leicester City FC\n"
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            input_path = directory / "source.csv"
            output_dir = directory / "processed"
            input_path.write_text(source, encoding="utf-8")

            counts = clean_dataset(
                input_path=input_path,
                output_dir=output_dir,
                competition_id="premier-league",
                competition_name="English Premier League",
                country="England",
                competition_type="league",
                tier=1,
                season_id="2018-19",
                season_label="2018/19",
                expected_matches=1,
                expected_teams=2,
            )

            self.assertEqual(counts, (1, 2))
            matches = (output_dir / "matches.csv").read_text(encoding="utf-8")
            self.assertIn("2018-08-10-manchester-united-leicester-city", matches)
            self.assertIn("2018-08-10", matches)
            self.assertTrue((output_dir / "teams.csv").is_file())
            self.assertTrue((output_dir / "competitions.csv").is_file())
            self.assertTrue((output_dir / "seasons.csv").is_file())
            competitions = (output_dir / "competitions.csv").read_text(
                encoding="utf-8"
            )
            self.assertIn("competition_type,tier", competitions)
            self.assertIn("league,1", competitions)


if __name__ == "__main__":
    unittest.main()
