"""Tests for the screening-results exporter."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "export_screening_results.py"
)

SPEC = importlib.util.spec_from_file_location(
    "export_screening_results",
    SCRIPT_PATH,
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        f"Unable to load script: {SCRIPT_PATH}"
    )

exporter = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = exporter
SPEC.loader.exec_module(exporter)


PRIORITY_LABELS = {
    "A1": "A1-central-integracao-llm",
    "A2": "A2-central-decoding-linguagem",
    "A3": "A3-central-riscos-governanca",
}


def screening_row(
    *,
    record_id: str,
    decision: str = "",
    priority: str = "A1",
    title: str | None = None,
    abstract_available: str = "true",
    second_review_required: str | None = None,
) -> dict[str, str]:
    """Return one synthetic screening-matrix record."""

    reason_codes = {
        "Include": "I01",
        "Exclude": "E01",
        "Uncertain": "U01",
    }

    completed = decision != ""

    if second_review_required is None:
        second_review_required = (
            "true"
            if decision == "Uncertain"
            else "false"
        )

    return {
        "record_id": record_id,
        "source_record_id": (
            f"SOURCE-{record_id}"
        ),
        "duplicate_group": "",
        "title": title or f"Study {record_id}",
        "authors": "Researcher A; Researcher B",
        "year": "2026",
        "venue": "Synthetic Research Venue",
        "doi": f"10.1000/{record_id.lower()}",
        "url": (
            "https://example.org/"
            f"{record_id.lower()}"
        ),
        "abstract": (
            "Synthetic abstract describing a study "
            "used only for automated testing."
        ),
        "abstract_available": abstract_available,
        "suggested_priority": (
            PRIORITY_LABELS[priority]
        ),
        "adjudicated_priority": "",
        "final_priority": (
            PRIORITY_LABELS[priority]
        ),
        "screening_decision": decision,
        "screening_reason_code": (
            reason_codes.get(decision, "")
        ),
        "screening_reason": (
            f"Synthetic {decision.lower()} reason."
            if completed
            else ""
        ),
        "screening_evidence": (
            "Synthetic evidence supporting the decision."
            if completed
            else ""
        ),
        "screened_by": (
            "Andre Cataldo"
            if completed
            else ""
        ),
        "screening_date": (
            "2026-08-04"
            if completed
            else ""
        ),
        "second_review_required": (
            second_review_required
        ),
        "screening_notes": "",
    }


def incomplete_dataframe() -> pd.DataFrame:
    """Return a matrix containing completed and pending records."""

    return pd.DataFrame(
        [
            screening_row(
                record_id="NLM-001",
                decision="Include",
                priority="A1",
            ),
            screening_row(
                record_id="NLM-002",
                decision="Exclude",
                priority="A1",
            ),
            screening_row(
                record_id="NLM-003",
                decision="Uncertain",
                priority="A3",
            ),
            screening_row(
                record_id="NLM-004",
                decision="",
                priority="A2",
            ),
            screening_row(
                record_id="NLM-005",
                decision="",
                priority="A2",
            ),
        ],
        columns=exporter.REQUIRED_COLUMNS,
    )


def complete_dataframe() -> pd.DataFrame:
    """Return a matrix without pending records."""

    return pd.DataFrame(
        [
            screening_row(
                record_id="NLM-101",
                decision="Include",
                priority="A1",
            ),
            screening_row(
                record_id="NLM-102",
                decision="Include",
                priority="A2",
            ),
            screening_row(
                record_id="NLM-103",
                decision="Exclude",
                priority="A2",
            ),
            screening_row(
                record_id="NLM-104",
                decision="Uncertain",
                priority="A3",
            ),
        ],
        columns=exporter.REQUIRED_COLUMNS,
    )


def write_matrix(
    dataframe: pd.DataFrame,
    path: Path,
) -> None:
    """Write a synthetic matrix using the project encoding."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        path,
        index=False,
        encoding="utf-8-sig",
        lineterminator="\n",
    )


