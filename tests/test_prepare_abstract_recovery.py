"""Tests for abstract-recovery queue preparation."""

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
    / "prepare_abstract_recovery.py"
)

SPEC = importlib.util.spec_from_file_location(
    "prepare_abstract_recovery",
    SCRIPT_PATH,
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        f"Unable to load script: {SCRIPT_PATH}"
    )

recovery = importlib.util.module_from_spec(
    SPEC
)

sys.modules[SPEC.name] = recovery
SPEC.loader.exec_module(recovery)


PRIORITY_LABELS = {
    "A1": "A1-central-integracao-llm",
    "A2": "A2-central-decoding-linguagem",
    "A3": "A3-central-riscos-governanca",
}


def screening_row(
    *,
    record_id: str,
    priority: str = "A1",
    abstract: str = (
        "Synthetic abstract available for testing."
    ),
    abstract_available: str | None = None,
    second_review_required: str | None = None,
    duplicate_group: str = "",
) -> dict[str, str]:
    """Create one synthetic screening record."""

    missing = recovery.abstract_is_missing(
        abstract
    )

    if abstract_available is None:
        abstract_available = (
            "false"
            if missing
            else "true"
        )

    if second_review_required is None:
        second_review_required = (
            "true"
            if missing or duplicate_group
            else "false"
        )

    return {
        "record_id": record_id,
        "source_record_id": (
            f"SOURCE-{record_id}"
        ),
        "duplicate_group": duplicate_group,
        "title": f"Study {record_id}",
        "authors": "Researcher A; Researcher B",
        "year": "2026",
        "venue": "Synthetic Research Venue",
        "doi": f"10.1000/{record_id.lower()}",
        "url": (
            "https://example.org/"
            f"{record_id.lower()}"
        ),
        "abstract": abstract,
        "abstract_available": (
            abstract_available
        ),
        "suggested_priority": (
            PRIORITY_LABELS[priority]
        ),
        "adjudicated_priority": "",
        "final_priority": (
            PRIORITY_LABELS[priority]
        ),
        "screening_decision": "",
        "screening_reason_code": "",
        "screening_reason": "",
        "screening_evidence": "",
        "screened_by": "",
        "screening_date": "",
        "second_review_required": (
            second_review_required
        ),
        "screening_notes": "",
    }


def synthetic_matrix() -> pd.DataFrame:
    """Create a valid matrix with two missing abstracts."""

    return pd.DataFrame(
        [
            screening_row(
                record_id="NLM-001",
                priority="A1",
            ),
            screening_row(
                record_id="NLM-002",
                priority="A1",
                abstract="",
                duplicate_group="DUP-01",
            ),
            screening_row(
                record_id="NLM-003",
                priority="A3",
                abstract="No abstract available",
            ),
            screening_row(
                record_id="NLM-004",
                priority="A2",
            ),
        ],
        columns=recovery.REQUIRED_COLUMNS,
    )


def write_matrix(
    dataframe: pd.DataFrame,
    path: Path,
) -> None:
    """Write a synthetic screening matrix."""

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
    """Read one generated CSV artifact."""

    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )


def silent_prepare(
    dataframe: pd.DataFrame,
    *,
    input_path: Path,
    output_dir: Path,
    label: str = "test",
    expected_missing: int | None = 2,
    force: bool = False,
    dry_run: bool = False,
) -> dict[str, object]:
    """Run preparation without printing its summary."""

    output = io.StringIO()

    with redirect_stdout(output):
        return recovery.prepare_recovery(
            dataframe,
            input_path=input_path,
            output_dir=output_dir,
            label=label,
            expected_missing=expected_missing,
            force=force,
            dry_run=dry_run,
        )


