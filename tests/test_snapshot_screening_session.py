"""Tests for screening-session snapshots."""

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
    / "snapshot_screening_session.py"
)

SPEC = importlib.util.spec_from_file_location(
    "snapshot_screening_session",
    SCRIPT_PATH,
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError(
        f"Unable to load script: {SCRIPT_PATH}"
    )

snapshotter = importlib.util.module_from_spec(
    SPEC
)

sys.modules[SPEC.name] = snapshotter
SPEC.loader.exec_module(snapshotter)


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
    abstract: str = (
        "Synthetic abstract used for automated testing."
    ),
    abstract_available: str | None = None,
    evidence: str | None = None,
) -> dict[str, str]:
    """Create one synthetic screening record."""

    completed = decision != ""

    if abstract_available is None:
        abstract_available = (
            "true"
            if abstract.strip()
            else "false"
        )

    reason_codes = {
        "Include": "I01",
        "Exclude": "E01",
        "Uncertain": "U01",
    }

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
        "abstract": abstract,
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
            evidence
            if evidence is not None
            else (
                "Synthetic evidence supporting "
                "the screening decision."
                if completed
                else ""
            )
        ),
        "screened_by": (
            "Andre Cataldo"
            if completed
            else ""
        ),
        "screening_date": (
            "2026-08-05"
            if completed
            else ""
        ),
        "second_review_required": (
            "true"
            if decision == "Uncertain"
            else "false"
        ),
        "screening_notes": "",
    }


def baseline_dataframe() -> pd.DataFrame:
    """Return the synthetic baseline matrix."""

    return pd.DataFrame(
        [
            screening_row(
                record_id="NLM-001",
                decision="",
                priority="A1",
            ),
            screening_row(
                record_id="NLM-002",
                decision="Include",
                priority="A1",
                evidence="Original evidence.",
            ),
            screening_row(
                record_id="NLM-003",
                decision="",
                priority="A3",
                abstract="",
                abstract_available="false",
            ),
            screening_row(
                record_id="NLM-004",
                decision="",
                priority="A2",
                title="Original bibliographic title",
            ),
        ],
        columns=snapshotter.REQUIRED_COLUMNS,
    )


def changed_dataframe() -> pd.DataFrame:
    """Return a synthetic session derived from the baseline."""

    dataframe = baseline_dataframe().copy()

    decision_mask = (
        dataframe["record_id"] == "NLM-001"
    )

    dataframe.loc[
        decision_mask,
        "screening_decision",
    ] = "Include"

    dataframe.loc[
        decision_mask,
        "screening_reason_code",
    ] = "I01"

    dataframe.loc[
        decision_mask,
        "screening_reason",
    ] = "Operational LLM integration confirmed."

    dataframe.loc[
        decision_mask,
        "screening_evidence",
    ] = (
        "The abstract describes neural decoding "
        "followed by language generation."
    )

    dataframe.loc[
        decision_mask,
        "screened_by",
    ] = "Andre Cataldo"

    dataframe.loc[
        decision_mask,
        "screening_date",
    ] = "2026-08-05"

    evidence_mask = (
        dataframe["record_id"] == "NLM-002"
    )

    dataframe.loc[
        evidence_mask,
        "screening_evidence",
    ] = "Revised evidence after manual review."

    abstract_mask = (
        dataframe["record_id"] == "NLM-003"
    )

    dataframe.loc[
        abstract_mask,
        "abstract",
    ] = (
        "Recovered abstract describing "
        "neurotechnology governance."
    )

    dataframe.loc[
        abstract_mask,
        "abstract_available",
    ] = "true"

    title_mask = (
        dataframe["record_id"] == "NLM-004"
    )

    dataframe.loc[
        title_mask,
        "title",
    ] = "Modified bibliographic title"

    return dataframe


def write_matrix(
    dataframe: pd.DataFrame,
    path: Path,
) -> None:
    """Write a synthetic matrix."""

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
    """Read a generated CSV."""

    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )


def silent_snapshot(
    *,
    input_path: Path,
    output_root: Path,
    session_id: str,
    reviewer: str = "Andre Cataldo",
    previous_directory: Path | None = None,
    note: str = "",
    dry_run: bool = False,
) -> dict[str, object]:
    """Run create_snapshot without terminal output."""

    output = io.StringIO()

    with redirect_stdout(output):
        return snapshotter.create_snapshot(
            input_path=input_path,
            output_root=output_root,
            session_id=session_id,
            reviewer=reviewer,
            previous_directory=(
                previous_directory
            ),
            note=note,
            dry_run=dry_run,
        )


