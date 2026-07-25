#!/usr/bin/env python3
"""Create the initial title-and-abstract screening matrix.

The script reads the adjudicated v4.3f corpus, selects the final central
records, optionally recovers the automated classification from the
non-adjudicated corpus and produces a local CSV for manual screening.

The output file is generated under outputs/ and must not be committed.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Iterable

import pandas as pd


DEFAULT_INPUT = Path(
    "outputs/resultados_neuro_v4_3f_union_p5_p10_adjudicado.csv"
)

DEFAULT_AUTOMATED_INPUT = Path(
    "outputs/resultados_neuro_v4_3f_union_p5_p10.csv"
)

DEFAULT_OUTPUT = Path(
    "outputs/matriz_triagem_neuro_v4_3f.csv"
)

PIPELINE_VERSION = "v4.3f"
TAXONOMY_VERSION = "1.6"

PRIORITY_LABELS = {
    "A1": "A1-central-integracao-llm",
    "A2": "A2-central-decoding-linguagem",
    "A3": "A3-central-riscos-governanca",
    "B": "B-apoio",
    "D": "D-descartar",
}

CENTRAL_PRIORITIES = {
    PRIORITY_LABELS["A1"],
    PRIORITY_LABELS["A2"],
    PRIORITY_LABELS["A3"],
}

EXPECTED_CENTRAL_COUNTS = {
    PRIORITY_LABELS["A1"]: 71,
    PRIORITY_LABELS["A2"]: 120,
    PRIORITY_LABELS["A3"]: 63,
}

PRIORITY_SORT_ORDER = {
    PRIORITY_LABELS["A1"]: 1,
    PRIORITY_LABELS["A3"]: 2,
    PRIORITY_LABELS["A2"]: 3,
}

COLUMN_ALIASES = {
    "record_id": (
        "record_id",
        "id",
        "work_id",
        "paper_id",
        "source_record_id",
        "openalex_id",
    ),
    "title": (
        "title",
        "titulo",
        "paper_title",
        "work_title",
    ),
    "normalized_title": (
        "normalized_title",
        "title_normalized",
        "titulo_normalizado",
    ),
    "authors": (
        "authors",
        "author",
        "autores",
        "creator",
    ),
    "year": (
        "year",
        "publication_year",
        "ano",
        "published_year",
    ),
    "venue": (
        "venue",
        "journal",
        "conference",
        "publication_venue",
        "container_title",
        "source_name",
    ),
    "doi": (
        "doi",
        "normalized_doi",
        "doi_normalized",
    ),
    "url": (
        "url",
        "publication_url",
        "landing_page_url",
        "source_url",
    ),
    "abstract": (
        "abstract",
        "resumo",
        "summary",
    ),
}

FINAL_PRIORITY_ALIASES = (
    "final_priority",
    "priority_final",
    "prioridade_final",
    "adjudicated_priority",
    "priority",
    "prioridade",
    "classification",
    "classificacao",
)

AUTOMATED_PRIORITY_ALIASES = (
    "suggested_priority",
    "automated_priority",
    "automatic_priority",
    "priority_auto",
    "prioridade_automatica",
    "priority",
    "prioridade",
    "classification",
    "classificacao",
)

OUTPUT_COLUMNS = [
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

MISSING_MARKERS = {
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create the initial screening matrix from the "
            "adjudicated v4.3f corpus."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Adjudicated corpus CSV.",
    )

    parser.add_argument(
        "--automated-input",
        type=Path,
        default=DEFAULT_AUTOMATED_INPUT,
        help=(
            "Automated corpus before manual adjudication. "
            "Used to recover suggested_priority."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination screening matrix CSV.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing output file.",
    )

    parser.add_argument(
        "--skip-baseline-validation",
        action="store_true",
        help=(
            "Do not validate the expected v4.3f distribution "
            "of 71 A1, 120 A2 and 63 A3 records."
        ),
    )

    return parser.parse_args()


def remove_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)

    return "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )


def clean_text(value: object) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.casefold() == "nan":
        return ""

    return re.sub(r"\s+", " ", text)


def normalize_header(value: str) -> str:
    value = remove_accents(value).casefold()
    value = re.sub(r"[^a-z0-9]+", "_", value)

    return value.strip("_")


def normalize_title(value: object) -> str:
    text = remove_accents(clean_text(value)).casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)

    return re.sub(r"\s+", " ", text).strip()


def normalize_doi(value: object) -> str:
    doi = clean_text(value).casefold()

    doi = re.sub(
        r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)",
        "",
        doi,
    )

    doi = doi.strip().rstrip(".,;")

    return doi


def extract_year(value: object) -> str:
    text = clean_text(value)
    match = re.search(r"\b(?:19|20)\d{2}\b", text)

    return match.group(0) if match else ""


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

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


def resolve_column(
    dataframe: pd.DataFrame,
    aliases: Iterable[str],
    *,
    required: bool = False,
    label: str,
) -> str | None:
    normalized_columns: dict[str, str] = {}

    for column in dataframe.columns:
        normalized_columns.setdefault(
            normalize_header(column),
            column,
        )

    for alias in aliases:
        normalized_alias = normalize_header(alias)

        if normalized_alias in normalized_columns:
            return normalized_columns[normalized_alias]

    if required:
        available = ", ".join(dataframe.columns)

        raise ValueError(
            f"Required column not found for '{label}'. "
            f"Accepted aliases: {', '.join(aliases)}. "
            f"Available columns: {available}"
        )

    return None


def canonical_priority(value: object) -> str:
    text = clean_text(value).upper()

    match = re.search(
        r"(?:^|[^A-Z0-9])(A1|A2|A3|B|D)(?=$|[^A-Z0-9])",
        text,
    )

    if match:
        return PRIORITY_LABELS[match.group(1)]

    for code in ("A1", "A2", "A3", "B", "D"):
        if text.startswith(code):
            return PRIORITY_LABELS[code]

    raise ValueError(
        f"Unknown priority value: {value!r}"
    )


def row_value(
    row: pd.Series,
    column: str | None,
) -> str:
    if column is None:
        return ""

    return clean_text(row.get(column, ""))


def has_abstract(value: object) -> bool:
    abstract = clean_text(value)
    normalized = remove_accents(abstract).casefold()

    return normalized not in MISSING_MARKERS


def build_title_key(
    title: object,
    year: object,
) -> str:
    normalized = normalize_title(title)
    normalized_year = extract_year(year)

    if not normalized:
        return ""

    return f"{normalized}|{normalized_year}"


def add_lookup_value(
    lookup: dict[str, str],
    key: str,
    priority: str,
    *,
    key_type: str,
) -> None:
    if not key:
        return

    existing = lookup.get(key)

    if existing is not None and existing != priority:
        raise ValueError(
            f"Conflicting automated priorities for "
            f"{key_type} key {key!r}: "
            f"{existing!r} versus {priority!r}"
        )

    lookup[key] = priority


def build_automated_priority_lookups(
    dataframe: pd.DataFrame,
) -> tuple[dict[str, str], dict[str, str]]:
    priority_column = resolve_column(
        dataframe,
        AUTOMATED_PRIORITY_ALIASES,
        required=True,
        label="automated priority",
    )

    title_column = resolve_column(
        dataframe,
        COLUMN_ALIASES["title"],
        required=True,
        label="title",
    )

    year_column = resolve_column(
        dataframe,
        COLUMN_ALIASES["year"],
        label="year",
    )

    doi_column = resolve_column(
        dataframe,
        COLUMN_ALIASES["doi"],
        label="doi",
    )

    by_doi: dict[str, str] = {}
    by_title: dict[str, str] = {}

    for _, row in dataframe.iterrows():
        priority = canonical_priority(
            row_value(row, priority_column)
        )

        doi = normalize_doi(
            row_value(row, doi_column)
        )

        title_key = build_title_key(
            row_value(row, title_column),
            row_value(row, year_column),
        )

        add_lookup_value(
            by_doi,
            doi,
            priority,
            key_type="DOI",
        )

        add_lookup_value(
            by_title,
            title_key,
            priority,
            key_type="title",
        )

    return by_doi, by_title


def find_automated_priority(
    row: pd.Series,
    *,
    final_priority: str,
    doi_column: str | None,
    title_column: str,
    year_column: str | None,
    automated_by_doi: dict[str, str],
    automated_by_title: dict[str, str],
) -> tuple[str, bool]:
    doi = normalize_doi(
        row_value(row, doi_column)
    )

    if doi and doi in automated_by_doi:
        return automated_by_doi[doi], True

    title_key = build_title_key(
        row_value(row, title_column),
        row_value(row, year_column),
    )

    if title_key and title_key in automated_by_title:
        return automated_by_title[title_key], True

    return final_priority, False


def create_record_id(
    row: pd.Series,
    *,
    id_column: str | None,
    doi_column: str | None,
    title_column: str,
    year_column: str | None,
) -> str:
    existing_id = row_value(row, id_column)

    if existing_id:
        return existing_id

    doi = normalize_doi(
        row_value(row, doi_column)
    )

    if doi:
        seed = f"doi:{doi}"
    else:
        title_key = build_title_key(
            row_value(row, title_column),
            row_value(row, year_column),
        )

        if not title_key:
            raise ValueError(
                "Unable to create record_id: "
                "record has neither DOI nor title."
            )

        seed = f"title:{title_key}"

    digest = hashlib.sha256(
        seed.encode("utf-8")
    ).hexdigest()[:12].upper()

    return f"NLM-{digest}"


def disambiguate_duplicate_record_ids(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, int, int]:
    """Create unique screening IDs without hiding duplicate candidates.

    Records that share the same original record_id remain in the matrix.
    The original identifier is preserved in duplicate_group, while each
    screening record receives a deterministic sequential suffix.
    """

    duplicated_mask = dataframe[
        "record_id"
    ].duplicated(keep=False)

    if not duplicated_mask.any():
        return dataframe, 0, 0

    duplicate_subset = dataframe.loc[duplicated_mask]

    duplicate_group_count = int(
        duplicate_subset["record_id"].nunique()
    )

    duplicate_record_count = int(
        duplicated_mask.sum()
    )

    grouped_indices = (
        duplicate_subset
        .groupby("record_id", sort=True)
        .groups
    )

    for base_id, indices in grouped_indices.items():
        ordered_indices = sorted(
            indices,
            key=lambda index: (
                normalize_doi(
                    dataframe.at[index, "doi"]
                ),
                build_title_key(
                    dataframe.at[index, "title"],
                    dataframe.at[index, "year"],
                ),
                clean_text(
                    dataframe.at[index, "url"]
                ).casefold(),
                str(index),
            ),
        )

        for position, index in enumerate(
            ordered_indices,
            start=1,
        ):
            dataframe.at[
                index,
                "duplicate_group",
            ] = base_id

            dataframe.at[
                index,
                "record_id",
            ] = f"{base_id}-{position:02d}"

            dataframe.at[
                index,
                "second_review_required",
            ] = "true"

            warning = (
                "Potential duplicate candidate: shares source "
                f"record ID {base_id}. Verify the canonical "
                "publication before the final screening decision."
            )

            existing_notes = clean_text(
                dataframe.at[index, "screening_notes"]
            )

            dataframe.at[
                index,
                "screening_notes",
            ] = " ".join(
                part
                for part in (
                    existing_notes,
                    warning,
                )
                if part
            )

    if dataframe["record_id"].duplicated().any():
        duplicated = dataframe[
            dataframe["record_id"].duplicated(
                keep=False
            )
        ]

        raise ValueError(
            "Unable to produce unique screening record IDs:\n"
            + duplicated[
                [
                    "record_id",
                    "source_record_id",
                    "title",
                ]
            ].to_string(index=False)
        )

    return (
        dataframe,
        duplicate_group_count,
        duplicate_record_count,
    )


def validate_baseline(dataframe: pd.DataFrame) -> None:
    actual = Counter(dataframe["final_priority"])

    errors: list[str] = []

    for priority, expected_count in EXPECTED_CENTRAL_COUNTS.items():
        actual_count = actual.get(priority, 0)

        if actual_count != expected_count:
            errors.append(
                f"{priority}: expected {expected_count}, "
                f"found {actual_count}"
            )

    expected_total = sum(EXPECTED_CENTRAL_COUNTS.values())
    actual_total = len(dataframe)

    if actual_total != expected_total:
        errors.append(
            f"central total: expected {expected_total}, "
            f"found {actual_total}"
        )

    if errors:
        raise ValueError(
            "The corpus does not match the v4.3f baseline:\n- "
            + "\n- ".join(errors)
        )


def create_screening_matrix(
    adjudicated: pd.DataFrame,
    automated: pd.DataFrame | None,
) -> tuple[pd.DataFrame, int, int, int]:
    columns = {
        field: resolve_column(
            adjudicated,
            aliases,
            required=field == "title",
            label=field,
        )
        for field, aliases in COLUMN_ALIASES.items()
    }

    priority_column = resolve_column(
        adjudicated,
        FINAL_PRIORITY_ALIASES,
        required=True,
        label="final priority",
    )

    automated_by_doi: dict[str, str] = {}
    automated_by_title: dict[str, str] = {}

    if automated is not None:
        (
            automated_by_doi,
            automated_by_title,
        ) = build_automated_priority_lookups(automated)

    records: list[dict[str, str]] = []
    unmatched_automated_records = 0

    for _, row in adjudicated.iterrows():
        final_priority = canonical_priority(
            row_value(row, priority_column)
        )

        if final_priority not in CENTRAL_PRIORITIES:
            continue

        suggested_priority, matched = find_automated_priority(
            row,
            final_priority=final_priority,
            doi_column=columns["doi"],
            title_column=columns["title"],
            year_column=columns["year"],
            automated_by_doi=automated_by_doi,
            automated_by_title=automated_by_title,
        )

        if automated is not None and not matched:
            unmatched_automated_records += 1

        adjudicated_priority = ""

        if suggested_priority != final_priority:
            adjudicated_priority = final_priority

        abstract = row_value(
            row,
            columns["abstract"],
        )

        abstract_is_available = has_abstract(abstract)

        source_record_id = row_value(
            row,
            columns["record_id"],
        )

        record = {
            "record_id": create_record_id(
                row,
                id_column=columns["record_id"],
                doi_column=columns["doi"],
                title_column=columns["title"],
                year_column=columns["year"],
            ),
            "source_record_id": source_record_id,
            "duplicate_group": "",
            "title": row_value(
                row,
                columns["title"],
            ),
            "authors": row_value(
                row,
                columns["authors"],
            ),
            "year": extract_year(
                row_value(row, columns["year"])
            ),
            "venue": row_value(
                row,
                columns["venue"],
            ),
            "doi": normalize_doi(
                row_value(row, columns["doi"])
            ),
            "url": row_value(
                row,
                columns["url"],
            ),
            "abstract": abstract,
            "abstract_available": (
                "true"
                if abstract_is_available
                else "false"
            ),
            "suggested_priority": suggested_priority,
            "adjudicated_priority": adjudicated_priority,
            "final_priority": final_priority,
            "screening_decision": "",
            "screening_reason_code": "",
            "screening_reason": "",
            "screening_evidence": "",
            "screened_by": "",
            "screening_date": "",
            "second_review_required": (
                "false"
                if abstract_is_available
                else "true"
            ),
            "screening_notes": "",
        }

        records.append(record)

    matrix = pd.DataFrame(
        records,
        columns=OUTPUT_COLUMNS,
    )

    (
        matrix,
        duplicate_group_count,
        duplicate_record_count,
    ) = disambiguate_duplicate_record_ids(matrix)

    matrix["_priority_order"] = matrix[
        "final_priority"
    ].map(PRIORITY_SORT_ORDER)

    matrix["_abstract_order"] = matrix[
        "abstract_available"
    ].map(
        {
            "false": 0,
            "true": 1,
        }
    )

    matrix["_year_order"] = pd.to_numeric(
        matrix["year"],
        errors="coerce",
    ).fillna(-1)

    matrix["_title_order"] = matrix[
        "title"
    ].map(normalize_title)

    matrix = matrix.sort_values(
        by=[
            "_priority_order",
            "_abstract_order",
            "_year_order",
            "_title_order",
        ],
        ascending=[
            True,
            True,
            False,
            True,
        ],
        kind="stable",
    )

    matrix = matrix.drop(
        columns=[
            "_priority_order",
            "_abstract_order",
            "_year_order",
            "_title_order",
        ]
    ).reset_index(drop=True)

    return (
        matrix,
        unmatched_automated_records,
        duplicate_group_count,
        duplicate_record_count,
    )


def print_summary(
    *,
    input_rows: int,
    matrix: pd.DataFrame,
    unmatched_automated_records: int,
    duplicate_group_count: int,
    duplicate_record_count: int,
    output: Path,
) -> None:
    counts = Counter(matrix["final_priority"])

    missing_abstracts = int(
        (matrix["abstract_available"] == "false").sum()
    )

    adjudications = int(
        (matrix["adjudicated_priority"] != "").sum()
    )

    print()
    print("Screening matrix created successfully")
    print("-------------------------------------")
    print(f"Input records:              {input_rows}")
    print(f"Central records:            {len(matrix)}")
    print(
        "A1 records:                 "
        f"{counts.get(PRIORITY_LABELS['A1'], 0)}"
    )
    print(
        "A3 records:                 "
        f"{counts.get(PRIORITY_LABELS['A3'], 0)}"
    )
    print(
        "A2 records:                 "
        f"{counts.get(PRIORITY_LABELS['A2'], 0)}"
    )
    print(f"Records without abstract:   {missing_abstracts}")
    print(f"Adjudicated central records:{adjudications:>6}")
    print(
        "Automated matches missing:  "
        f"{unmatched_automated_records}"
    )
    print(
        "Potential duplicate groups: "
        f"{duplicate_group_count}"
    )
    print(
        "Potential duplicate records:"
        f"{duplicate_record_count:>6}"
    )
    print(f"Output:                     {output}")


def main() -> int:
    args = parse_args()

    if args.output.exists() and not args.force:
        print(
            f"ERROR: output already exists: {args.output}\n"
            "Use --force only when you are certain that no manual "
            "screening work will be overwritten.",
            file=sys.stderr,
        )
        return 2

    try:
        adjudicated = read_csv(args.input)

        automated: pd.DataFrame | None = None

        if args.automated_input.exists():
            automated = read_csv(args.automated_input)
        else:
            print(
                "WARNING: automated input was not found. "
                "suggested_priority will fall back to final_priority: "
                f"{args.automated_input}",
                file=sys.stderr,
            )

        (
            matrix,
            unmatched,
            duplicate_group_count,
            duplicate_record_count,
        ) = create_screening_matrix(
            adjudicated,
            automated,
        )

        if not args.skip_baseline_validation:
            validate_baseline(matrix)

        args.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        matrix.to_csv(
            args.output,
            index=False,
            encoding="utf-8-sig",
            lineterminator="\n",
        )

        print_summary(
            input_rows=len(adjudicated),
            matrix=matrix,
            unmatched_automated_records=unmatched,
            duplicate_group_count=duplicate_group_count,
            duplicate_record_count=duplicate_record_count,
            output=args.output,
        )

        return 0

    except (
        FileNotFoundError,
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
