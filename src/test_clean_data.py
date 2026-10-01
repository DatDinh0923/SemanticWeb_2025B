import tempfile
import unittest
from pathlib import Path

from clean_data import (
    DataValidationError,
    canonical_team_name,
    clean_all,
    competition_id_for,
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

    def test_team_aliases_and_distinct_wimbledon_clubs(self) -> None:
        self.assertEqual(canonical_team_name("Manchester Utd"), "Manchester United FC")
        self.assertEqual(canonical_team_name("Hereford FC (2014-)"), "Hereford FC")
        self.assertEqual(slugify_team_name("Wimbledon FC"), "wimbledon")
        self.assertEqual(slugify_team_name("AFC Wimbledon"), "afc-wimbledon")

    def test_competition_names_follow_2004_rename(self) -> None:
        self.assertEqual(competition_id_for("eng.2", 2003), "first-division")
        self.assertEqual(competition_id_for("eng.2", 2004), "championship")
        self.assertEqual(competition_id_for("eng.cup", 2019), "fa-cup")

    def test_clean_all_merges_files_and_skips_unplayed(self) -> None:
        league = (
            "Round,Date,Team 1,FT,Team 2\n"
            "1,Fri Aug 10 2018,Manchester United FC,2-1,Leicester City FC\n"
            "2,Sat Aug 18 2018,Leicester City FC,,Manchester Utd\n"
        )
        cup = (
            "Round,Date,Team 1,FT,Team 2\n"
            "Final,Sat May 18 2019,Manchester City FC,6-0,Watford FC\n"
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "england_csv"
            season_dir = root / "2010s" / "2018-19"
            season_dir.mkdir(parents=True)
            (season_dir / "eng.1.csv").write_text(league, encoding="utf-8")
            (season_dir / "eng.cup.csv").write_text(cup, encoding="utf-8")
            output_dir = Path(temporary_directory) / "processed"

            counts = clean_all(root, output_dir)

            self.assertEqual(counts["matches"], 2)
            self.assertEqual(counts["teams"], 4)
            self.assertEqual(counts["skipped_unplayed"], 1)
            matches = (output_dir / "matches.csv").read_text(encoding="utf-8")
            self.assertIn("premier-league-2018-19", matches)
            self.assertIn("fa-cup-2018-19,Final", matches)
            teams = (output_dir / "teams.csv").read_text(encoding="utf-8")
            self.assertIn("manchester-united,Manchester United FC", teams)


if __name__ == "__main__":
    unittest.main()