class UtilityTests(unittest.TestCase):
    def test_clean_text_normalizes_whitespace(
        self,
    ) -> None:
        self.assertEqual(
            recovery.clean_text(
                "  Synthetic   abstract \n text  "
            ),
            "Synthetic abstract text",
        )

        self.assertEqual(
            recovery.clean_text(float("nan")),
            "",
        )

    def test_validate_label_accepts_safe_value(
        self,
    ) -> None:
        self.assertEqual(
            recovery.validate_label(
                " v4_3f-recovery.01 "
            ),
            "v4_3f-recovery.01",
        )

    def test_validate_label_rejects_unsafe_values(
        self,
    ) -> None:
        invalid_values = [
            "",
            "recovery 01",
            "../recovery",
            "recovery/01",
            "recovery\\01",
            "recovery:01",
        ]

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(
                    ValueError
                ):
                    recovery.validate_label(
                        value
                    )

    def test_abstract_missing_markers(
        self,
    ) -> None:
        missing_values = [
            "",
            None,
            float("nan"),
            "N/A",
            "none",
            "No abstract available",
            "sem resumo",
            "Resumo indisponível",
        ]

        for value in missing_values:
            with self.subTest(value=value):
                self.assertTrue(
                    recovery.abstract_is_missing(
                        value
                    )
                )

        self.assertFalse(
            recovery.abstract_is_missing(
                "A valid scientific abstract."
            )
        )

    def test_output_paths_use_label(
        self,
    ) -> None:
        paths = recovery.output_paths(
            Path("generated"),
            "v4_3f_test",
        )

        self.assertEqual(
            paths["queue"],
            Path(
                "generated/"
                "matriz_recuperacao_resumos_"
                "v4_3f_test.csv"
            ),
        )

        self.assertEqual(
            paths["manifest"],
            Path(
                "generated/"
                "manifesto_preparacao_recuperacao_"
                "resumos_v4_3f_test.json"
            ),
        )


class MatrixValidationTests(
    unittest.TestCase
):
    def test_valid_matrix_is_accepted(
        self,
    ) -> None:
        recovery.validate_matrix(
            synthetic_matrix(),
            expected_missing=2,
        )

    def test_missing_required_column_is_rejected(
        self,
    ) -> None:
        dataframe = synthetic_matrix().drop(
            columns=["abstract_available"]
        )

        with self.assertRaisesRegex(
            ValueError,
            "Missing required columns",
        ):
            recovery.validate_matrix(
                dataframe,
                expected_missing=2,
            )

    def test_blank_record_id_is_rejected(
        self,
    ) -> None:
        dataframe = synthetic_matrix()

        dataframe.loc[
            0,
            "record_id",
        ] = ""

        with self.assertRaisesRegex(
            ValueError,
            "blank record_id",
        ):
            recovery.validate_matrix(
                dataframe,
                expected_missing=2,
            )

    def test_duplicate_record_id_is_rejected(
        self,
    ) -> None:
        dataframe = synthetic_matrix()

        dataframe.loc[
            1,
            "record_id",
        ] = "NLM-001"

        with self.assertRaisesRegex(
            ValueError,
            "duplicated record_id",
        ):
            recovery.validate_matrix(
                dataframe,
                expected_missing=2,
            )

    def test_invalid_abstract_boolean_is_rejected(
        self,
    ) -> None:
        dataframe = synthetic_matrix()

        dataframe.loc[
            0,
            "abstract_available",
        ] = "yes"

        with self.assertRaisesRegex(
            ValueError,
            "Invalid abstract_available",
        ):
            recovery.validate_matrix(
                dataframe,
                expected_missing=2,
            )

    def test_invalid_second_review_boolean_is_rejected(
        self,
    ) -> None:
        dataframe = synthetic_matrix()

        dataframe.loc[
            0,
            "second_review_required",
        ] = "yes"

        with self.assertRaisesRegex(
            ValueError,
            "Invalid second_review_required",
        ):
            recovery.validate_matrix(
                dataframe,
                expected_missing=2,
            )

    def test_abstract_flag_must_match_content(
        self,
    ) -> None:
        dataframe = synthetic_matrix()

        dataframe.loc[
            1,
            "abstract_available",
        ] = "true"

        with self.assertRaisesRegex(
            ValueError,
            "does not match abstract content",
        ):
            recovery.validate_matrix(
                dataframe,
                expected_missing=2,
            )

    def test_missing_abstract_requires_second_review(
        self,
    ) -> None:
        dataframe = synthetic_matrix()

        dataframe.loc[
            1,
            "second_review_required",
        ] = "false"

        with self.assertRaisesRegex(
            ValueError,
            "must require second review",
        ):
            recovery.validate_matrix(
                dataframe,
                expected_missing=2,
            )

    def test_unexpected_missing_count_is_rejected(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Unexpected missing-abstract count",
        ):
            recovery.validate_matrix(
                synthetic_matrix(),
                expected_missing=40,
            )

    def test_expected_count_can_be_disabled(
        self,
    ) -> None:
        recovery.validate_matrix(
            synthetic_matrix(),
            expected_missing=None,
        )