def create_baseline_snapshot(
    root: Path,
) -> tuple[Path, Path]:
    """Create a baseline matrix and snapshot."""

    input_path = root / "matrix.csv"
    output_root = root / "sessions"

    write_matrix(
        baseline_dataframe(),
        input_path,
    )

    silent_snapshot(
        input_path=input_path,
        output_root=output_root,
        session_id="baseline",
        note="Synthetic baseline.",
    )

    return (
        input_path,
        output_root / "baseline",
    )


class NormalizationAndValidationTests(
    unittest.TestCase
):
    def test_clean_and_normalized_text(
        self,
    ) -> None:
        self.assertEqual(
            snapshotter.clean_text("  A   B  "),
            "  A   B  ",
        )

        self.assertEqual(
            snapshotter.normalized_text(
                "  A   B  "
            ),
            "A B",
        )

        self.assertEqual(
            snapshotter.clean_text(float("nan")),
            "",
        )

    def test_validate_identifier_accepts_safe_value(
        self,
    ) -> None:
        self.assertEqual(
            snapshotter.validate_identifier(
                " session_01-test.2 ",
                field_name="Session ID",
            ),
            "session_01-test.2",
        )

    def test_validate_identifier_rejects_unsafe_value(
        self,
    ) -> None:
        invalid_values = [
            "",
            "session 01",
            "../session",
            "session/01",
            "session\\01",
            "session:01",
        ]

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(
                    ValueError
                ):
                    snapshotter.validate_identifier(
                        value,
                        field_name="Session ID",
                    )

    def test_validate_reviewer_rejects_empty_value(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Reviewer cannot be empty",
        ):
            snapshotter.validate_reviewer("   ")

    def test_validate_matrix_accepts_valid_matrix(
        self,
    ) -> None:
        snapshotter.validate_matrix(
            baseline_dataframe()
        )

    def test_validate_matrix_rejects_missing_column(
        self,
    ) -> None:
        dataframe = baseline_dataframe().drop(
            columns=["screening_decision"]
        )

        with self.assertRaisesRegex(
            ValueError,
            "Missing required columns",
        ):
            snapshotter.validate_matrix(
                dataframe
            )

    def test_validate_matrix_rejects_duplicate_id(
        self,
    ) -> None:
        dataframe = baseline_dataframe()

        dataframe.loc[
            1,
            "record_id",
        ] = "NLM-001"

        with self.assertRaisesRegex(
            ValueError,
            "duplicated record_id",
        ):
            snapshotter.validate_matrix(
                dataframe
            )

    def test_validate_matrix_rejects_invalid_decision(
        self,
    ) -> None:
        dataframe = baseline_dataframe()

        dataframe.loc[
            0,
            "screening_decision",
        ] = "Maybe"

        with self.assertRaisesRegex(
            ValueError,
            "Invalid screening_decision",
        ):
            snapshotter.validate_matrix(
                dataframe
            )


