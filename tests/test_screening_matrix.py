"""Regression tests for the screening-matrix initialization script."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import pandas as pd


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "init_screening_matrix.py"
)

SPEC = importlib.util.spec_from_file_location(
    "init_screening_matrix",
    SCRIPT_PATH,
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        f"Unable to load script: {SCRIPT_PATH}"
    )

screening = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(screening)


class CanonicalPriorityTests(unittest.TestCase):
    def test_canonical_priority_accepts_codes_and_labels(
        self,
    ) -> None:
        cases = {
            "A1": screening.PRIORITY_LABELS["A1"],
            "A1-central-integracao-llm": (
                screening.PRIORITY_LABELS["A1"]
            ),
            "A2-central-decoding-linguagem": (
                screening.PRIORITY_LABELS["A2"]
            ),
            "A3 risks": screening.PRIORITY_LABELS["A3"],
            "B-apoio": screening.PRIORITY_LABELS["B"],
            "D-descartar": screening.PRIORITY_LABELS["D"],
        }

        for raw_value, expected in cases.items():
            with self.subTest(raw_value=raw_value):
                self.assertEqual(
                    screening.canonical_priority(raw_value),
                    expected,
                )

    def test_canonical_priority_rejects_unknown_value(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            screening.canonical_priority("unknown")


class ScreeningMatrixTests(unittest.TestCase):
    def test_selects_only_central_records_and_orders_streams(
        self,
    ) -> None:
        adjudicated = pd.DataFrame(
            [
                {
                    "id": "R-A2",
                    "title": "A2 record",
                    "year": "2026",
                    "abstract": "Available abstract",
                    "priority": "A2",
                },
                {
                    "id": "R-B",
                    "title": "Supporting record",
                    "year": "2026",
                    "abstract": "Available abstract",
                    "priority": "B",
                },
                {
                    "id": "R-A3",
                    "title": "A3 record",
                    "year": "2025",
                    "abstract": "Available abstract",
                    "priority": "A3",
                },
                {
                    "id": "R-A1-AVAILABLE",
                    "title": "A1 record with abstract",
                    "year": "2026",
                    "abstract": "Available abstract",
                    "priority": "A1",
                },
                {
                    "id": "R-A1-MISSING",
                    "title": "A1 record without abstract",
                    "year": "2024",
                    "abstract": "",
                    "priority": "A1",
                },
            ]
        )

        matrix, unmatched, groups, records = (
            screening.create_screening_matrix(
                adjudicated,
                automated=None,
            )
        )

        self.assertEqual(len(matrix), 4)
        self.assertEqual(unmatched, 0)
        self.assertEqual(groups, 0)
        self.assertEqual(records, 0)

        self.assertEqual(
            matrix["record_id"].tolist(),
            [
                "R-A1-MISSING",
                "R-A1-AVAILABLE",
                "R-A3",
                "R-A2",
            ],
        )

        self.assertEqual(
            matrix["final_priority"].tolist(),
            [
                screening.PRIORITY_LABELS["A1"],
                screening.PRIORITY_LABELS["A1"],
                screening.PRIORITY_LABELS["A3"],
                screening.PRIORITY_LABELS["A2"],
            ],
        )

        self.assertEqual(
            matrix.iloc[0]["abstract_available"],
            "false",
        )

        self.assertEqual(
            matrix.iloc[0]["second_review_required"],
            "true",
        )

    def test_disambiguates_shared_record_ids(
        self,
    ) -> None:
        adjudicated = pd.DataFrame(
            [
                {
                    "id": "SHARED-ID",
                    "title": "Original publication",
                    "year": "2026",
                    "doi": "10.1000/example",
                    "abstract": "First abstract",
                    "priority": "A1",
                },
                {
                    "id": "SHARED-ID",
                    "title": "Special issue version",
                    "year": "2026",
                    "doi": "10.1000/example-special",
                    "abstract": "Second abstract",
                    "priority": "A1",
                },
            ]
        )

        matrix, unmatched, groups, records = (
            screening.create_screening_matrix(
                adjudicated,
                automated=None,
            )
        )

        self.assertEqual(unmatched, 0)
        self.assertEqual(groups, 1)
        self.assertEqual(records, 2)

        self.assertTrue(
            matrix["record_id"].is_unique
        )

        self.assertEqual(
            set(matrix["record_id"]),
            {
                "SHARED-ID-01",
                "SHARED-ID-02",
            },
        )

        self.assertEqual(
            set(matrix["source_record_id"]),
            {"SHARED-ID"},
        )

        self.assertEqual(
            set(matrix["duplicate_group"]),
            {"SHARED-ID"},
        )

        self.assertEqual(
            set(matrix["second_review_required"]),
            {"true"},
        )

        for note in matrix["screening_notes"]:
            self.assertIn(
                "Potential duplicate candidate",
                note,
            )

    def test_preserves_automated_and_adjudicated_priorities(
        self,
    ) -> None:
        adjudicated = pd.DataFrame(
            [
                {
                    "id": "R-001",
                    "title": "Operational neural language system",
                    "year": "2026",
                    "doi": "10.1000/adjudicated",
                    "abstract": "An abstract",
                    "priority": "A1",
                },
            ]
        )

        automated = pd.DataFrame(
            [
                {
                    "id": "R-001",
                    "title": "Operational neural language system",
                    "year": "2026",
                    "doi": "https://doi.org/10.1000/adjudicated",
                    "abstract": "An abstract",
                    "priority": "A2",
                },
            ]
        )

        matrix, unmatched, groups, records = (
            screening.create_screening_matrix(
                adjudicated,
                automated=automated,
            )
        )

        row = matrix.iloc[0]

        self.assertEqual(unmatched, 0)
        self.assertEqual(groups, 0)
        self.assertEqual(records, 0)

        self.assertEqual(
            row["suggested_priority"],
            screening.PRIORITY_LABELS["A2"],
        )

        self.assertEqual(
            row["adjudicated_priority"],
            screening.PRIORITY_LABELS["A1"],
        )

        self.assertEqual(
            row["final_priority"],
            screening.PRIORITY_LABELS["A1"],
        )

    def test_baseline_validation_rejects_wrong_counts(
        self,
    ) -> None:
        matrix = pd.DataFrame(
            {
                "final_priority": [
                    screening.PRIORITY_LABELS["A1"],
                    screening.PRIORITY_LABELS["A2"],
                    screening.PRIORITY_LABELS["A3"],
                ]
            }
        )

        with self.assertRaises(ValueError):
            screening.validate_baseline(matrix)


if __name__ == "__main__":
    unittest.main()