class RecoveryQueueTests(
    unittest.TestCase
):
    def test_build_queue_selects_missing_records_in_order(
        self,
    ) -> None:
        queue = recovery.build_recovery_queue(
            synthetic_matrix()
        )

        self.assertEqual(
            queue["record_id"].tolist(),
            [
                "NLM-002",
                "NLM-003",
            ],
        )

        self.assertEqual(
            queue["matrix_row"].tolist(),
            [
                "3",
                "4",
            ],
        )

        self.assertEqual(
            queue["original_abstract_available"].tolist(),
            [
                "false",
                "false",
            ],
        )

    def test_new_queue_fields_start_empty_and_pending(
        self,
    ) -> None:
        queue = recovery.build_recovery_queue(
            synthetic_matrix()
        )

        self.assertTrue(
            queue["recovery_status"]
            .eq("Pending")
            .all()
        )

        editable_fields = [
            "recovery_source_type",
            "recovery_source_name",
            "recovery_source_url",
            "recovery_date",
            "recovered_by",
            "recovered_abstract",
            "recovery_notes",
        ]

        for field in editable_fields:
            with self.subTest(field=field):
                self.assertTrue(
                    queue[field].eq("").all()
                )

    def test_priority_counts(
        self,
    ) -> None:
        queue = recovery.build_recovery_queue(
            synthetic_matrix()
        )

        self.assertEqual(
            recovery.priority_counts(
                queue
            ),
            {
                PRIORITY_LABELS["A1"]: 1,
                PRIORITY_LABELS["A3"]: 1,
            },
        )

    def test_queue_schema_is_validated(
        self,
    ) -> None:
        queue = recovery.build_recovery_queue(
            synthetic_matrix()
        ).drop(
            columns=["recovery_status"]
        )

        with self.assertRaisesRegex(
            ValueError,
            "columns do not match",
        ):
            recovery.validate_recovery_queue(
                queue
            )

    def test_invalid_recovery_status_is_rejected(
        self,
    ) -> None:
        queue = recovery.build_recovery_queue(
            synthetic_matrix()
        )

        queue.loc[
            0,
            "recovery_status",
        ] = "Unknown"

        with self.assertRaisesRegex(
            ValueError,
            "Invalid recovery_status",
        ):
            recovery.validate_recovery_queue(
                queue
            )

    def test_valid_non_pending_status_is_rejected_for_new_queue(
        self,
    ) -> None:
        queue = recovery.build_recovery_queue(
            synthetic_matrix()
        )

        queue.loc[
            0,
            "recovery_status",
        ] = "In progress"

        with self.assertRaisesRegex(
            ValueError,
            "start entirely as Pending",
        ):
            recovery.validate_recovery_queue(
                queue
            )

    def test_duplicate_queue_ids_are_rejected(
        self,
    ) -> None:
        queue = recovery.build_recovery_queue(
            synthetic_matrix()
        )

        queue.loc[
            1,
            "record_id",
        ] = queue.loc[
            0,
            "record_id",
        ]

        with self.assertRaisesRegex(
            ValueError,
            "duplicated record_id",
        ):
            recovery.validate_recovery_queue(
                queue
            )