class ChangeClassificationTests(
    unittest.TestCase
):
    def test_classify_requested_change_types(
        self,
    ) -> None:
        cases = [
            (
                "screening_decision",
                "",
                "Include",
                (
                    "decision_added",
                    "info",
                ),
            ),
            (
                "screening_evidence",
                "Old",
                "New",
                (
                    "evidence_changed",
                    "info",
                ),
            ),
            (
                "abstract",
                "",
                "Recovered abstract",
                (
                    "abstract_recovered",
                    "info",
                ),
            ),
            (
                "title",
                "Old title",
                "New title",
                (
                    "bibliographic_field_changed",
                    "warning",
                ),
            ),
        ]

        for (
            field,
            old_value,
            new_value,
            expected,
        ) in cases:
            with self.subTest(field=field):
                self.assertEqual(
                    snapshotter.classify_change(
                        field,
                        old_value,
                        new_value,
                    ),
                    expected,
                )

    def test_compare_tracks_requested_changes(
        self,
    ) -> None:
        changes = snapshotter.compare_matrices(
            baseline_dataframe(),
            changed_dataframe(),
            session_id="session_01",
            previous_session_id="baseline",
        )

        change_keys = {
            (
                row.record_id,
                row.field,
                row.change_type,
                row.severity,
            )
            for row in changes.itertuples(
                index=False
            )
        }

        self.assertIn(
            (
                "NLM-001",
                "screening_decision",
                "decision_added",
                "info",
            ),
            change_keys,
        )

        self.assertIn(
            (
                "NLM-002",
                "screening_evidence",
                "evidence_changed",
                "info",
            ),
            change_keys,
        )

        self.assertIn(
            (
                "NLM-003",
                "abstract",
                "abstract_recovered",
                "info",
            ),
            change_keys,
        )

        self.assertIn(
            (
                "NLM-004",
                "title",
                "bibliographic_field_changed",
                "warning",
            ),
            change_keys,
        )

        self.assertEqual(
            len(changes),
            10,
        )

    def test_compare_tracks_added_and_removed_records(
        self,
    ) -> None:
        previous = baseline_dataframe().iloc[
            :2
        ].copy()

        current = previous.iloc[
            :1
        ].copy()

        added = screening_row(
            record_id="NLM-999"
        )

        current = pd.concat(
            [
                current,
                pd.DataFrame(
                    [added],
                    columns=(
                        snapshotter.REQUIRED_COLUMNS
                    ),
                ),
            ],
            ignore_index=True,
        )

        changes = snapshotter.compare_matrices(
            previous,
            current,
            session_id="session_02",
            previous_session_id="baseline",
        )

        types = set(
            changes["change_type"]
        )

        self.assertEqual(
            types,
            {
                "record_added",
                "record_removed",
            },
        )

        self.assertTrue(
            (
                changes["severity"]
                == "warning"
            ).all()
        )

    def test_row_order_change_is_detected(
        self,
    ) -> None:
        previous = baseline_dataframe()

        current = previous.iloc[
            [1, 0, 2, 3]
        ].reset_index(drop=True)

        self.assertTrue(
            snapshotter.row_order_changed(
                previous,
                current,
            )
        )

        self.assertFalse(
            snapshotter.row_order_changed(
                previous,
                previous.copy(),
            )
        )

    def test_column_changes_are_detected(
        self,
    ) -> None:
        previous = baseline_dataframe()

        current = previous.drop(
            columns=["venue"]
        ).copy()

        current["new_test_column"] = ""

        changes = snapshotter.changed_columns(
            previous,
            current,
        )

        self.assertEqual(
            changes,
            {
                "added": [
                    "new_test_column",
                ],
                "removed": [
                    "venue",
                ],
            },
        )

    def test_change_summary_and_decision_counts(
        self,
    ) -> None:
        current = changed_dataframe()

        changes = snapshotter.compare_matrices(
            baseline_dataframe(),
            current,
            session_id="session_01",
            previous_session_id="baseline",
        )

        summary = snapshotter.summarize_changes(
            changes
        )

        self.assertEqual(
            summary["total_changes"],
            10,
        )

        self.assertEqual(
            summary["changed_records"],
            4,
        )

        self.assertEqual(
            summary["by_severity"],
            {
                "info": 9,
                "warning": 1,
            },
        )

        self.assertEqual(
            snapshotter.decision_counts(
                current
            ),
            {
                "include": 2,
                "exclude": 0,
                "uncertain": 0,
                "pending": 2,
            },
        )


