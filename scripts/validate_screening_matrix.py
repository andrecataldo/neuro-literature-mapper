#!/usr/bin/env python3
"""Validate the title-and-abstract screening matrix.

The validator checks:

- required columns;
- unique and non-empty record identifiers;
- controlled vocabulary values;
- baseline totals and category distribution;
- consistency between abstract text and availability flag;
- completeness of manual screening decisions;
- ISO-formatted screening dates;
- second-review requirements;
- potential duplicate groups;
- preservation of bibliographic fields from the source corpus.

Pending records are valid. A record becomes subject to completion rules
only after screening_decision is filled.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

import pandas as pd


DEFAULT_INPUT = Path(
    "outputs/matriz_triagem_neuro_v4_3f.csv"
)

DEFAULT_SOURCE = Path(
    "outputs/resultados_neuro_v4_3f_union_p5_p10_adjudicado.csv"
)

EXPECTED_TOTAL = 254

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

ALL_PRIORITIES = set(PRIORITY_LABELS.values())

EXPECTED_FINAL_COUNTS = {
    PRIORITY_LABELS["A1"]: 71,
    PRIORITY_LABELS["A2"]: 120,
    PRIORITY_LABELS["A3"]: 63,
}

VALID_DECISIONS = {
    "",
    "Include",
    "Exclude",
    "Uncertain",
}

VALID_BOOLEANS = {
    "true",
    "false",
}

INCLUSION_CODES = {
    f"I{number:02d}"
    for number in range(1, 9)
}

EXCLUSION_CODES = {
    f"E{number:02d}"
    for number in range(1, 17)
}

UNCERTAIN_CODE_PATTERN = re.compile(r"^U\d{2}$")

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

IMMUTABLE_SOURCE_FIELDS = [
    "title",
    "authors",
    "year",
    "venue",
    "doi",
    "url",
]

SOURCE_COLUMN_ALIASES = {
    "title": (
        "title",
        "titulo",
        "paper_title",
        "work_title",
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


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    record_id: str
    message: str


class ValidationReport:
    def __init__(self) -> None:
        self.issues: list[ValidationIssue] = []

    def add(
        self,
        severity: str,
        code: str,
        message: str,
        *,
        record_id: str = "",
    ) -> None:
        self.issues.append(
            ValidationIssue(
                severity=severity,
                code=code,
                record_id=record_id,
                message=message,
            )
        )

    def error(
        self,
        code: str,
        message: str,
        *,
        record_id: str = "",
    ) -> None:
        self.add(
            "ERROR",
            code,
            message,
            record_id=record_id,
        )

    def warning(
        self,
        code: str,
        message: str,
        *,
        record_id: str = "",
    ) -> None:
        self.add(
            "WARNING",
            code,
            message,
            record_id=record_id,
        )

    @property
    def errors(self) -> list[ValidationIssue]:
        return [
            issue
            for issue in self.issues
            if issue.severity == "ERROR"
        ]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [
            issue
            for issue in self.issues
            if issue.severity == "WARNING"
        ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the screening matrix."
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Screening matrix CSV.",
    )

    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Adjudicated source corpus CSV.",
    )

    parser.add_argument(
        "--skip-source-check",
        action="store_true",
        help="Skip bibliographic comparison with the source corpus.",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a failure status when warnings are found.",
    )

    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional JSON file for the validation report.",
    )

    return parser.parse_args()


def clean_text(value: object) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.casefold() == "nan":
        return ""

    return re.sub(r"\s+", " ", text)


def remove_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)

    return "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )


def normalize_header(value: str) -> str:
    value = remove_accents(value).casefold()
    value = re.sub(r"[^a-z0-9]+", "_", value)

    return value.strip("_")


def normalize_title(value: object) -> str:
    text = html.unescape(clean_text(value))
    text = re.sub(r"<[^>]+>", " ", text)
    text = remove_accents(text).casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)

    return re.sub(r"\s+", " ", text).strip()


def normalize_generic_text(value: object) -> str:
    text = html.unescape(clean_text(value))
    text = remove_accents(text).casefold()

    return re.sub(r"\s+", " ", text).strip()


def normalize_doi(value: object) -> str:
    doi = clean_text(value).casefold()

    doi = re.sub(
        r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)",
        "",
        doi,
    )

    return doi.strip().rstrip(".,;")


def normalize_url(value: object) -> str:
    url = clean_text(value)

    return url.rstrip("/")


def extract_year(value: object) -> str:
    match = re.search(
        r"\b(?:19|20)\d{2}\b",
        clean_text(value),
    )

    return match.group(0) if match else ""


def abstract_is_available(value: object) -> bool:
    normalized = remove_accents(
        clean_text(value)
    ).casefold()

    return normalized not in MISSING_ABSTRACT_MARKERS


def split_reason_codes(value: object) -> list[str]:
    text = clean_text(value)

    if not text:
        return []

    return [
        code.strip().upper()
        for code in text.split(";")
        if code.strip()
    ]


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
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


def resolve_column(
    dataframe: pd.DataFrame,
    aliases: Iterable[str],
) -> str | None:
    normalized_columns = {
        normalize_header(column): column
        for column in dataframe.columns
    }

    for alias in aliases:
        normalized_alias = normalize_header(alias)

        if normalized_alias in normalized_columns:
            return normalized_columns[normalized_alias]

    return None


def validate_structure(
    dataframe: pd.DataFrame,
    report: ValidationReport,
) -> bool:
    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing:
        report.error(
            "STRUCTURE_MISSING_COLUMNS",
            "Missing required columns: "
            + ", ".join(missing),
        )

        return False

    unexpected = [
        column
        for column in dataframe.columns
        if column not in REQUIRED_COLUMNS
    ]

    if unexpected:
        report.warning(
            "STRUCTURE_EXTRA_COLUMNS",
            "Unexpected columns were found: "
            + ", ".join(unexpected),
        )

    return True


def validate_record_ids(
    dataframe: pd.DataFrame,
    report: ValidationReport,
) -> None:
    blank_ids = dataframe[
        dataframe["record_id"].map(clean_text) == ""
    ]

    for index in blank_ids.index:
        report.error(
            "RECORD_ID_BLANK",
            f"Blank record_id at row {index + 2}.",
        )

    duplicated = dataframe[
        dataframe["record_id"].duplicated(keep=False)
    ]

    for _, row in duplicated.iterrows():
        report.error(
            "RECORD_ID_DUPLICATED",
            "record_id is not unique.",
            record_id=clean_text(row["record_id"]),
        )


def validate_baseline(
    dataframe: pd.DataFrame,
    report: ValidationReport,
) -> None:
    if len(dataframe) != EXPECTED_TOTAL:
        report.error(
            "BASELINE_TOTAL",
            (
                f"Expected {EXPECTED_TOTAL} records, "
                f"found {len(dataframe)}."
            ),
        )

    counts = Counter(
        dataframe["final_priority"].map(clean_text)
    )

    for priority, expected in EXPECTED_FINAL_COUNTS.items():
        actual = counts.get(priority, 0)

        if actual != expected:
            report.error(
                "BASELINE_PRIORITY_COUNT",
                (
                    f"{priority}: expected {expected}, "
                    f"found {actual}."
                ),
            )


def validate_priorities(
    dataframe: pd.DataFrame,
    report: ValidationReport,
) -> None:
    for _, row in dataframe.iterrows():
        record_id = clean_text(row["record_id"])

        suggested = clean_text(
            row["suggested_priority"]
        )

        adjudicated = clean_text(
            row["adjudicated_priority"]
        )

        final = clean_text(
            row["final_priority"]
        )

        if suggested not in ALL_PRIORITIES:
            report.error(
                "PRIORITY_SUGGESTED_INVALID",
                f"Invalid suggested_priority: {suggested!r}.",
                record_id=record_id,
            )

        if (
            adjudicated
            and adjudicated not in ALL_PRIORITIES
        ):
            report.error(
                "PRIORITY_ADJUDICATED_INVALID",
                (
                    "Invalid adjudicated_priority: "
                    f"{adjudicated!r}."
                ),
                record_id=record_id,
            )

        if final not in CENTRAL_PRIORITIES:
            report.error(
                "PRIORITY_FINAL_INVALID",
                (
                    "final_priority must be one of "
                    "A1, A2 or A3."
                ),
                record_id=record_id,
            )

        expected_final = (
            adjudicated
            if adjudicated
            else suggested
        )

        if final != expected_final:
            report.error(
                "PRIORITY_FINAL_INCONSISTENT",
                (
                    f"Expected final_priority "
                    f"{expected_final!r}, found {final!r}."
                ),
                record_id=record_id,
            )


def validate_booleans_and_abstracts(
    dataframe: pd.DataFrame,
    report: ValidationReport,
) -> None:
    for _, row in dataframe.iterrows():
        record_id = clean_text(row["record_id"])

        abstract_flag = clean_text(
            row["abstract_available"]
        ).casefold()

        second_review = clean_text(
            row["second_review_required"]
        ).casefold()

        if abstract_flag not in VALID_BOOLEANS:
            report.error(
                "ABSTRACT_FLAG_INVALID",
                (
                    "abstract_available must be "
                    "'true' or 'false'."
                ),
                record_id=record_id,
            )
        else:
            actual_available = abstract_is_available(
                row["abstract"]
            )

            expected_flag = (
                "true"
                if actual_available
                else "false"
            )

            if abstract_flag != expected_flag:
                report.error(
                    "ABSTRACT_FLAG_INCONSISTENT",
                    (
                        "abstract_available does not match "
                        "the abstract content."
                    ),
                    record_id=record_id,
                )

        if second_review not in VALID_BOOLEANS:
            report.error(
                "SECOND_REVIEW_INVALID",
                (
                    "second_review_required must be "
                    "'true' or 'false'."
                ),
                record_id=record_id,
            )

        if (
            abstract_flag == "false"
            and second_review != "true"
        ):
            report.error(
                "MISSING_ABSTRACT_REVIEW",
                (
                    "Records without abstracts must require "
                    "a second review."
                ),
                record_id=record_id,
            )

        duplicate_group = clean_text(
            row["duplicate_group"]
        )

        if (
            duplicate_group
            and second_review != "true"
        ):
            report.error(
                "DUPLICATE_REVIEW_REQUIRED",
                (
                    "Potential duplicate candidates must "
                    "require a second review."
                ),
                record_id=record_id,
            )


def validate_iso_date(
    value: str,
) -> tuple[bool, str]:
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return False, "Date must use the YYYY-MM-DD format."

    if parsed > date.today():
        return False, "Date cannot be in the future."

    return True, ""


def validate_reason_codes(
    decision: str,
    codes: list[str],
) -> tuple[bool, str]:
    if decision == "Include":
        invalid = [
            code
            for code in codes
            if code not in INCLUSION_CODES
        ]

        if invalid:
            return (
                False,
                "Include decisions require I01-I08 codes.",
            )

    elif decision == "Exclude":
        invalid = [
            code
            for code in codes
            if code not in EXCLUSION_CODES
        ]

        if invalid:
            return (
                False,
                "Exclude decisions require E01-E16 codes.",
            )

    elif decision == "Uncertain":
        invalid = [
            code
            for code in codes
            if not UNCERTAIN_CODE_PATTERN.fullmatch(code)
        ]

        if invalid:
            return (
                False,
                (
                    "Uncertain decisions require a code "
                    "in the U01-U99 format."
                ),
            )

    return True, ""


def validate_screening_decisions(
    dataframe: pd.DataFrame,
    report: ValidationReport,
) -> None:
    completion_fields = [
        "screening_reason_code",
        "screening_reason",
        "screening_evidence",
        "screened_by",
        "screening_date",
    ]

    for _, row in dataframe.iterrows():
        record_id = clean_text(row["record_id"])
        decision = clean_text(
            row["screening_decision"]
        )

        if decision not in VALID_DECISIONS:
            report.error(
                "DECISION_INVALID",
                (
                    "screening_decision must be blank, "
                    "Include, Exclude or Uncertain."
                ),
                record_id=record_id,
            )

            continue

        if not decision:
            partially_filled = [
                field
                for field in completion_fields
                if clean_text(row[field])
            ]

            if partially_filled:
                report.warning(
                    "PENDING_PARTIAL_DATA",
                    (
                        "Pending record has screening fields "
                        "already filled: "
                        + ", ".join(partially_filled)
                    ),
                    record_id=record_id,
                )

            continue

        missing = [
            field
            for field in completion_fields
            if not clean_text(row[field])
        ]

        if missing:
            report.error(
                "DECISION_INCOMPLETE",
                (
                    "Completed screening decision is missing: "
                    + ", ".join(missing)
                ),
                record_id=record_id,
            )

        codes = split_reason_codes(
            row["screening_reason_code"]
        )

        if not codes:
            report.error(
                "REASON_CODE_MISSING",
                "At least one screening reason code is required.",
                record_id=record_id,
            )
        else:
            valid_codes, message = validate_reason_codes(
                decision,
                codes,
            )

            if not valid_codes:
                report.error(
                    "REASON_CODE_INVALID",
                    message,
                    record_id=record_id,
                )

        screening_date = clean_text(
            row["screening_date"]
        )

        if screening_date:
            valid_date, date_message = validate_iso_date(
                screening_date
            )

            if not valid_date:
                report.error(
                    "SCREENING_DATE_INVALID",
                    date_message,
                    record_id=record_id,
                )

        second_review = clean_text(
            row["second_review_required"]
        ).casefold()

        if (
            decision == "Uncertain"
            and second_review != "true"
        ):
            report.error(
                "UNCERTAIN_REVIEW_REQUIRED",
                (
                    "Uncertain decisions must require "
                    "a second review."
                ),
                record_id=record_id,
            )


def validate_duplicate_groups(
    dataframe: pd.DataFrame,
    report: ValidationReport,
) -> None:
    candidates = dataframe[
        dataframe["duplicate_group"].map(clean_text) != ""
    ]

    if candidates.empty:
        report.warning(
            "DUPLICATE_GROUPS_ABSENT",
            (
                "No duplicate candidates were found. "
                "The v4.3f baseline originally contained "
                "two groups and four records."
            ),
        )

        return

    group_sizes = candidates.groupby(
        "duplicate_group"
    ).size()

    if len(group_sizes) != 2 or int(group_sizes.sum()) != 4:
        report.warning(
            "DUPLICATE_BASELINE_CHANGED",
            (
                "Expected two duplicate groups and four "
                "candidate records in the v4.3f baseline."
            ),
        )

    for duplicate_group, group in candidates.groupby(
        "duplicate_group"
    ):
        if len(group) < 2:
            report.error(
                "DUPLICATE_GROUP_SINGLETON",
                (
                    f"Duplicate group {duplicate_group!r} "
                    "contains only one record."
                ),
            )

        decisions = [
            clean_text(value)
            for value in group["screening_decision"]
        ]

        if all(decisions):
            include_count = decisions.count("Include")

            if include_count > 1:
                report.warning(
                    "DUPLICATE_MULTIPLE_INCLUDED",
                    (
                        f"Duplicate group {duplicate_group!r} "
                        "contains more than one included record."
                    ),
                )

            if include_count == 0:
                report.warning(
                    "DUPLICATE_NONE_INCLUDED",
                    (
                        f"Duplicate group {duplicate_group!r} "
                        "contains no included record."
                    ),
                )


def build_source_indexes(
    source: pd.DataFrame,
) -> tuple[
    dict[str, list[pd.Series]],
    dict[str, list[pd.Series]],
    dict[str, str | None],
]:
    columns = {
        field: resolve_column(
            source,
            aliases,
        )
        for field, aliases in SOURCE_COLUMN_ALIASES.items()
    }

    title_column = columns["title"]

    if title_column is None:
        raise ValueError(
            "The source corpus does not contain a title column."
        )

    by_doi: dict[str, list[pd.Series]] = defaultdict(list)
    by_title_year: dict[str, list[pd.Series]] = defaultdict(list)

    for _, row in source.iterrows():
        doi = normalize_doi(
            row.get(columns["doi"], "")
            if columns["doi"]
            else ""
        )

        title = normalize_title(
            row.get(title_column, "")
        )

        year = extract_year(
            row.get(columns["year"], "")
            if columns["year"]
            else ""
        )

        if doi:
            by_doi[doi].append(row)

        if title:
            by_title_year[
                f"{title}|{year}"
            ].append(row)

    return by_doi, by_title_year, columns


def select_source_candidate(
    matrix_row: pd.Series,
    by_doi: dict[str, list[pd.Series]],
    by_title_year: dict[str, list[pd.Series]],
) -> pd.Series | None:
    doi = normalize_doi(matrix_row["doi"])

    if doi and doi in by_doi:
        candidates = by_doi[doi]

        if len(candidates) == 1:
            return candidates[0]

        matrix_title = normalize_title(
            matrix_row["title"]
        )

        for candidate in candidates:
            candidate_titles = [
                normalize_title(value)
                for value in candidate.values
            ]

            if matrix_title in candidate_titles:
                return candidate

        return candidates[0]

    title_key = (
        f"{normalize_title(matrix_row['title'])}|"
        f"{extract_year(matrix_row['year'])}"
    )

    candidates = by_title_year.get(
        title_key,
        [],
    )

    if candidates:
        return candidates[0]

    return None


def normalized_field_value(
    field: str,
    value: object,
) -> str:
    if field == "title":
        return normalize_title(value)

    if field == "year":
        return extract_year(value)

    if field == "doi":
        return normalize_doi(value)

    if field == "url":
        return normalize_url(value)

    return normalize_generic_text(value)


def validate_source_integrity(
    matrix: pd.DataFrame,
    source: pd.DataFrame,
    report: ValidationReport,
) -> None:
    (
        by_doi,
        by_title_year,
        source_columns,
    ) = build_source_indexes(source)

    for _, row in matrix.iterrows():
        record_id = clean_text(row["record_id"])

        candidate = select_source_candidate(
            row,
            by_doi,
            by_title_year,
        )

        if candidate is None:
            report.error(
                "SOURCE_RECORD_NOT_FOUND",
                (
                    "Unable to match this matrix record "
                    "to the adjudicated source corpus."
                ),
                record_id=record_id,
            )

            continue

        for field in IMMUTABLE_SOURCE_FIELDS:
            source_column = source_columns.get(field)

            if source_column is None:
                continue

            matrix_value = normalized_field_value(
                field,
                row[field],
            )

            source_value = normalized_field_value(
                field,
                candidate.get(source_column, ""),
            )

            if matrix_value != source_value:
                report.error(
                    "SOURCE_FIELD_CHANGED",
                    (
                        f"Bibliographic field {field!r} differs "
                        "from the adjudicated source corpus."
                    ),
                    record_id=record_id,
                )

        source_abstract_column = source_columns.get(
            "abstract"
        )

        if source_abstract_column is None:
            continue

        matrix_abstract = normalize_generic_text(
            row["abstract"]
        )

        source_abstract = normalize_generic_text(
            candidate.get(
                source_abstract_column,
                "",
            )
        )

        if matrix_abstract != source_abstract:
            notes = normalize_generic_text(
                row["screening_notes"]
            )

            recovery_markers = (
                "abstract recovered",
                "resumo recuperado",
                "publisher",
                "source",
                "fonte",
            )

            if not any(
                marker in notes
                for marker in recovery_markers
            ):
                report.warning(
                    "ABSTRACT_CHANGED_WITHOUT_SOURCE",
                    (
                        "Abstract differs from the source corpus, "
                        "but screening_notes does not identify "
                        "the recovery or correction source."
                    ),
                    record_id=record_id,
                )


def print_summary(
    dataframe: pd.DataFrame,
    report: ValidationReport,
) -> None:
    decisions = dataframe[
        "screening_decision"
    ].map(clean_text)

    completed = int(
        (decisions != "").sum()
    )

    pending = len(dataframe) - completed

    decision_counts = Counter(
        decision or "Pending"
        for decision in decisions
    )

    second_review_count = int(
        (
            dataframe["second_review_required"]
            .map(clean_text)
            .str.casefold()
            == "true"
        ).sum()
    )

    print()
    print("Screening matrix validation")
    print("===========================")
    print(f"Records:                   {len(dataframe)}")
    print(f"Completed:                 {completed}")
    print(f"Pending:                   {pending}")
    print(f"Include:                   {decision_counts['Include']}")
    print(f"Exclude:                   {decision_counts['Exclude']}")
    print(f"Uncertain:                 {decision_counts['Uncertain']}")
    print(f"Second review required:    {second_review_count}")
    print(f"Errors:                    {len(report.errors)}")
    print(f"Warnings:                  {len(report.warnings)}")

    if report.issues:
        print()
        print("Issues")
        print("------")

        for issue in report.issues:
            record = (
                f" [{issue.record_id}]"
                if issue.record_id
                else ""
            )

            print(
                f"{issue.severity} {issue.code}"
                f"{record}: {issue.message}"
            )
    else:
        print()
        print("Validation completed successfully.")


def write_json_report(
    path: Path,
    dataframe: pd.DataFrame,
    report: ValidationReport,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "record_count": len(dataframe),
        "error_count": len(report.errors),
        "warning_count": len(report.warnings),
        "issues": [
            asdict(issue)
            for issue in report.issues
        ],
    }

    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    report = ValidationReport()

    try:
        matrix = read_csv(args.input)

        if not validate_structure(matrix, report):
            print_summary(matrix, report)

            return 1

        validate_record_ids(matrix, report)
        validate_baseline(matrix, report)
        validate_priorities(matrix, report)
        validate_booleans_and_abstracts(
            matrix,
            report,
        )
        validate_screening_decisions(
            matrix,
            report,
        )
        validate_duplicate_groups(
            matrix,
            report,
        )

        if not args.skip_source_check:
            source = read_csv(args.source)

            validate_source_integrity(
                matrix,
                source,
                report,
            )

        print_summary(matrix, report)

        if args.json_output:
            write_json_report(
                args.json_output,
                matrix,
                report,
            )

        if report.errors:
            return 1

        if args.strict and report.warnings:
            return 2

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
