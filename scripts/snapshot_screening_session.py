#!/usr/bin/env python3
"""Create immutable snapshots of screening sessions.

Each snapshot stores:

- an exact copy of the screening matrix;
- a field-level change log compared with a previous snapshot;
- a JSON manifest with metadata, counts and SHA-256 checksums.

The source screening matrix is never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_INPUT = Path(
    "outputs/matriz_triagem_neuro_v4_3f.csv"
)

DEFAULT_OUTPUT_ROOT = Path(
    "outputs/screening_sessions"
)

SNAPSHOT_MATRIX_FILENAME = "matriz_triagem.csv"
CHANGES_FILENAME = "alteracoes.csv"
MANIFEST_FILENAME = "manifesto.json"

REQUIRED_COLUMNS = [
    "record_id",
    "source_record_id",
    "duplicate_group",
    "title",
    "authors",
    "year",
    "venue",
    "doi",
    "url",
    "abstract",
    "abstract_available",
    "suggested_priority",
    "adjudicated_priority",
    "final_priority",
    "screening_decision",
    "screening_reason_code",
    "screening_reason",
    "screening_evidence",
    "screened_by",
    "screening_date",
    "second_review_required",
    "screening_notes",
]

CHANGE_COLUMNS = [
    "session_id",
    "previous_session_id",
    "record_id",
    "change_type",
    "field",
    "old_value",
    "new_value",
    "severity",
]

BIBLIOGRAPHIC_FIELDS = {
    "source_record_id",
    "title",
    "authors",
    "year",
    "venue",
    "doi",
    "url",
}

PRIORITY_FIELDS = {
    "suggested_priority",
    "adjudicated_priority",
    "final_priority",
}

VALID_DECISIONS = {
    "",
    "Include",
    "Exclude",
    "Uncertain",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create an immutable snapshot of a "
            "title-and-abstract screening session."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Current screening matrix CSV.",
    )

    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Root directory for session snapshots.",
    )

    parser.add_argument(
        "--session-id",
        required=True,
        help=(
            "Unique session identifier. "
            "Example: baseline_v4_3f."
        ),
    )

    parser.add_argument(
        "--reviewer",
        required=True,
        help="Researcher responsible for the session.",
    )

    parser.add_argument(
        "--previous",
        type=Path,
        help=(
            "Previous snapshot directory. "
            "Omit only for the baseline snapshot."
        ),
    )

    parser.add_argument(
        "--note",
        default="",
        help="Optional note describing the session.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Validate and compare without writing "
            "the snapshot directory."
        ),
    )

    return parser.parse_args()


def clean_text(value: object) -> str:
    if value is None:
        return ""

    text = str(value)

    if text.strip().casefold() == "nan":
        return ""

    return text


def normalized_text(value: object) -> str:
    return " ".join(
        clean_text(value).strip().split()
    )


def validate_identifier(
    value: str,
    *,
    field_name: str,
) -> str:
    normalized = normalized_text(value)

    if not normalized:
        raise ValueError(
            f"{field_name} cannot be empty."
        )

    if not re.fullmatch(
        r"[A-Za-z0-9_.-]+",
        normalized,
    ):
        raise ValueError(
            f"{field_name} may contain only letters, "
            "numbers, dots, underscores and hyphens."
        )

    return normalized


def validate_reviewer(value: str) -> str:
    normalized = normalized_text(value)

    if not normalized:
        raise ValueError(
            "Reviewer cannot be empty."
        )

    return normalized


def read_matrix(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Screening matrix not found: {path}"
        )

    try:
        dataframe = pd.read_csv(
            path,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
        )
    except UnicodeDecodeError:
        dataframe = pd.read_csv(
            path,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8",
        )

    dataframe.columns = [
        normalized_text(column)
        for column in dataframe.columns
    ]

    return dataframe


def validate_matrix(
    dataframe: pd.DataFrame,
) -> None:
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    record_ids = dataframe[
        "record_id"
    ].map(normalized_text)

    if record_ids.eq("").any():
        raise ValueError(
            "The matrix contains blank record_id values."
        )

    if not record_ids.is_unique:
        raise ValueError(
            "The matrix contains duplicated record_id values."
        )

    decisions = dataframe[
        "screening_decision"
    ].map(normalized_text)

    invalid_decisions = sorted(
        set(decisions) - VALID_DECISIONS
    )

    if invalid_decisions:
        raise ValueError(
            "Invalid screening_decision values: "
            + ", ".join(invalid_decisions)
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file_handle:
        for chunk in iter(
            lambda: file_handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def read_previous_snapshot(
    snapshot_directory: Path,
) -> tuple[
    pd.DataFrame,
    dict[str, Any],
    Path,
]:
    if not snapshot_directory.exists():
        raise FileNotFoundError(
            "Previous snapshot directory not found: "
            f"{snapshot_directory}"
        )

    if not snapshot_directory.is_dir():
        raise ValueError(
            "Previous snapshot must be a directory: "
            f"{snapshot_directory}"
        )

    matrix_path = (
        snapshot_directory
        / SNAPSHOT_MATRIX_FILENAME
    )

    manifest_path = (
        snapshot_directory
        / MANIFEST_FILENAME
    )

    if not matrix_path.exists():
        raise FileNotFoundError(
            "Previous snapshot matrix not found: "
            f"{matrix_path}"
        )

    if not manifest_path.exists():
        raise FileNotFoundError(
            "Previous snapshot manifest not found: "
            f"{manifest_path}"
        )

    try:
        manifest = json.loads(
            manifest_path.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            "Previous snapshot manifest is invalid JSON: "
            f"{manifest_path}"
        ) from error

    expected_checksum = (
        manifest
        .get("snapshot", {})
        .get("matrix", {})
        .get("sha256", "")
    )

    actual_checksum = sha256_file(
        matrix_path
    )

    if not expected_checksum:
        raise ValueError(
            "Previous manifest does not contain "
            "snapshot.matrix.sha256."
        )

    if actual_checksum != expected_checksum:
        raise ValueError(
            "Previous snapshot matrix checksum does "
            "not match its manifest."
        )

    dataframe = read_matrix(
        matrix_path
    )

    validate_matrix(
        dataframe
    )

    return (
        dataframe,
        manifest,
        matrix_path,
    )


def classify_change(
    field: str,
    old_value: str,
    new_value: str,
) -> tuple[str, str]:
    old_normalized = normalized_text(
        old_value
    )

    new_normalized = normalized_text(
        new_value
    )

    if field == "screening_decision":
        if (
            not old_normalized
            and new_normalized
        ):
            return (
                "decision_added",
                "info",
            )

        if (
            old_normalized
            and not new_normalized
        ):
            return (
                "decision_cleared",
                "warning",
            )

        return (
            "decision_changed",
            "info",
        )

    if field == "screening_reason_code":
        return (
            "reason_code_changed",
            "info",
        )

    if field == "screening_reason":
        return (
            "reason_changed",
            "info",
        )

    if field == "screening_evidence":
        return (
            "evidence_changed",
            "info",
        )

    if field == "screened_by":
        return (
            "reviewer_changed",
            "info",
        )

    if field == "screening_date":
        return (
            "screening_date_changed",
            "info",
        )

    if field == "second_review_required":
        return (
            "review_flag_changed",
            "info",
        )

    if field == "screening_notes":
        return (
            "notes_changed",
            "info",
        )

    if field == "abstract":
        if (
            not old_normalized
            and new_normalized
        ):
            return (
                "abstract_recovered",
                "info",
            )

        if (
            old_normalized
            and not new_normalized
        ):
            return (
                "abstract_removed",
                "warning",
            )

        return (
            "abstract_changed",
            "info",
        )

    if field == "abstract_available":
        return (
            "abstract_availability_changed",
            "info",
        )

    if field in BIBLIOGRAPHIC_FIELDS:
        return (
            "bibliographic_field_changed",
            "warning",
        )

    if field in PRIORITY_FIELDS:
        return (
            "priority_changed",
            "warning",
        )

    if field == "duplicate_group":
        return (
            "duplicate_group_changed",
            "warning",
        )

    return (
        "field_changed",
        "info",
    )


def change_record(
    *,
    session_id: str,
    previous_session_id: str,
    record_id: str,
    change_type: str,
    field: str,
    old_value: str,
    new_value: str,
    severity: str,
) -> dict[str, str]:
    return {
        "session_id": session_id,
        "previous_session_id": (
            previous_session_id
        ),
        "record_id": record_id,
        "change_type": change_type,
        "field": field,
        "old_value": old_value,
        "new_value": new_value,
        "severity": severity,
    }


def compare_matrices(
    previous: pd.DataFrame,
    current: pd.DataFrame,
    *,
    session_id: str,
    previous_session_id: str,
) -> pd.DataFrame:
    previous_indexed = (
        previous
        .copy()
        .set_index("record_id", drop=False)
    )

    current_indexed = (
        current
        .copy()
        .set_index("record_id", drop=False)
    )

    previous_ids = set(
        previous_indexed.index
    )

    current_ids = set(
        current_indexed.index
    )

    changes: list[
        dict[str, str]
    ] = []

    for record_id in sorted(
        current_ids - previous_ids
    ):
        changes.append(
            change_record(
                session_id=session_id,
                previous_session_id=(
                    previous_session_id
                ),
                record_id=record_id,
                change_type="record_added",
                field="record_id",
                old_value="",
                new_value=record_id,
                severity="warning",
            )
        )

    for record_id in sorted(
        previous_ids - current_ids
    ):
        changes.append(
            change_record(
                session_id=session_id,
                previous_session_id=(
                    previous_session_id
                ),
                record_id=record_id,
                change_type="record_removed",
                field="record_id",
                old_value=record_id,
                new_value="",
                severity="warning",
            )
        )

    shared_ids = sorted(
        previous_ids & current_ids
    )

    comparable_columns = [
        column
        for column in current.columns
        if (
            column != "record_id"
            and column in previous.columns
        )
    ]

    for record_id in shared_ids:
        previous_row = previous_indexed.loc[
            record_id
        ]

        current_row = current_indexed.loc[
            record_id
        ]

        for field in comparable_columns:
            old_value = clean_text(
                previous_row[field]
            )

            new_value = clean_text(
                current_row[field]
            )

            if old_value == new_value:
                continue

            change_type, severity = (
                classify_change(
                    field,
                    old_value,
                    new_value,
                )
            )

            changes.append(
                change_record(
                    session_id=session_id,
                    previous_session_id=(
                        previous_session_id
                    ),
                    record_id=record_id,
                    change_type=change_type,
                    field=field,
                    old_value=old_value,
                    new_value=new_value,
                    severity=severity,
                )
            )

    return pd.DataFrame(
        changes,
        columns=CHANGE_COLUMNS,
    )


def empty_changes() -> pd.DataFrame:
    return pd.DataFrame(
        columns=CHANGE_COLUMNS
    )


def row_order_changed(
    previous: pd.DataFrame | None,
    current: pd.DataFrame,
) -> bool:
    if previous is None:
        return False

    previous_ids = list(
        previous["record_id"]
    )

    current_ids = list(
        current["record_id"]
    )

    shared_previous = [
        record_id
        for record_id in previous_ids
        if record_id in set(current_ids)
    ]

    shared_current = [
        record_id
        for record_id in current_ids
        if record_id in set(previous_ids)
    ]

    return shared_previous != shared_current


def changed_columns(
    previous: pd.DataFrame | None,
    current: pd.DataFrame,
) -> dict[str, list[str]]:
    if previous is None:
        return {
            "added": [],
            "removed": [],
        }

    previous_columns = set(
        previous.columns
    )

    current_columns = set(
        current.columns
    )

    return {
        "added": sorted(
            current_columns - previous_columns
        ),
        "removed": sorted(
            previous_columns - current_columns
        ),
    }


def summarize_changes(
    changes: pd.DataFrame,
) -> dict[str, Any]:
    if changes.empty:
        return {
            "total_changes": 0,
            "changed_records": 0,
            "by_type": {},
            "by_field": {},
            "by_severity": {},
        }

    return {
        "total_changes": len(changes),
        "changed_records": int(
            changes["record_id"].nunique()
        ),
        "by_type": dict(
            sorted(
                Counter(
                    changes["change_type"]
                ).items()
            )
        ),
        "by_field": dict(
            sorted(
                Counter(
                    changes["field"]
                ).items()
            )
        ),
        "by_severity": dict(
            sorted(
                Counter(
                    changes["severity"]
                ).items()
            )
        ),
    }


def decision_counts(
    dataframe: pd.DataFrame,
) -> dict[str, int]:
    decisions = dataframe[
        "screening_decision"
    ].map(normalized_text)

    return {
        "include": int(
            (decisions == "Include").sum()
        ),
        "exclude": int(
            (decisions == "Exclude").sum()
        ),
        "uncertain": int(
            (decisions == "Uncertain").sum()
        ),
        "pending": int(
            (decisions == "").sum()
        ),
    }


def write_changes(
    changes: pd.DataFrame,
    path: Path,
) -> None:
    changes.to_csv(
        path,
        index=False,
        encoding="utf-8-sig",
        lineterminator="\n",
    )


def write_manifest(
    manifest: dict[str, Any],
    path: Path,
) -> None:
    path.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def build_manifest(
    *,
    session_id: str,
    reviewer: str,
    note: str,
    created_at: str,
    input_path: Path,
    input_sha256: str,
    current: pd.DataFrame,
    previous_directory: Path | None,
    previous_session_id: str,
    previous_matrix_sha256: str,
    changes: pd.DataFrame,
    matrix_snapshot_path: Path,
    changes_path: Path,
    row_order_was_changed: bool,
    column_changes: dict[str, list[str]],
) -> dict[str, Any]:
    summary = summarize_changes(
        changes
    )

    return {
        "schema_version": 1,
        "session_id": session_id,
        "created_at": created_at,
        "reviewer": reviewer,
        "note": note,
        "baseline_snapshot": (
            previous_directory is None
        ),
        "input": {
            "path": str(input_path),
            "sha256": input_sha256,
            "rows": len(current),
        },
        "previous_snapshot": (
            None
            if previous_directory is None
            else {
                "session_id": (
                    previous_session_id
                ),
                "directory": str(
                    previous_directory
                ),
                "matrix_sha256": (
                    previous_matrix_sha256
                ),
            }
        ),
        "snapshot": {
            "matrix": {
                "path": str(
                    matrix_snapshot_path
                ),
                "rows": len(current),
                "sha256": sha256_file(
                    matrix_snapshot_path
                ),
            },
            "changes": {
                "path": str(
                    changes_path
                ),
                "rows": len(changes),
                "sha256": sha256_file(
                    changes_path
                ),
            },
        },
        "screening_decisions": decision_counts(
            current
        ),
        "changes": summary,
        "structure": {
            "row_order_changed": (
                row_order_was_changed
            ),
            "columns_added": (
                column_changes["added"]
            ),
            "columns_removed": (
                column_changes["removed"]
            ),
        },
    }


def print_summary(
    *,
    session_id: str,
    reviewer: str,
    output_directory: Path,
    baseline: bool,
    current: pd.DataFrame,
    changes: pd.DataFrame,
    dry_run: bool,
) -> None:
    summary = summarize_changes(
        changes
    )

    decisions = decision_counts(
        current
    )

    print()
    print("Screening session snapshot")
    print("==========================")
    print(f"Session:     {session_id}")
    print(f"Reviewer:    {reviewer}")
    print(
        "Mode:        "
        + (
            "dry run"
            if dry_run
            else "write snapshot"
        )
    )
    print(f"Output:      {output_directory}")
    print(
        "Baseline:    "
        + (
            "yes"
            if baseline
            else "no"
        )
    )

    print()
    print("Matrix")
    print("------")
    print(f"Rows:        {len(current)}")
    print(f"Include:     {decisions['include']}")
    print(f"Exclude:     {decisions['exclude']}")
    print(f"Uncertain:   {decisions['uncertain']}")
    print(f"Pending:     {decisions['pending']}")

    print()
    print("Changes")
    print("-------")
    print(
        "Total:       "
        f"{summary['total_changes']}"
    )
    print(
        "Records:     "
        f"{summary['changed_records']}"
    )

    warnings = summary[
        "by_severity"
    ].get(
        "warning",
        0,
    )

    print(f"Warnings:    {warnings}")


def create_snapshot(
    *,
    input_path: Path,
    output_root: Path,
    session_id: str,
    reviewer: str,
    previous_directory: Path | None,
    note: str,
    dry_run: bool,
) -> dict[str, Any]:
    current = read_matrix(
        input_path
    )

    validate_matrix(
        current
    )

    previous: pd.DataFrame | None = None
    previous_manifest: dict[str, Any] = {}
    previous_session_id = ""
    previous_matrix_sha256 = ""

    if previous_directory is not None:
        (
            previous,
            previous_manifest,
            previous_matrix_path,
        ) = read_previous_snapshot(
            previous_directory
        )

        previous_session_id = (
            normalized_text(
                previous_manifest.get(
                    "session_id",
                    "",
                )
            )
        )

        if not previous_session_id:
            raise ValueError(
                "Previous manifest does not contain "
                "a valid session_id."
            )

        previous_matrix_sha256 = (
            sha256_file(
                previous_matrix_path
            )
        )

        changes = compare_matrices(
            previous,
            current,
            session_id=session_id,
            previous_session_id=(
                previous_session_id
            ),
        )

    else:
        changes = empty_changes()

    destination = (
        output_root
        / session_id
    )

    if destination.exists():
        raise FileExistsError(
            "Snapshot directory already exists: "
            f"{destination}"
        )

    print_summary(
        session_id=session_id,
        reviewer=reviewer,
        output_directory=destination,
        baseline=(
            previous_directory is None
        ),
        current=current,
        changes=changes,
        dry_run=dry_run,
    )

    input_sha256_before = sha256_file(
        input_path
    )

    structure_changes = changed_columns(
        previous,
        current,
    )

    order_changed = row_order_changed(
        previous,
        current,
    )

    if dry_run:
        return {
            "session_id": session_id,
            "destination": destination,
            "changes": changes,
            "baseline": (
                previous_directory is None
            ),
            "row_order_changed": (
                order_changed
            ),
            "column_changes": (
                structure_changes
            ),
        }

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_root = Path(
        tempfile.mkdtemp(
            prefix=f".{session_id}.",
            dir=output_root,
        )
    )

    try:
        matrix_snapshot_path = (
            temporary_root
            / SNAPSHOT_MATRIX_FILENAME
        )

        changes_path = (
            temporary_root
            / CHANGES_FILENAME
        )

        manifest_path = (
            temporary_root
            / MANIFEST_FILENAME
        )

        shutil.copyfile(
            input_path,
            matrix_snapshot_path,
        )

        snapshot_checksum = sha256_file(
            matrix_snapshot_path
        )

        if (
            snapshot_checksum
            != input_sha256_before
        ):
            raise RuntimeError(
                "Snapshot matrix checksum differs "
                "from the input matrix."
            )

        write_changes(
            changes,
            changes_path,
        )

        manifest = build_manifest(
            session_id=session_id,
            reviewer=reviewer,
            note=note,
            created_at=utc_now(),
            input_path=input_path,
            input_sha256=(
                input_sha256_before
            ),
            current=current,
            previous_directory=(
                previous_directory
            ),
            previous_session_id=(
                previous_session_id
            ),
            previous_matrix_sha256=(
                previous_matrix_sha256
            ),
            changes=changes,
            matrix_snapshot_path=(
                matrix_snapshot_path
            ),
            changes_path=changes_path,
            row_order_was_changed=(
                order_changed
            ),
            column_changes=(
                structure_changes
            ),
        )

        manifest["snapshot"]["matrix"]["path"] = str(
            destination
            / SNAPSHOT_MATRIX_FILENAME
        )

        manifest["snapshot"]["changes"]["path"] = str(
            destination
            / CHANGES_FILENAME
        )

        write_manifest(
            manifest,
            manifest_path,
        )

        input_sha256_after = sha256_file(
            input_path
        )

        if (
            input_sha256_before
            != input_sha256_after
        ):
            raise RuntimeError(
                "The input screening matrix changed "
                "during snapshot creation."
            )

        temporary_root.replace(
            destination
        )

    except Exception:
        shutil.rmtree(
            temporary_root,
            ignore_errors=True,
        )
        raise

    final_manifest_path = (
        destination
        / MANIFEST_FILENAME
    )

    final_manifest = json.loads(
        final_manifest_path.read_text(
            encoding="utf-8"
        )
    )

    print()
    print("Snapshot created")
    print("----------------")
    print(destination)
    print(
        destination
        / SNAPSHOT_MATRIX_FILENAME
    )
    print(
        destination
        / CHANGES_FILENAME
    )
    print(final_manifest_path)

    return {
        "session_id": session_id,
        "destination": destination,
        "changes": changes,
        "manifest": final_manifest,
        "baseline": (
            previous_directory is None
        ),
    }


def main() -> int:
    args = parse_args()

    try:
        session_id = validate_identifier(
            args.session_id,
            field_name="Session ID",
        )

        reviewer = validate_reviewer(
            args.reviewer
        )

        create_snapshot(
            input_path=args.input,
            output_root=args.output_root,
            session_id=session_id,
            reviewer=reviewer,
            previous_directory=(
                args.previous
            ),
            note=normalized_text(
                args.note
            ),
            dry_run=args.dry_run,
        )

        return 0

    except (
        FileExistsError,
        FileNotFoundError,
        RuntimeError,
        ValueError,
        pd.errors.ParserError,
    ) as error:
        print(
            f"ERROR: {error}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())
