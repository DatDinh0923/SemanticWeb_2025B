import tempfile
import unittest
from pathlib import Path

from suggest_links import (
    LocalEntity,
    SuggestionError,
    VERIFIED_LINKS,
    collect_suggestions,
    write_suggestions,
)


class LinkSuggestionTests(unittest.TestCase):
    def test_candidates_are_marked_unverified(self) -> None:
        def fake_search(
            label: str, limit: int, timeout: float
        ) -> list[dict[str, str]]:
            self.assertEqual(label, "Arsenal")
            self.assertEqual(limit, 2)
            self.assertEqual(timeout, 5.0)
            return [
                {
                    "id": "Q9617",
                    "label": "Arsenal F.C.",
                    "description": "association football club in London",
                }
            ]

        rows = collect_suggestions(
            [LocalEntity("team", "arsenal", "Arsenal")],
            limit=2,
            timeout=5.0,
            searcher=fake_search,
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["wikidata_uri"], "http://www.wikidata.org/entity/Q9617")
        self.assertEqual(rows[0]["verification_status"], "unverified")

    def test_verified_mapping_file_can_never_be_overwritten(self) -> None:
        with self.assertRaises(SuggestionError):
            write_suggestions(VERIFIED_LINKS, [], force=True)

    def test_existing_suggestion_file_requires_force(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "suggestions.csv"
            output.write_text("existing\n", encoding="utf-8")
            with self.assertRaises(SuggestionError):
                write_suggestions(output, [], force=False)


if __name__ == "__main__":
    unittest.main()