class SnapshotTests(unittest.TestCase):
    def test_baseline_snapshot_writes_expected_artifacts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            input_path = root / "matrix.csv"
            output_root = root / "sessions"

            write_matrix(
                baseline_dataframe(),
                input_path,
            )

            result = silent_snapshot(
                input_path=input_path,
                output_root=output_root,
                session_id="baseline",
                note="Synthetic baseline.",
            )

            destination = result[
                "destination"
            ]

            matrix_path = (
                destination
                / snapshotter.SNAPSHOT_MATRIX_FILENAME
            )

            changes_path = (
                destination
                / snapshotter.CHANGES_FILENAME
            )

            manifest_path = (
                destination
                / snapshotter.MANIFEST_FILENAME
            )

            self.assertTrue(
                matrix_path.exists()
            )

            self.assertTrue(
                changes_path.exists()
            )

            self.assertTrue(
                manifest_path.exists()
            )

            changes = read_csv(
                changes_path
            )

            self.assertTrue(
                changes.empty
            )

            manifest = json.loads(
                manifest_path.read_text(
                    encoding="utf-8"
                )
            )

            self.assertTrue(
                manifest["baseline_snapshot"]
            )

            self.assertIsNone(
                manifest["previous_snapshot"]
            )

            self.assertEqual(
                manifest["changes"][
                    "total_changes"
                ],
                0,
            )

            self.assertEqual(
                manifest["screening_decisions"],
                {
                    "include": 1,
                    "exclude": 0,
                    "uncertain": 0,
                    "pending": 3,
                },
            )

            recorded_matrix_path = Path(
                manifest["snapshot"][
                    "matrix"
                ]["path"]
            )

            recorded_changes_path = Path(
                manifest["snapshot"][
                    "changes"
                ]["path"]
            )

            self.assertEqual(
                recorded_matrix_path,
                matrix_path,
            )

            self.assertEqual(
                recorded_changes_path,
                changes_path,
            )

            self.assertTrue(
                recorded_matrix_path.exists()
            )

            self.assertTrue(
                recorded_changes_path.exists()
            )

            self.assertEqual(
                manifest["snapshot"][
                    "matrix"
                ]["sha256"],
                snapshotter.sha256_file(
                    matrix_path
                ),
            )

    def test_dry_run_writes_nothing(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            input_path = root / "matrix.csv"
            output_root = root / "sessions"

            write_matrix(
                baseline_dataframe(),
                input_path,
            )

            result = silent_snapshot(
                input_path=input_path,
                output_root=output_root,
                session_id="dry_run",
                dry_run=True,
            )

            self.assertTrue(
                result["baseline"]
            )

            self.assertFalse(
                output_root.exists()
            )

    def test_second_snapshot_links_previous_and_writes_changes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            (
                input_path,
                baseline_directory,
            ) = create_baseline_snapshot(root)

            write_matrix(
                changed_dataframe(),
                input_path,
            )

            result = silent_snapshot(
                input_path=input_path,
                output_root=root / "sessions",
                session_id="session_01",
                previous_directory=(
                    baseline_directory
                ),
                note="First synthetic review session.",
            )

            destination = result[
                "destination"
            ]

            changes = read_csv(
                destination
                / snapshotter.CHANGES_FILENAME
            )

            manifest = json.loads(
                (
                    destination
                    / snapshotter.MANIFEST_FILENAME
                ).read_text(
                    encoding="utf-8"
                )
            )

            self.assertFalse(
                manifest["baseline_snapshot"]
            )

            self.assertEqual(
                manifest["previous_snapshot"][
                    "session_id"
                ],
                "baseline",
            )

            self.assertEqual(
                manifest["changes"][
                    "total_changes"
                ],
                10,
            )

            self.assertEqual(
                manifest["changes"][
                    "changed_records"
                ],
                4,
            )

            self.assertEqual(
                manifest["changes"][
                    "by_severity"
                ],
                {
                    "info": 9,
                    "warning": 1,
                },
            )

            self.assertEqual(
                len(changes),
                10,
            )

            bibliographic_changes = changes[
                changes["change_type"]
                == "bibliographic_field_changed"
            ]

            self.assertEqual(
                len(bibliographic_changes),
                1,
            )

            self.assertEqual(
                bibliographic_changes.iloc[
                    0
                ]["record_id"],
                "NLM-004",
            )

    def test_input_checksum_is_preserved(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            input_path = root / "matrix.csv"

            write_matrix(
                baseline_dataframe(),
                input_path,
            )

            checksum_before = (
                snapshotter.sha256_file(
                    input_path
                )
            )

            result = silent_snapshot(
                input_path=input_path,
                output_root=root / "sessions",
                session_id="baseline",
            )

            checksum_after = (
                snapshotter.sha256_file(
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

    def test_existing_snapshot_directory_is_protected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            input_path = root / "matrix.csv"

            write_matrix(
                baseline_dataframe(),
                input_path,
            )

            silent_snapshot(
                input_path=input_path,
                output_root=root / "sessions",
                session_id="baseline",
            )

            with self.assertRaisesRegex(
                FileExistsError,
                "Snapshot directory already exists",
            ):
                silent_snapshot(
                    input_path=input_path,
                    output_root=root / "sessions",
                    session_id="baseline",
                )

    def test_tampered_previous_matrix_is_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            (
                _,
                baseline_directory,
            ) = create_baseline_snapshot(root)

            matrix_path = (
                baseline_directory
                / snapshotter.SNAPSHOT_MATRIX_FILENAME
            )

            with matrix_path.open(
                "a",
                encoding="utf-8",
            ) as file_handle:
                file_handle.write(
                    "\n"
                )

            with self.assertRaisesRegex(
                ValueError,
                "checksum does not match",
            ):
                snapshotter.read_previous_snapshot(
                    baseline_directory
                )

    def test_previous_snapshot_requires_manifest(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_directory = (
                Path(directory)
                / "previous"
            )

            snapshot_directory.mkdir()

            write_matrix(
                baseline_dataframe(),
                snapshot_directory
                / snapshotter.SNAPSHOT_MATRIX_FILENAME,
            )

            with self.assertRaisesRegex(
                FileNotFoundError,
                "manifest not found",
            ):
                snapshotter.read_previous_snapshot(
                    snapshot_directory
                )

    def test_invalid_previous_manifest_json_is_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_directory = (
                Path(directory)
                / "previous"
            )

            snapshot_directory.mkdir()

            write_matrix(
                baseline_dataframe(),
                snapshot_directory
                / snapshotter.SNAPSHOT_MATRIX_FILENAME,
            )

            (
                snapshot_directory
                / snapshotter.MANIFEST_FILENAME
            ).write_text(
                "{invalid json",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "invalid JSON",
            ):
                snapshotter.read_previous_snapshot(
                    snapshot_directory
                )


if __name__ == "__main__":
    unittest.main()