def read_csv(path: Path) -> pd.DataFrame:
    """Read one generated synthetic CSV."""

    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )


def silent_export(
    dataframe: pd.DataFrame,
    *,
    input_path: Path,
    output_dir: Path,
    label: str = "test",
    force: bool = False,
    dry_run: bool = False,
    require_complete: bool = False,
) -> dict[str, object]:
    """Execute export_results without printing its report."""

    output = io.StringIO()

    with redirect_stdout(output):
        return exporter.export_results(
            dataframe,
            input_path=input_path,
            output_dir=output_dir,
            label=label,
            force=force,
            dry_run=dry_run,
            require_complete=require_complete,
        )


class LabelTests(unittest.TestCase):
    def test_valid_label_is_accepted(self) -> None:
        self.assertEqual(
            exporter.validate_label("v4_3f-test.1"),
            "v4_3f-test.1",
        )

    def test_empty_label_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "cannot be empty",
        ):
            exporter.validate_label("   ")

    def test_unsafe_labels_are_rejected(self) -> None:
        invalid_labels = [
            "v4 3f",
            "../v4_3f",
            "v4/3f",
            "v4\\3f",
            "v4:3f",
        ]

        for label in invalid_labels:
            with self.subTest(label=label):
                with self.assertRaisesRegex(
                    ValueError,
                    "may contain only",
                ):
                    exporter.validate_label(label)


class MatrixValidationTests(unittest.TestCase):
    def test_valid_matrix_is_accepted(self) -> None:
        exporter.validate_matrix(
            incomplete_dataframe()
        )

    def test_missing_required_column_is_rejected(
        self,
    ) -> None:
        dataframe = incomplete_dataframe().drop(
            columns=["screening_decision"]
        )

        with self.assertRaisesRegex(
            ValueError,
            "Missing required columns",
        ):
            exporter.validate_matrix(dataframe)

    def test_blank_record_id_is_rejected(self) -> None:
        dataframe = incomplete_dataframe()
        dataframe.loc[0, "record_id"] = ""

        with self.assertRaisesRegex(
            ValueError,
            "blank record_id",
        ):
            exporter.validate_matrix(dataframe)

    def test_duplicate_record_id_is_rejected(
        self,
    ) -> None:
        dataframe = incomplete_dataframe()
        dataframe.loc[1, "record_id"] = "NLM-001"

        with self.assertRaisesRegex(
            ValueError,
            "duplicated record_id",
        ):
            exporter.validate_matrix(dataframe)

    def test_invalid_decision_is_rejected(self) -> None:
        dataframe = incomplete_dataframe()
        dataframe.loc[
            0,
            "screening_decision",
        ] = "Maybe"

        with self.assertRaisesRegex(
            ValueError,
            "Invalid screening_decision",
        ):
            exporter.validate_matrix(dataframe)

    def test_incomplete_completed_decision_is_rejected(
        self,
    ) -> None:
        dataframe = incomplete_dataframe()
        dataframe.loc[
            0,
            "screening_reason",
        ] = ""

        with self.assertRaisesRegex(
            ValueError,
            "blank screening_reason",
        ):
            exporter.validate_matrix(dataframe)

    def test_invalid_abstract_boolean_is_rejected(
        self,
    ) -> None:
        dataframe = incomplete_dataframe()
        dataframe.loc[
            0,
            "abstract_available",
        ] = "yes"

        with self.assertRaisesRegex(
            ValueError,
            "Invalid abstract_available",
        ):
            exporter.validate_matrix(dataframe)

    def test_invalid_second_review_boolean_is_rejected(
        self,
    ) -> None:
        dataframe = incomplete_dataframe()
        dataframe.loc[
            0,
            "second_review_required",
        ] = "no"

        with self.assertRaisesRegex(
            ValueError,
            "Invalid second_review_required",
        ):
            exporter.validate_matrix(dataframe)


