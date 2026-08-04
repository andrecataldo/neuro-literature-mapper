"""Tests for the screening progress reporter."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "screening_progress.py"
)

SPEC = importlib.util.spec_from_file_location(
    "screening_progress",
    SCRIPT_PATH,
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        f"Unable to load script: {SCRIPT_PATH}"
    )

progress = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = progress
SPEC.loader.exec_module(progress)


def screening_row(
    *,
    record_id: str,
    priority: str = "A1",
    decision: str = "",
    abstract_available: str = "true",
    second_review_required: str = "false",
    duplicate_group: str = "",
) -> dict[str, str]:
    """Return one minimally valid screening record."""

    return {
        "record_id": record_id,
        "title": f"Study {record_id}",
        "year": "2026",
        "abstract_available": abstract_available,
        "final_priority": (
            progress.PRIORITY_LABELS[priority]
        ),
        "screening_decision": decision,
        "second_review_required": (
            second_review_required
        ),
        "duplicate_group": duplicate_group,
    }


def sample_dataframe() -> pd.DataFrame:
    """Return a matrix with mixed screening states."""

    return pd.DataFrame(
        [
            screening_row(
                record_id="NLM-001",
                priority="A1",
                decision="Include",
            ),
            screening_row(
                record_id="NLM-002",
                priority="A1",
                decision="",
                abstract_available="false",
                second_review_required="true",
                duplicate_group="DUP-A",
            ),
            screening_row(
                record_id="NLM-003",
                priority="A1",
                decision="Exclude",
                second_review_required="true",
                duplicate_group="DUP-A",
            ),
            screening_row(
                record_id="NLM-004",
                priority="A3",
                decision="Uncertain",
                abstract_available="false",
                second_review_required="true",
            ),
            screening_row(
                record_id="NLM-005",
                priority="A2",
                decision="Exclude",
                duplicate_group="DUP-B",
            ),
            screening_row(
                record_id="NLM-006",
                priority="A2",
                decision="Exclude",
                duplicate_group="DUP-B",
            ),
        ]
    )


class UtilityTests(unittest.TestCase):
    def test_clean_text_normalizes_values(self) -> None:
        self.assertEqual(
            progress.clean_text("  neural   decoding  "),
            "neural decoding",
        )

        self.assertEqual(
            progress.clean_text(None),
            "",
        )

        self.assertEqual(
            progress.clean_text(float("nan")),
            "",
        )

    def test_percentage_handles_regular_and_zero_totals(
        self,
    ) -> None:
        self.assertEqual(
            progress.percentage(1, 4),
            25.0,
        )

        self.assertEqual(
            progress.percentage(0, 0),
            0.0,
        )


class StructureTests(unittest.TestCase):
    def test_valid_minimum_structure_is_accepted(
        self,
    ) -> None:
        dataframe = pd.DataFrame(
            [
                screening_row(
                    record_id="NLM-001",
                )
            ]
        )

        progress.validate_minimum_structure(
            dataframe
        )

    def test_missing_required_column_is_rejected(
        self,
    ) -> None:
        row = screening_row(
            record_id="NLM-001"
        )

        row.pop("screening_decision")

        dataframe = pd.DataFrame([row])

        with self.assertRaisesRegex(
            ValueError,
            "Missing required columns",
        ):
            progress.validate_minimum_structure(
                dataframe
            )

    def test_duplicate_record_ids_are_rejected(
        self,
    ) -> None:
        dataframe = pd.DataFrame(
            [
                screening_row(
                    record_id="NLM-001",
                ),
                screening_row(
                    record_id="NLM-001",
                ),
            ]
        )

        with self.assertRaisesRegex(
            ValueError,
            "duplicated record_id",
        ):
            progress.validate_minimum_structure(
                dataframe
            )

    def test_invalid_decision_is_rejected(
        self,
    ) -> None:
        dataframe = pd.DataFrame(
            [
                screening_row(
                    record_id="NLM-001",
                    decision="Maybe",
                )
            ]
        )

        with self.assertRaisesRegex(
            ValueError,
            "Invalid screening_decision",
        ):
            progress.validate_minimum_structure(
                dataframe
            )

    def test_invalid_boolean_is_rejected(
        self,
    ) -> None:
        dataframe = pd.DataFrame(
            [
                screening_row(
                    record_id="NLM-001",
                    abstract_available="yes",
                )
            ]
        )

        with self.assertRaisesRegex(
            ValueError,
            "Invalid abstract_available",
        ):
            progress.validate_minimum_structure(
                dataframe
            )

    def test_invalid_priority_is_rejected(
        self,
    ) -> None:
        row = screening_row(
            record_id="NLM-001"
        )

        row["final_priority"] = "B-contextual"

        dataframe = pd.DataFrame([row])

        with self.assertRaisesRegex(
            ValueError,
            "Invalid final_priority",
        ):
            progress.validate_minimum_structure(
                dataframe
            )


class ProgressMetricTests(unittest.TestCase):
    def test_decision_counts(self) -> None:
        counts = progress.decision_counts(
            sample_dataframe()
        )

        self.assertEqual(
            counts,
            {
                "Include": 1,
                "Exclude": 3,
                "Uncertain": 1,
                "Pending": 1,
            },
        )

    def test_priority_progress(self) -> None:
        result = progress.build_priority_progress(
            sample_dataframe()
        )

        by_priority = {
            item["priority"]: item
            for item in result
        }

        self.assertEqual(
            by_priority["A1"]["total"],
            3,
        )

        self.assertEqual(
            by_priority["A1"]["completed"],
            2,
        )

        self.assertEqual(
            by_priority["A1"]["pending"],
            1,
        )

        self.assertEqual(
            by_priority["A1"]["progress_percent"],
            66.7,
        )

        self.assertEqual(
            by_priority["A3"]["uncertain"],
            1,
        )

        self.assertEqual(
            by_priority["A2"]["exclude"],
            2,
        )

    def test_abstract_progress(self) -> None:
        result = progress.build_abstract_progress(
            sample_dataframe()
        )

        self.assertEqual(
            result,
            {
                "available_total": 4,
                "missing_total": 2,
                "missing_pending": 1,
                "missing_screened": 1,
                "missing_uncertain": 1,
            },
        )

    def test_duplicate_progress_with_pending_and_ambiguous_groups(
        self,
    ) -> None:
        result = progress.build_duplicate_progress(
            sample_dataframe()
        )

        self.assertEqual(
            result,
            {
                "groups_total": 2,
                "records_total": 4,
                "groups_pending": 1,
                "groups_resolved": 0,
                "groups_ambiguous": 1,
                "records_pending": 1,
            },
        )

    def test_duplicate_group_with_one_include_is_resolved(
        self,
    ) -> None:
        dataframe = pd.DataFrame(
            [
                screening_row(
                    record_id="NLM-DUP-01",
                    decision="Include",
                    duplicate_group="DUP-001",
                ),
                screening_row(
                    record_id="NLM-DUP-02",
                    decision="Exclude",
                    duplicate_group="DUP-001",
                ),
            ]
        )

        result = progress.build_duplicate_progress(
            dataframe
        )

        self.assertEqual(
            result["groups_resolved"],
            1,
        )

        self.assertEqual(
            result["groups_pending"],
            0,
        )

        self.assertEqual(
            result["groups_ambiguous"],
            0,
        )

    def test_second_review_progress(self) -> None:
        result = (
            progress.build_second_review_progress(
                sample_dataframe()
            )
        )

        self.assertEqual(
            result,
            {
                "flagged_total": 3,
                "awaiting_initial_screening": 1,
                "screened_but_still_flagged": 2,
                "uncertain_flagged": 1,
            },
        )

    def test_complete_report(self) -> None:
        report = progress.build_report(
            sample_dataframe(),
            input_path=Path(
                "outputs/test_matrix.csv"
            ),
        )

        self.assertEqual(
            report["overall"]["total"],
            6,
        )

        self.assertEqual(
            report["overall"]["completed"],
            5,
        )

        self.assertEqual(
            report["overall"]["pending"],
            1,
        )

        self.assertEqual(
            report["overall"]["progress_percent"],
            83.3,
        )

        self.assertEqual(
            report["decisions"]["include"],
            1,
        )

        self.assertEqual(
            report["duplicates"]["groups_total"],
            2,
        )


class ExportTests(unittest.TestCase):
    def test_json_and_csv_reports_are_written(
        self,
    ) -> None:
        report = progress.build_report(
            sample_dataframe(),
            input_path=Path(
                "outputs/test_matrix.csv"
            ),
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            json_path = root / "progress.json"
            csv_path = root / "progress.csv"

            progress.write_json_report(
                json_path,
                report,
            )

            progress.write_csv_report(
                csv_path,
                report,
            )

            self.assertTrue(json_path.exists())
            self.assertTrue(csv_path.exists())

            json_data = json.loads(
                json_path.read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                json_data["overall"]["total"],
                6,
            )

            csv_data = pd.read_csv(
                csv_path,
                dtype=str,
                keep_default_na=False,
                encoding="utf-8-sig",
            )

            self.assertEqual(
                list(csv_data.columns),
                [
                    "section",
                    "group",
                    "metric",
                    "value",
                ],
            )

            self.assertIn(
                "overall",
                set(csv_data["section"]),
            )

            self.assertIn(
                "priorities",
                set(csv_data["section"]),
            )


if __name__ == "__main__":
    unittest.main()