class PreparationTests(unittest.TestCase):
    def test_dry_run_does_not_write_files(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "matrix.csv"
            output_dir = root / "artifacts"

            dataframe = synthetic_matrix()

            write_matrix(
                dataframe,
                input_path,
            )

            result = silent_prepare(
                dataframe,
                input_path=input_path,
                output_dir=output_dir,
                dry_run=True,
            )

            self.assertEqual(
                len(result["queue"]),
                2,
            )

            self.assertFalse(
                output_dir.exists()
            )

    def test_artifacts_and_manifest_are_written(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "matrix.csv"
            output_dir = root / "artifacts"

            dataframe = synthetic_matrix()

            write_matrix(
                dataframe,
                input_path,
            )

            result = silent_prepare(
                dataframe,
                input_path=input_path,
                output_dir=output_dir,
                label="synthetic",
            )

            queue_path = result[
                "paths"
            ]["queue"]

            manifest_path = result[
                "paths"
            ]["manifest"]

            self.assertTrue(
                queue_path.exists()
            )

            self.assertTrue(
                manifest_path.exists()
            )

            queue = read_csv(
                queue_path
            )

            manifest = json.loads(
                manifest_path.read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                list(queue.columns),
                recovery.RECOVERY_COLUMNS,
            )

            self.assertEqual(
                len(queue),
                2,
            )

            self.assertEqual(
                manifest["schema_version"],
                1,
            )

            self.assertEqual(
                manifest["input"]["rows"],
                4,
            )

            self.assertEqual(
                manifest["counts"][
                    "missing_abstracts"
                ],
                2,
            )

            self.assertEqual(
                manifest["counts"][
                    "pending_recovery"
                ],
                2,
            )

            self.assertEqual(
                manifest["counts"][
                    "duplicate_candidates"
                ],
                1,
            )

            self.assertEqual(
                manifest["queue"]["rows"],
                2,
            )

            self.assertEqual(
                manifest["queue"]["columns"],
                len(
                    recovery.RECOVERY_COLUMNS
                ),
            )

            self.assertEqual(
                Path(
                    manifest["queue"]["path"]
                ),
                queue_path,
            )

            self.assertEqual(
                manifest["queue"]["sha256"],
                recovery.sha256_file(
                    queue_path
                ),
            )

    def test_existing_outputs_are_protected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "matrix.csv"
            output_dir = root / "artifacts"

            dataframe = synthetic_matrix()

            write_matrix(
                dataframe,
                input_path,
            )

            silent_prepare(
                dataframe,
                input_path=input_path,
                output_dir=output_dir,
            )

            with self.assertRaisesRegex(
                FileExistsError,
                "already exist",
            ):
                silent_prepare(
                    dataframe,
                    input_path=input_path,
                    output_dir=output_dir,
                )

    def test_force_overwrites_existing_outputs(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "matrix.csv"
            output_dir = root / "artifacts"

            dataframe = synthetic_matrix()

            write_matrix(
                dataframe,
                input_path,
            )

            first = silent_prepare(
                dataframe,
                input_path=input_path,
                output_dir=output_dir,
            )

            queue_path = first[
                "paths"
            ]["queue"]

            queue_path.write_text(
                "stale artifact\n",
                encoding="utf-8",
            )

            second = silent_prepare(
                dataframe,
                input_path=input_path,
                output_dir=output_dir,
                force=True,
            )

            queue = read_csv(
                second["paths"]["queue"]
            )

            self.assertEqual(
                len(queue),
                2,
            )

            self.assertEqual(
                list(queue.columns),
                recovery.RECOVERY_COLUMNS,
            )

    def test_input_checksum_is_preserved(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "matrix.csv"
            output_dir = root / "artifacts"

            dataframe = synthetic_matrix()

            write_matrix(
                dataframe,
                input_path,
            )

            checksum_before = (
                recovery.sha256_file(
                    input_path
                )
            )

            result = silent_prepare(
                dataframe,
                input_path=input_path,
                output_dir=output_dir,
            )

            checksum_after = (
                recovery.sha256_file(
                    input_path
                )
            )

            self.assertEqual(
                checksum_before,
                checksum_after,
            )

            self.assertEqual(
                result["manifest"]["input"][
                    "sha256"
                ],
                checksum_before,
            )


if __name__ == "__main__":
    unittest.main()
