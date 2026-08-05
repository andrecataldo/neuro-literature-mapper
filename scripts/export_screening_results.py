#!/usr/bin/env python3
"""Export subsets derived from the screening matrix.

The script exports:

- included records;
- excluded records;
- uncertain records;
- pending records;
- records selected for full-text assessment;
- a completed matrix snapshot when no pending records remain;
- an audit manifest with counts and SHA-256 checksums.

The input screening matrix is never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_INPUT = Path(
    "outputs/matriz_triagem_neuro_v4_3f.csv"
)

DEFAULT_OUTPUT_DIR = Path("outputs")
DEFAULT_LABEL = "v4_3f"

VALID_DECISIONS = {
    "",
    "Include",
    "Exclude",
    "Uncertain",
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

COMPLETED_DECISION_FIELDS = [
    "screening_reason_code",
    "screening_reason",
    "screening_evidence",
    "screened_by",
    "screening_date",
    "second_review_required",
]

EXPORT_FILENAMES = {
    "include": (
        "estudos_incluidos_titulo_resumo_{label}.csv"
    ),
    "exclude": (
        "estudos_excluidos_titulo_resumo_{label}.csv"
    ),
    "uncertain": (
        "estudos_incertos_titulo_resumo_{label}.csv"
    ),
    "pending": (
        "estudos_pendentes_titulo_resumo_{label}.csv"
    ),
    "full_text": (
        "estudos_para_texto_completo_{label}.csv"
    ),
    "completed_matrix": (
        "matriz_triagem_neuro_{label}_concluida.csv"
    ),
    "manifest": (
        "manifesto_exportacao_triagem_{label}.json"
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export decision subsets from the "
            "title-and-abstract screening matrix."
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
        help="Directory for generated exports.",
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
        "--require-complete",
        action="store_true",
        help=(
            "Refuse export when pending records remain."
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated files.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Validate and report counts without "
            "writing files."
        ),
    )

    return parser.parse_args()


def clean_text(value: object) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.casefold() == "nan":
        return ""

    return " ".join(text.split())


def validate_label(label: str) -> str:
    normalized = clean_text(label)

    if not normalized:
        raise ValueError(
            "The export label cannot be empty."
        )

    if not re.fullmatch(
        r"[A-Za-z0-9_.-]+",
        normalized,
    ):
        raise ValueError(
            "The export label may contain only letters, "
            "numbers, dots, underscores and hyphens."
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
        clean_text(column)
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
    ].map(clean_text)

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
    ].map(clean_text)

    invalid_decisions = sorted(
        set(decisions) - VALID_DECISIONS
    )

    if invalid_decisions:
        raise ValueError(
            "Invalid screening_decision values: "
            + ", ".join(invalid_decisions)
        )

    completed = decisions != ""

    for column in COMPLETED_DECISION_FIELDS:
        values = dataframe[column].map(clean_text)

        incomplete_ids = dataframe.loc[
            completed & values.eq(""),
            "record_id",
        ].map(clean_text).tolist()

        if incomplete_ids:
            sample = ", ".join(incomplete_ids[:5])

            raise ValueError(
                f"Completed decisions have blank {column}: "
                f"{sample}"
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

    valid_booleans = {
        "true",
        "false",
    }

    invalid_abstract_flags = sorted(
        set(abstract_flags) - valid_booleans
    )

    if invalid_abstract_flags:
        raise ValueError(
            "Invalid abstract_available values: "
            + ", ".join(invalid_abstract_flags)
        )

    invalid_second_review_flags = sorted(
        set(second_review_flags)
        - valid_booleans
    )

    if invalid_second_review_flags:
        raise ValueError(
            "Invalid second_review_required values: "
            + ", ".join(
                invalid_second_review_flags
            )
        )


def build_subsets(
    dataframe: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    decisions = dataframe[
        "screening_decision"
    ].map(clean_text)

    include = dataframe[
        decisions == "Include"
    ].copy()

    exclude = dataframe[
        decisions == "Exclude"
    ].copy()

    uncertain = dataframe[
        decisions == "Uncertain"
    ].copy()

    pending = dataframe[
        decisions == ""
    ].copy()

    full_text = dataframe[
        decisions.isin(
            {
                "Include",
                "Uncertain",
            }
        )
    ].copy()

    return {
        "include": include,
        "exclude": exclude,
        "uncertain": uncertain,
        "pending": pending,
        "full_text": full_text,
    }


def build_counts(
    dataframe: pd.DataFrame,
    subsets: dict[str, pd.DataFrame],
) -> dict[str, int]:
    total = len(dataframe)
    pending = len(subsets["pending"])

    return {
        "total": total,
        "completed": total - pending,
        "include": len(subsets["include"]),
        "exclude": len(subsets["exclude"]),
        "uncertain": len(
            subsets["uncertain"]
        ),
        "pending": pending,
        "full_text": len(
            subsets["full_text"]
        ),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file_handle:
        for chunk in iter(
            lambda: file_handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def output_paths(
    output_dir: Path,
    label: str,
    *,
    complete: bool,
) -> dict[str, Path]:
    keys = [
        "include",
        "exclude",
        "uncertain",
        "pending",
        "full_text",
        "manifest",
    ]

    if complete:
        keys.append("completed_matrix")

    return {
        key: output_dir
        / EXPORT_FILENAMES[key].format(
            label=label
        )
        for key in keys
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
            "Output files already exist. "
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
    data: dict[str, Any],
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
                data,
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


def build_manifest(
    *,
    input_path: Path,
    input_sha256: str,
    counts: dict[str, int],
    output_files: dict[str, dict[str, object]],
    complete: bool,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "input": {
            "path": str(input_path),
            "sha256": input_sha256,
            "rows": counts["total"],
        },
        "screening_complete": complete,
        "counts": counts,
        "full_text_rule": (
            "screening_decision is Include "
            "or Uncertain"
        ),
        "outputs": output_files,
    }


def print_summary(
    *,
    input_path: Path,
    output_dir: Path,
    label: str,
    counts: dict[str, int],
    complete: bool,
    dry_run: bool,
) -> None:
    print()
    print("Screening result export")
    print("=======================")
    print(f"Input:       {input_path}")
    print(f"Output dir:  {output_dir}")
    print(f"Label:       {label}")
    print(
        "Mode:        "
        + (
            "dry run"
            if dry_run
            else "write files"
        )
    )

    print()
    print("Counts")
    print("------")
    print(f"Total:       {counts['total']}")
    print(f"Completed:   {counts['completed']}")
    print(f"Include:     {counts['include']}")
    print(f"Exclude:     {counts['exclude']}")
    print(f"Uncertain:   {counts['uncertain']}")
    print(f"Pending:     {counts['pending']}")
    print(f"Full text:   {counts['full_text']}")

    print()
    print(
        "Complete:    "
        + (
            "yes"
            if complete
            else "no"
        )
    )

    if not complete:
        print(
            "Completed matrix snapshot: "
            "not generated"
        )


def export_results(
    dataframe: pd.DataFrame,
    *,
    input_path: Path,
    output_dir: Path,
    label: str,
    force: bool,
    dry_run: bool,
    require_complete: bool,
) -> dict[str, Any]:
    validate_matrix(dataframe)

    subsets = build_subsets(dataframe)

    counts = build_counts(
        dataframe,
        subsets,
    )

    complete = counts["pending"] == 0

    if require_complete and not complete:
        raise ValueError(
            "The matrix is incomplete: "
            f"{counts['pending']} pending records remain."
        )

    paths = output_paths(
        output_dir,
        label,
        complete=complete,
    )

    print_summary(
        input_path=input_path,
        output_dir=output_dir,
        label=label,
        counts=counts,
        complete=complete,
        dry_run=dry_run,
    )

    if dry_run:
        return {
            "counts": counts,
            "complete": complete,
            "paths": paths,
        }

    check_existing_outputs(
        paths,
        force=force,
    )

    input_sha256_before = sha256_file(
        input_path
    )

    csv_exports = {
        "include": subsets["include"],
        "exclude": subsets["exclude"],
        "uncertain": subsets["uncertain"],
        "pending": subsets["pending"],
        "full_text": subsets["full_text"],
    }

    if complete:
        csv_exports["completed_matrix"] = (
            dataframe.copy()
        )

    output_files: dict[
        str,
        dict[str, object],
    ] = {}

    for key, export_dataframe in csv_exports.items():
        path = paths[key]

        write_csv_atomic(
            export_dataframe,
            path,
        )

        output_files[key] = {
            "path": str(path),
            "rows": len(export_dataframe),
            "sha256": sha256_file(path),
        }

    input_sha256_after = sha256_file(
        input_path
    )

    if input_sha256_before != input_sha256_after:
        raise RuntimeError(
            "The input screening matrix changed "
            "during export."
        )

    manifest = build_manifest(
        input_path=input_path,
        input_sha256=input_sha256_before,
        counts=counts,
        output_files=output_files,
        complete=complete,
    )

    write_json_atomic(
        manifest,
        paths["manifest"],
    )

    print()
    print("Generated files")
    print("---------------")

    for key, metadata in output_files.items():
        print(
            f"{key}: "
            f"{metadata['path']} "
            f"({metadata['rows']} rows)"
        )

    print(
        "manifest: "
        f"{paths['manifest']}"
    )

    return {
        "counts": counts,
        "complete": complete,
        "paths": paths,
        "manifest": manifest,
    }


def main() -> int:
    args = parse_args()

    try:
        label = validate_label(
            args.label
        )

        dataframe = read_matrix(
            args.input
        )

        export_results(
            dataframe,
            input_path=args.input,
            output_dir=args.output_dir,
            label=label,
            force=args.force,
            dry_run=args.dry_run,
            require_complete=(
                args.require_complete
            ),
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