class SubsetTests(unittest.TestCase):
    def test_subsets_and_counts_are_correct(
        self,
    ) -> None:
        dataframe = incomplete_dataframe()

        subsets = exporter.build_subsets(
            dataframe
        )

        counts = exporter.build_counts(
            dataframe,
            subsets,
        )

        self.assertEqual(
            counts,
            {
                "total": 5,
                "completed": 3,
                "include": 1,
                "exclude": 1,
                "uncertain": 1,
                "pending": 2,
                "full_text": 2,
            },
        )

        self.assertEqual(
            list(
                subsets["full_text"][
                    "record_id"
                ]
            ),
            [
                "NLM-001",
                "NLM-003",
            ],
        )

    def test_completed_matrix_path_depends_on_completion(
        self,
    ) -> None:
        incomplete_paths = exporter.output_paths(
            Path("outputs"),
            "test",
            complete=False,
        )

        complete_paths = exporter.output_paths(
            Path("outputs"),
            "test",
            complete=True,
        )

        self.assertNotIn(
            "completed_matrix",
            incomplete_paths,
        )

        self.assertIn(
            "completed_matrix",
            complete_paths,
        )


class ExportTests(unittest.TestCase):
    def test_dry_run_does_not_write_files(
        self,
    ) -> None:
        dataframe = incomplete_dataframe()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "matrix.csv"
            output_dir = root / "exports"

            write_matrix(
                dataframe,
                input_path,
            )

            result = silent_export(
                dataframe,
                input_path=input_path,
                output_dir=output_dir,
                dry_run=True,
            )

            self.assertEqual(
                result["counts"]["pending"],
                2,
            )

            self.assertFalse(
                output_dir.exists()
            )

    def test_require_complete_rejects_pending_records(
        self,
    ) -> None:
        dataframe = incomplete_dataframe()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "matrix.csv"

            write_matrix(
                dataframe,
                input_path,
            )

            with self.assertRaisesRegex(
                ValueError,
                "2 pending records remain",
            ):
                silent_export(
                    dataframe,
                    input_path=input_path,
                    output_dir=root / "exports",
                    dry_run=True,
                    require_complete=True,
                )

    def test_incomplete_export_writes_expected_files(
        self,
    ) -> None:
        dataframe = incomplete_dataframe()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "matrix.csv"
            output_dir = root / "exports"

            write_matrix(
                dataframe,
                input_path,
            )

            result = silent_export(
                dataframe,
                input_path=input_path,
                output_dir=output_dir,
            )

            paths = result["paths"]

            expected_keys = {
                "include",
                "exclude",
                "uncertain",
                "pending",
                "full_text",
                "manifest",
            }

            self.assertEqual(
                set(paths),
                expected_keys,
            )

            for path in paths.values():
                self.assertTrue(path.exists())

            self.assertNotIn(
                "completed_matrix",
                paths,
            )

            self.assertEqual(
                len(read_csv(paths["include"])),
                1,
            )

            self.assertEqual(
                len(read_csv(paths["exclude"])),
                1,
            )

            self.assertEqual(
                len(read_csv(paths["uncertain"])),
                1,
            )

            self.assertEqual(
                len(read_csv(paths["pending"])),
                2,
            )

            self.assertEqual(
                len(read_csv(paths["full_text"])),
                2,
            )

            manifest = json.loads(
                paths["manifest"].read_text(
                    encoding="utf-8"
                )
            )

            self.assertFalse(
                manifest["screening_complete"]
            )

            self.assertEqual(
                manifest["counts"]["pending"],
                2,
            )

            self.assertEqual(
                set(manifest["outputs"]),
                {
                    "include",
                    "exclude",
                    "uncertain",
                    "pending",
                    "full_text",
                },
            )

    def test_complete_export_writes_completed_snapshot(
        self,
    ) -> None:
        dataframe = complete_dataframe()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "matrix.csv"
            output_dir = root / "exports"

            write_matrix(
                dataframe,
                input_path,
            )

            result = silent_export(
                dataframe,
                input_path=input_path,
                output_dir=output_dir,
                require_complete=True,
            )

            self.assertTrue(
                result["complete"]
            )

            self.assertEqual(
                result["counts"],
                {
                    "total": 4,
                    "completed": 4,
                    "include": 2,
                    "exclude": 1,
                    "uncertain": 1,
                    "pending": 0,
                    "full_text": 3,
                },
            )

            completed_path = result[
                "paths"
            ]["completed_matrix"]

            self.assertTrue(
                completed_path.exists()
            )

            completed = read_csv(
                completed_path
            )

            pd.testing.assert_frame_equal(
                completed.reset_index(drop=True),
                dataframe.reset_index(drop=True),
                check_dtype=False,
            )

            full_text = read_csv(
                result["paths"]["full_text"]
            )

            self.assertEqual(
                set(
                    full_text[
                        "screening_decision"
                    ]
                ),
                {
                    "Include",
                    "Uncertain",
                },
            )

            manifest = json.loads(
                result["paths"][
                    "manifest"
                ].read_text(
                    encoding="utf-8"
                )
            )

            self.assertTrue(
                manifest["screening_complete"]
            )

            self.assertIn(
                "completed_matrix",
                manifest["outputs"],
            )

    def test_existing_outputs_are_protected(
        self,
    ) -> None:
        dataframe = incomplete_dataframe()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "matrix.csv"
            output_dir = root / "exports"

            write_matrix(
                dataframe,
                input_path,
            )

            silent_export(
                dataframe,
                input_path=input_path,
                output_dir=output_dir,
            )

            with self.assertRaisesRegex(
                FileExistsError,
                "Output files already exist",
            ):
                silent_export(
                    dataframe,
                    input_path=input_path,
                    output_dir=output_dir,
                )

    def test_force_overwrites_existing_outputs(
        self,
    ) -> None:
        dataframe = incomplete_dataframe()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "matrix.csv"
            output_dir = root / "exports"

            write_matrix(
                dataframe,
                input_path,
            )

            first = silent_export(
                dataframe,
                input_path=input_path,
                output_dir=output_dir,
            )

            changed = dataframe.copy()

            changed.loc[
                changed["record_id"] == "NLM-001",
                "title",
            ] = "Updated synthetic title"

            write_matrix(
                changed,
                input_path,
            )

            second = silent_export(
                changed,
                input_path=input_path,
                output_dir=output_dir,
                force=True,
            )

            first_path = first[
                "paths"
            ]["include"]

            second_path = second[
                "paths"
            ]["include"]

            self.assertEqual(
                first_path,
                second_path,
            )

            included = read_csv(
                second_path
            )

            self.assertEqual(
                included.loc[0, "title"],
                "Updated synthetic title",
            )

    def test_input_checksum_is_preserved(
        self,
    ) -> None:
        dataframe = complete_dataframe()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "matrix.csv"
            output_dir = root / "exports"

            write_matrix(
                dataframe,
                input_path,
            )

            checksum_before = (
                exporter.sha256_file(
                    input_path
                )
            )

            result = silent_export(
                dataframe,
                input_path=input_path,
                output_dir=output_dir,
            )

            checksum_after = (
                exporter.sha256_file(
                    input_path
                )
            )

            self.assertEqual(
                checksum_before,
                checksum_after,
            )

            manifest = json.loads(
                result["paths"][
                    "manifest"
                ].read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                manifest["input"]["sha256"],
                checksum_before,
            )

            for metadata in (
                manifest["outputs"].values()
            ):
                path = Path(
                    metadata["path"]
                )

                self.assertEqual(
                    metadata["sha256"],
                    exporter.sha256_file(
                        path
                    ),
                )


if __name__ == "__main__":
    unittest.main()
