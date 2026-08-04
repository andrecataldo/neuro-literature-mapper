"""Tests for the screening-matrix validator."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "validate_screening_matrix.py"
)

SPEC = importlib.util.spec_from_file_location(
    "validate_screening_matrix",
    SCRIPT_PATH,
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        f"Unable to load script: {SCRIPT_PATH}"
    )

validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def valid_row(
    *,
    record_id: str = "NLM-TEST-001",
) -> dict[str, str]:
    """Return one valid completed screening record."""

    return {
        "record_id": record_id,
        "source_record_id": "SOURCE-001",
        "duplicate_group": "",
        "title": "A Valid Neural Language Study",
        "authors": "Researcher A; Researcher B",
        "year": "2026",
        "venue": "Journal of Neural Engineering",
        "doi": "10.1000/valid-study",
        "url": "https://example.org/valid-study",
        "abstract": (
            "This study integrates neural signals with a "
            "language model for communication."
        ),
        "abstract_available": "true",
        "suggested_priority": (
            validator.PRIORITY_LABELS["A1"]
        ),
        "adjudicated_priority": "",
        "final_priority": (
            validator.PRIORITY_LABELS["A1"]
        ),
        "screening_decision": "Include",
        "screening_reason_code": "I01",
        "screening_reason": (
            "Operational integration between neural signals "
            "and a language model."
        ),
        "screening_evidence": (
            "The abstract describes a neural-to-language "
            "generation pipeline."
        ),
        "screened_by": "Andre Cataldo",
        "screening_date": date.today().isoformat(),
        "second_review_required": "false",
        "screening_notes": "",
    }


def source_row() -> dict[str, str]:
    """Return the source-corpus counterpart of valid_row."""

    row = valid_row()

    return {
        "title": row["title"],
        "authors": row["authors"],
        "year": row["year"],
        "venue": row["venue"],
        "doi": row["doi"],
        "url": row["url"],
        "abstract": row["abstract"],
        "priority": row["final_priority"],
    }


def issue_codes(
    report: object,
) -> set[str]:
    return {
        issue.code
        for issue in report.issues
    }


class StructureTests(unittest.TestCase):
    def test_valid_structure_is_accepted(self) -> None:
        dataframe = pd.DataFrame(
            [valid_row()],
            columns=validator.REQUIRED_COLUMNS,
        )

        report = validator.ValidationReport()

        result = validator.validate_structure(
            dataframe,
            report,
        )

        self.assertTrue(result)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_missing_required_column_is_rejected(
        self,
    ) -> None:
        row = valid_row()
        row.pop("screening_decision")

        dataframe = pd.DataFrame([row])
        report = validator.ValidationReport()

        result = validator.validate_structure(
            dataframe,
            report,
        )

        self.assertFalse(result)

        self.assertIn(
            "STRUCTURE_MISSING_COLUMNS",
            issue_codes(report),
        )


class BaselineTests(unittest.TestCase):
    def test_expected_v4_3f_baseline_is_valid(
        self,
    ) -> None:
        priorities = (
            [validator.PRIORITY_LABELS["A1"]] * 71
            + [validator.PRIORITY_LABELS["A2"]] * 120
            + [validator.PRIORITY_LABELS["A3"]] * 63
        )

        dataframe = pd.DataFrame(
            {
                "final_priority": priorities,
            }
        )

        report = validator.ValidationReport()

        validator.validate_baseline(
            dataframe,
            report,
        )

        self.assertEqual(report.errors, [])

    def test_wrong_baseline_is_rejected(self) -> None:
        dataframe = pd.DataFrame(
            {
                "final_priority": [
                    validator.PRIORITY_LABELS["A1"],
                    validator.PRIORITY_LABELS["A2"],
                    validator.PRIORITY_LABELS["A3"],
                ]
            }
        )

        report = validator.ValidationReport()

        validator.validate_baseline(
            dataframe,
            report,
        )

        codes = issue_codes(report)

        self.assertIn(
            "BASELINE_TOTAL",
            codes,
        )

        self.assertIn(
            "BASELINE_PRIORITY_COUNT",
            codes,
        )


class DecisionTests(unittest.TestCase):
    def test_valid_completed_decision_is_accepted(
        self,
    ) -> None:
        dataframe = pd.DataFrame([valid_row()])
        report = validator.ValidationReport()

        validator.validate_priorities(
            dataframe,
            report,
        )

        validator.validate_booleans_and_abstracts(
            dataframe,
            report,
        )

        validator.validate_screening_decisions(
            dataframe,
            report,
        )

        self.assertEqual(report.errors, [])

    def test_incomplete_decision_is_rejected(
        self,
    ) -> None:
        row = valid_row()
        row["screening_reason"] = ""
        row["screening_evidence"] = ""

        dataframe = pd.DataFrame([row])
        report = validator.ValidationReport()

        validator.validate_screening_decisions(
            dataframe,
            report,
        )

        self.assertIn(
            "DECISION_INCOMPLETE",
            issue_codes(report),
        )

    def test_include_with_exclusion_code_is_rejected(
        self,
    ) -> None:
        row = valid_row()
        row["screening_decision"] = "Include"
        row["screening_reason_code"] = "E06"

        dataframe = pd.DataFrame([row])
        report = validator.ValidationReport()

        validator.validate_screening_decisions(
            dataframe,
            report,
        )

        self.assertIn(
            "REASON_CODE_INVALID",
            issue_codes(report),
        )

    def test_exclude_with_inclusion_code_is_rejected(
        self,
    ) -> None:
        row = valid_row()
        row["screening_decision"] = "Exclude"
        row["screening_reason_code"] = "I01"

        dataframe = pd.DataFrame([row])
        report = validator.ValidationReport()

        validator.validate_screening_decisions(
            dataframe,
            report,
        )

        self.assertIn(
            "REASON_CODE_INVALID",
            issue_codes(report),
        )

    def test_future_screening_date_is_rejected(
        self,
    ) -> None:
        row = valid_row()

        row["screening_date"] = (
            date.today()
            + timedelta(days=1)
        ).isoformat()

        dataframe = pd.DataFrame([row])
        report = validator.ValidationReport()

        validator.validate_screening_decisions(
            dataframe,
            report,
        )

        self.assertIn(
            "SCREENING_DATE_INVALID",
            issue_codes(report),
        )

    def test_uncertain_requires_second_review(
        self,
    ) -> None:
        row = valid_row()
        row["screening_decision"] = "Uncertain"
        row["screening_reason_code"] = "U01"
        row["screening_reason"] = (
            "The abstract does not provide enough detail."
        )
        row["screening_evidence"] = (
            "Operational integration could not be confirmed."
        )
        row["second_review_required"] = "false"

        dataframe = pd.DataFrame([row])
        report = validator.ValidationReport()

        validator.validate_screening_decisions(
            dataframe,
            report,
        )

        self.assertIn(
            "UNCERTAIN_REVIEW_REQUIRED",
            issue_codes(report),
        )


class AbstractAndDuplicateTests(unittest.TestCase):
    def test_abstract_flag_must_match_content(
        self,
    ) -> None:
        row = valid_row()
        row["abstract"] = ""
        row["abstract_available"] = "true"
        row["second_review_required"] = "true"

        dataframe = pd.DataFrame([row])
        report = validator.ValidationReport()

        validator.validate_booleans_and_abstracts(
            dataframe,
            report,
        )

        self.assertIn(
            "ABSTRACT_FLAG_INCONSISTENT",
            issue_codes(report),
        )

    def test_duplicate_candidate_requires_second_review(
        self,
    ) -> None:
        row = valid_row()
        row["duplicate_group"] = "DUPLICATE-001"
        row["second_review_required"] = "false"

        dataframe = pd.DataFrame([row])
        report = validator.ValidationReport()

        validator.validate_booleans_and_abstracts(
            dataframe,
            report,
        )

        self.assertIn(
            "DUPLICATE_REVIEW_REQUIRED",
            issue_codes(report),
        )

    def test_multiple_included_duplicates_generate_warning(
        self,
    ) -> None:
        first = valid_row(
            record_id="NLM-DUPLICATE-01"
        )

        second = valid_row(
            record_id="NLM-DUPLICATE-02"
        )

        first["duplicate_group"] = "DUPLICATE-001"
        second["duplicate_group"] = "DUPLICATE-001"

        first["second_review_required"] = "true"
        second["second_review_required"] = "true"

        dataframe = pd.DataFrame(
            [
                first,
                second,
            ]
        )

        report = validator.ValidationReport()

        validator.validate_duplicate_groups(
            dataframe,
            report,
        )

        self.assertIn(
            "DUPLICATE_MULTIPLE_INCLUDED",
            issue_codes(report),
        )


class SourceIntegrityTests(unittest.TestCase):
    def test_unchanged_source_fields_are_valid(
        self,
    ) -> None:
        matrix = pd.DataFrame([valid_row()])
        source = pd.DataFrame([source_row()])
        report = validator.ValidationReport()

        validator.validate_source_integrity(
            matrix,
            source,
            report,
        )

        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_changed_bibliographic_field_is_rejected(
        self,
    ) -> None:
        matrix_row = valid_row()

        matrix_row["title"] = (
            "An Accidentally Modified Study Title"
        )

        matrix = pd.DataFrame([matrix_row])
        source = pd.DataFrame([source_row()])
        report = validator.ValidationReport()

        validator.validate_source_integrity(
            matrix,
            source,
            report,
        )

        self.assertIn(
            "SOURCE_FIELD_CHANGED",
            issue_codes(report),
        )

    def test_changed_abstract_without_source_is_warning(
        self,
    ) -> None:
        matrix_row = valid_row()

        matrix_row["abstract"] = (
            "A manually recovered and modified abstract."
        )

        matrix_row["screening_notes"] = ""

        matrix = pd.DataFrame([matrix_row])
        source = pd.DataFrame([source_row()])
        report = validator.ValidationReport()

        validator.validate_source_integrity(
            matrix,
            source,
            report,
        )

        self.assertIn(
            "ABSTRACT_CHANGED_WITHOUT_SOURCE",
            issue_codes(report),
        )

    def test_changed_abstract_with_source_note_is_valid(
        self,
    ) -> None:
        matrix_row = valid_row()

        matrix_row["abstract"] = (
            "A manually recovered and modified abstract."
        )

        matrix_row["screening_notes"] = (
            "Abstract recovered from publisher page "
            f"on {date.today().isoformat()}."
        )

        matrix = pd.DataFrame([matrix_row])
        source = pd.DataFrame([source_row()])
        report = validator.ValidationReport()

        validator.validate_source_integrity(
            matrix,
            source,
            report,
        )

        self.assertNotIn(
            "ABSTRACT_CHANGED_WITHOUT_SOURCE",
            issue_codes(report),
        )


if __name__ == "__main__":
    unittest.main()
