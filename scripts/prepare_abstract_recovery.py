#!/usr/bin/env python3
"""Prepare an auditable queue for abstract recovery.

The script selects records without abstracts from the title-and-abstract
screening matrix and creates:

- a structured CSV recovery queue;
- a JSON preparation manifest with counts and SHA-256 checksums.

The source screening matrix is never modified.
No external APIs are called.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_INPUT = Path(
    "outputs/matriz_triagem_neuro_v4_3f.csv"
)

DEFAULT_OUTPUT_DIR = Path("outputs")
DEFAULT_LABEL = "v4_3f"
EXPECTED_MISSING_ABSTRACTS = 40

VALID_BOOLEANS = {
    "true",
    "false",
}

VALID_RECOVERY_STATUSES = {
    "Pending",
    "In progress",
    "Recovered",
    "Not found",
}

MISSING_ABSTRACT_MARKERS = {
    "",
    "n/a",
    "na",
    "nan",
    "none",
    "null",
    "not available",
    "not informed",
    "no abstract",
    "no abstract available",
    "sem resumo",
    "resumo indisponivel",
}

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

RECOVERY_COLUMNS = [
    "record_id",
    "source_record_id",
    "matrix_row",
    "duplicate_group",
    "suggested_priority",
    "adjudicated_priority",
    "final_priority",
    "title",
    "authors",
    "year",
    "venue",
    "doi",
    "url",
    "original_abstract",
    "original_abstract_available",
    "screening_decision",
    "second_review_required",
    "original_screening_notes",
    "recovery_status",
    "recovery_source_type",
    "recovery_source_name",
    "recovery_source_url",
    "recovery_date",
    "recovered_by",
    "recovered_abstract",
    "recovery_notes",
]

OUTPUT_FILENAMES = {
    "queue": (
        "matriz_recuperacao_resumos_{label}.csv"
    ),
    "manifest": (
        "manifesto_preparacao_recuperacao_"
        "resumos_{label}.json"
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare a structured queue for recovering "
            "missing abstracts."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Screening matrix CSV.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for generated artifacts.",
    )

    parser.add_argument(
        "--label",
        default=DEFAULT_LABEL,
        help=(
            "Version label used in output filenames. "
            "Example: v4_3f."
        ),
    )

    parser.add_argument(
        "--expected-count",
        type=int,
        default=EXPECTED_MISSING_ABSTRACTS,
        help=(
            "Expected number of missing abstracts. "
            "Use a negative value to disable this check."
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated artifacts.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Validate and report the recovery queue "
            "without writing files."
        ),
    )

    return parser.parse_args()


def clean_text(value: object) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.casefold() == "nan":
        return ""

    return re.sub(r"\s+", " ", text)


def validate_label(label: str) -> str:
    normalized = clean_text(label)

    if not normalized:
        raise ValueError(
            "The recovery label cannot be empty."
        )

    if not re.fullmatch(
        r"[A-Za-z0-9_.-]+",
        normalized,
    ):
        raise ValueError(
            "The recovery label may contain only "
            "letters, numbers, dots, underscores "
            "and hyphens."
        )

    return normalized


def normalize_missing_marker(
    value: object,
) -> str:
    text = clean_text(value)

    normalized = unicodedata.normalize(
        "NFKD",
        text,
    )

    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(
            character
        )
    )

    return without_accents.casefold()


def abstract_is_missing(
    value: object,
) -> bool:
    return (
        normalize_missing_marker(value)
        in MISSING_ABSTRACT_MARKERS
    )


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
        clean_text(column)
        for column in dataframe.columns
    ]

    return dataframe


def validate_matrix(
    dataframe: pd.DataFrame,
    *,
    expected_missing: int | None,
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
    ].map(clean_text)

    if record_ids.eq("").any():
        raise ValueError(
            "The matrix contains blank record_id values."
        )

    if not record_ids.is_unique:
        raise ValueError(
            "The matrix contains duplicated record_id values."
        )

    abstract_flags = (
        dataframe["abstract_available"]
        .map(clean_text)
        .str.casefold()
    )

    second_review_flags = (
        dataframe["second_review_required"]
        .map(clean_text)
        .str.casefold()
    )

    invalid_abstract_flags = sorted(
        set(abstract_flags) - VALID_BOOLEANS
    )

    if invalid_abstract_flags:
        raise ValueError(
            "Invalid abstract_available values: "
            + ", ".join(invalid_abstract_flags)
        )

    invalid_review_flags = sorted(
        set(second_review_flags)
        - VALID_BOOLEANS
    )

    if invalid_review_flags:
        raise ValueError(
            "Invalid second_review_required values: "
            + ", ".join(invalid_review_flags)
        )

    inconsistencies: list[str] = []
    missing_without_review: list[str] = []

    for _, row in dataframe.iterrows():
        record_id = clean_text(
            row["record_id"]
        )

        flag = clean_text(
            row["abstract_available"]
        ).casefold()

        actual_missing = abstract_is_missing(
            row["abstract"]
        )

        expected_flag = (
            "false"
            if actual_missing
            else "true"
        )

        if flag != expected_flag:
            inconsistencies.append(record_id)

        if (
            flag == "false"
            and clean_text(
                row["second_review_required"]
            ).casefold()
            != "true"
        ):
            missing_without_review.append(
                record_id
            )

    if inconsistencies:
        raise ValueError(
            "abstract_available does not match "
            "abstract content for: "
            + ", ".join(inconsistencies[:10])
        )

    if missing_without_review:
        raise ValueError(
            "Records without abstracts must require "
            "second review: "
            + ", ".join(
                missing_without_review[:10]
            )
        )

    missing_count = int(
        (abstract_flags == "false").sum()
    )

    if (
        expected_missing is not None
        and missing_count != expected_missing
    ):
        raise ValueError(
            "Unexpected missing-abstract count: "
            f"expected {expected_missing}, "
            f"found {missing_count}."
        )


def build_recovery_queue(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    abstract_flags = (
        dataframe["abstract_available"]
        .map(clean_text)
        .str.casefold()
    )

    missing = dataframe[
        abstract_flags == "false"
    ].copy()

    recovery_rows: list[
        dict[str, str]
    ] = []

    for index, row in missing.iterrows():
        recovery_rows.append(
            {
                "record_id": clean_text(
                    row["record_id"]
                ),
                "source_record_id": clean_text(
                    row["source_record_id"]
                ),
                "matrix_row": str(
                    int(index) + 2
                ),
                "duplicate_group": clean_text(
                    row["duplicate_group"]
                ),
                "suggested_priority": clean_text(
                    row["suggested_priority"]
                ),
                "adjudicated_priority": clean_text(
                    row["adjudicated_priority"]
                ),
                "final_priority": clean_text(
                    row["final_priority"]
                ),
                "title": clean_text(
                    row["title"]
                ),
                "authors": clean_text(
                    row["authors"]
                ),
                "year": clean_text(
                    row["year"]
                ),
                "venue": clean_text(
                    row["venue"]
                ),
                "doi": clean_text(
                    row["doi"]
                ),
                "url": clean_text(
                    row["url"]
                ),
                "original_abstract": clean_text(
                    row["abstract"]
                ),
                "original_abstract_available": (
                    clean_text(
                        row["abstract_available"]
                    ).casefold()
                ),
                "screening_decision": clean_text(
                    row["screening_decision"]
                ),
                "second_review_required": (
                    clean_text(
                        row[
                            "second_review_required"
                        ]
                    ).casefold()
                ),
                "original_screening_notes": (
                    clean_text(
                        row["screening_notes"]
                    )
                ),
                "recovery_status": "Pending",
                "recovery_source_type": "",
                "recovery_source_name": "",
                "recovery_source_url": "",
                "recovery_date": "",
                "recovered_by": "",
                "recovered_abstract": "",
                "recovery_notes": "",
            }
        )

    return pd.DataFrame(
        recovery_rows,
        columns=RECOVERY_COLUMNS,
    )


def validate_recovery_queue(
    dataframe: pd.DataFrame,
) -> None:
    if list(dataframe.columns) != RECOVERY_COLUMNS:
        raise ValueError(
            "Recovery queue columns do not match "
            "the expected schema."
        )

    if dataframe["record_id"].duplicated().any():
        raise ValueError(
            "The recovery queue contains duplicated "
            "record_id values."
        )

    statuses = set(
        dataframe["recovery_status"].map(
            clean_text
        )
    )

    invalid_statuses = sorted(
        statuses - VALID_RECOVERY_STATUSES
    )

    if invalid_statuses:
        raise ValueError(
            "Invalid recovery_status values: "
            + ", ".join(invalid_statuses)
        )

    if not (
        dataframe["recovery_status"]
        .map(clean_text)
        .eq("Pending")
        .all()
    ):
        raise ValueError(
            "A newly prepared recovery queue must "
            "start entirely as Pending."
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file_handle:
        for chunk in iter(
            lambda: file_handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def output_paths(
    output_dir: Path,
    label: str,
) -> dict[str, Path]:
    return {
        key: (
            output_dir
            / filename.format(label=label)
        )
        for key, filename
        in OUTPUT_FILENAMES.items()
    }


def check_existing_outputs(
    paths: dict[str, Path],
    *,
    force: bool,
) -> None:
    existing = [
        path
        for path in paths.values()
        if path.exists()
    ]

    if existing and not force:
        formatted = "\n".join(
            f"  - {path}"
            for path in existing
        )

        raise FileExistsError(
            "Recovery artifacts already exist. "
            "Use --force to overwrite:\n"
            + formatted
        )


def write_csv_atomic(
    dataframe: pd.DataFrame,
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_name(
        path.name + ".tmp"
    )

    try:
        dataframe.to_csv(
            temporary,
            index=False,
            encoding="utf-8-sig",
            lineterminator="\n",
        )

        temporary.replace(path)

    finally:
        if temporary.exists():
            temporary.unlink()


def write_json_atomic(
    payload: dict[str, Any],
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_name(
        path.name + ".tmp"
    )

    try:
        temporary.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        temporary.replace(path)

    finally:
        if temporary.exists():
            temporary.unlink()


def priority_counts(
    recovery_queue: pd.DataFrame,
) -> dict[str, int]:
    counts = Counter(
        recovery_queue[
            "final_priority"
        ].map(clean_text)
    )

    return dict(
        sorted(counts.items())
    )


def build_manifest(
    *,
    input_path: Path,
    input_sha256: str,
    input_rows: int,
    recovery_queue: pd.DataFrame,
    queue_path: Path,
) -> dict[str, Any]:
    duplicate_candidates = int(
        recovery_queue[
            "duplicate_group"
        ].map(clean_text).ne("").sum()
    )

    return {
        "schema_version": 1,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "input": {
            "path": str(input_path),
            "sha256": input_sha256,
            "rows": input_rows,
        },
        "selection_rule": (
            "abstract_available is false and "
            "abstract contains a recognized "
            "missing-value marker"
        ),
        "counts": {
            "missing_abstracts": len(
                recovery_queue
            ),
            "by_final_priority": (
                priority_counts(
                    recovery_queue
                )
            ),
            "duplicate_candidates": (
                duplicate_candidates
            ),
            "pending_recovery": len(
                recovery_queue
            ),
            "recovered": 0,
            "not_found": 0,
        },
        "initial_status": "Pending",
        "queue": {
            "path": str(queue_path),
            "rows": len(recovery_queue),
            "columns": len(
                recovery_queue.columns
            ),
            "sha256": sha256_file(
                queue_path
            ),
        },
    }


def print_summary(
    *,
    input_path: Path,
    output_dir: Path,
    label: str,
    input_rows: int,
    recovery_queue: pd.DataFrame,
    dry_run: bool,
) -> None:
    print()
    print("Abstract recovery preparation")
    print("=============================")
    print(f"Input:       {input_path}")
    print(f"Output dir:  {output_dir}")
    print(f"Label:       {label}")
    print(
        "Mode:        "
        + (
            "dry run"
            if dry_run
            else "write artifacts"
        )
    )

    print()
    print("Counts")
    print("------")
    print(f"Input rows:          {input_rows}")
    print(
        "Missing abstracts:   "
        f"{len(recovery_queue)}"
    )
    print(
        "Pending recovery:     "
        f"{len(recovery_queue)}"
    )

    print()
    print("By final priority")
    print("-----------------")

    for priority, count in priority_counts(
        recovery_queue
    ).items():
        print(f"{priority}: {count}")

    duplicate_candidates = int(
        recovery_queue[
            "duplicate_group"
        ].map(clean_text).ne("").sum()
    )

    print()
    print(
        "Duplicate candidates: "
        f"{duplicate_candidates}"
    )


def prepare_recovery(
    dataframe: pd.DataFrame,
    *,
    input_path: Path,
    output_dir: Path,
    label: str,
    expected_missing: int | None,
    force: bool,
    dry_run: bool,
) -> dict[str, Any]:
    validate_matrix(
        dataframe,
        expected_missing=expected_missing,
    )

    recovery_queue = build_recovery_queue(
        dataframe
    )

    validate_recovery_queue(
        recovery_queue
    )

    paths = output_paths(
        output_dir,
        label,
    )

    print_summary(
        input_path=input_path,
        output_dir=output_dir,
        label=label,
        input_rows=len(dataframe),
        recovery_queue=recovery_queue,
        dry_run=dry_run,
    )

    if dry_run:
        return {
            "queue": recovery_queue,
            "paths": paths,
        }

    check_existing_outputs(
        paths,
        force=force,
    )

    input_sha256_before = sha256_file(
        input_path
    )

    write_csv_atomic(
        recovery_queue,
        paths["queue"],
    )

    manifest = build_manifest(
        input_path=input_path,
        input_sha256=input_sha256_before,
        input_rows=len(dataframe),
        recovery_queue=recovery_queue,
        queue_path=paths["queue"],
    )

    write_json_atomic(
        manifest,
        paths["manifest"],
    )

    input_sha256_after = sha256_file(
        input_path
    )

    if (
        input_sha256_before
        != input_sha256_after
    ):
        raise RuntimeError(
            "The screening matrix changed during "
            "recovery preparation."
        )

    print()
    print("Artifacts created")
    print("-----------------")
    print(paths["queue"])
    print(paths["manifest"])

    return {
        "queue": recovery_queue,
        "paths": paths,
        "manifest": manifest,
    }


def main() -> int:
    args = parse_args()

    try:
        label = validate_label(
            args.label
        )

        expected_missing = (
            None
            if args.expected_count < 0
            else args.expected_count
        )

        dataframe = read_matrix(
            args.input
        )

        prepare_recovery(
            dataframe,
            input_path=args.input,
            output_dir=args.output_dir,
            label=label,
            expected_missing=(
                expected_missing
            ),
            force=args.force,
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
