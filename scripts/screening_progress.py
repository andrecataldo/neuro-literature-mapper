#!/usr/bin/env python3
"""Report the progress of title-and-abstract screening.

The script reads the screening matrix and reports:

- overall screening completion;
- Include, Exclude, Uncertain and Pending counts;
- progress by A1, A3 and A2;
- records without abstracts;
- potential duplicate groups;
- records marked for second review;
- optional JSON and CSV summaries.

The screening matrix is never modified.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_INPUT = Path(
    "outputs/matriz_triagem_neuro_v4_3f.csv"
)

PRIORITY_LABELS = {
    "A1": "A1-central-integracao-llm",
    "A2": "A2-central-decoding-linguagem",
    "A3": "A3-central-riscos-governanca",
}

PRIORITY_ORDER = [
    "A1",
    "A3",
    "A2",
]

EXPECTED_COUNTS = {
    "A1": 71,
    "A3": 63,
    "A2": 120,
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

REQUIRED_COLUMNS = {
    "record_id",
    "title",
    "year",
    "abstract_available",
    "final_priority",
    "screening_decision",
    "second_review_required",
    "duplicate_group",
}

PRIORITY_DISPLAY_NAMES = {
    "A1": "Integration BMI/BCI-language model",
    "A3": "Risks and governance",
    "A2": "Neural language decoding",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Report progress for the title-and-abstract "
            "screening matrix."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Screening matrix CSV.",
    )

    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional destination for a JSON progress report.",
    )

    parser.add_argument(
        "--csv-output",
        type=Path,
        help="Optional destination for a long-format CSV summary.",
    )

    parser.add_argument(
        "--pending-limit",
        type=int,
        default=0,
        help=(
            "Show the first N pending records in matrix order. "
            "Use 0 to omit the list."
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


def read_csv(path: Path) -> pd.DataFrame:
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


def validate_minimum_structure(
    dataframe: pd.DataFrame,
) -> None:
    missing = sorted(
        REQUIRED_COLUMNS - set(dataframe.columns)
    )

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
        )

    if dataframe["record_id"].map(clean_text).eq("").any():
        raise ValueError(
            "The matrix contains blank record_id values."
        )

    if not dataframe["record_id"].is_unique:
        raise ValueError(
            "The matrix contains duplicated record_id values."
        )

    decisions = {
        clean_text(value)
        for value in dataframe["screening_decision"]
    }

    invalid_decisions = sorted(
        decisions - VALID_DECISIONS
    )

    if invalid_decisions:
        raise ValueError(
            "Invalid screening_decision values: "
            + ", ".join(invalid_decisions)
        )

    for column in (
        "abstract_available",
        "second_review_required",
    ):
        values = {
            clean_text(value).casefold()
            for value in dataframe[column]
        }

        invalid = sorted(
            values - VALID_BOOLEANS
        )

        if invalid:
            raise ValueError(
                f"Invalid {column} values: "
                + ", ".join(invalid)
            )

    valid_priorities = set(
        PRIORITY_LABELS.values()
    )

    priorities = {
        clean_text(value)
        for value in dataframe["final_priority"]
    }

    invalid_priorities = sorted(
        priorities - valid_priorities
    )

    if invalid_priorities:
        raise ValueError(
            "Invalid final_priority values: "
            + ", ".join(invalid_priorities)
        )


def percentage(
    numerator: int,
    denominator: int,
) -> float:
    if denominator == 0:
        return 0.0

    return round(
        (numerator / denominator) * 100,
        1,
    )


def decision_counts(
    dataframe: pd.DataFrame,
) -> dict[str, int]:
    values = [
        clean_text(value) or "Pending"
        for value in dataframe["screening_decision"]
    ]

    counts = Counter(values)

    return {
        "Include": counts.get("Include", 0),
        "Exclude": counts.get("Exclude", 0),
        "Uncertain": counts.get("Uncertain", 0),
        "Pending": counts.get("Pending", 0),
    }


def priority_code(
    final_priority: object,
) -> str:
    normalized = clean_text(final_priority)

    for code, label in PRIORITY_LABELS.items():
        if normalized == label:
            return code

    raise ValueError(
        f"Unknown final priority: {final_priority!r}"
    )


def build_priority_progress(
    dataframe: pd.DataFrame,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for code in PRIORITY_ORDER:
        subset = dataframe[
            dataframe["final_priority"]
            == PRIORITY_LABELS[code]
        ]

        counts = decision_counts(subset)
        total = len(subset)
        completed = total - counts["Pending"]

        rows.append(
            {
                "priority": code,
                "name": PRIORITY_DISPLAY_NAMES[code],
                "expected": EXPECTED_COUNTS[code],
                "total": total,
                "completed": completed,
                "pending": counts["Pending"],
                "include": counts["Include"],
                "exclude": counts["Exclude"],
                "uncertain": counts["Uncertain"],
                "progress_percent": percentage(
                    completed,
                    total,
                ),
            }
        )

    return rows


def build_abstract_progress(
    dataframe: pd.DataFrame,
) -> dict[str, int]:
    abstract_available = (
        dataframe["abstract_available"]
        .map(clean_text)
        .str.casefold()
    )

    decisions = dataframe[
        "screening_decision"
    ].map(clean_text)

    missing = abstract_available == "false"
    available = abstract_available == "true"
    screened = decisions != ""
    pending = decisions == ""
    uncertain = decisions == "Uncertain"

    return {
        "available_total": int(available.sum()),
        "missing_total": int(missing.sum()),
        "missing_pending": int(
            (missing & pending).sum()
        ),
        "missing_screened": int(
            (missing & screened).sum()
        ),
        "missing_uncertain": int(
            (missing & uncertain).sum()
        ),
    }


def build_duplicate_progress(
    dataframe: pd.DataFrame,
) -> dict[str, int]:
    duplicate_groups = dataframe[
        "duplicate_group"
    ].map(clean_text)

    candidates = dataframe[
        duplicate_groups != ""
    ].copy()

    if candidates.empty:
        return {
            "groups_total": 0,
            "records_total": 0,
            "groups_pending": 0,
            "groups_resolved": 0,
            "groups_ambiguous": 0,
            "records_pending": 0,
        }

    groups_pending = 0
    groups_resolved = 0
    groups_ambiguous = 0
    records_pending = 0

    for _, group in candidates.groupby(
        "duplicate_group",
        sort=True,
    ):
        decisions = [
            clean_text(value)
            for value in group["screening_decision"]
        ]

        pending_count = decisions.count("")
        include_count = decisions.count("Include")

        records_pending += pending_count

        if pending_count > 0:
            groups_pending += 1
        elif include_count == 1:
            groups_resolved += 1
        else:
            groups_ambiguous += 1

    return {
        "groups_total": int(
            candidates["duplicate_group"].nunique()
        ),
        "records_total": len(candidates),
        "groups_pending": groups_pending,
        "groups_resolved": groups_resolved,
        "groups_ambiguous": groups_ambiguous,
        "records_pending": records_pending,
    }


def build_second_review_progress(
    dataframe: pd.DataFrame,
) -> dict[str, int]:
    flags = (
        dataframe["second_review_required"]
        .map(clean_text)
        .str.casefold()
        == "true"
    )

    decisions = dataframe[
        "screening_decision"
    ].map(clean_text)

    pending_initial = decisions == ""
    screened = decisions != ""
    uncertain = decisions == "Uncertain"

    return {
        "flagged_total": int(flags.sum()),
        "awaiting_initial_screening": int(
            (flags & pending_initial).sum()
        ),
        "screened_but_still_flagged": int(
            (flags & screened).sum()
        ),
        "uncertain_flagged": int(
            (flags & uncertain).sum()
        ),
    }


def build_report(
    dataframe: pd.DataFrame,
    *,
    input_path: Path,
) -> dict[str, Any]:
    counts = decision_counts(dataframe)

    total = len(dataframe)
    completed = total - counts["Pending"]

    return {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "input": str(input_path),
        "overall": {
            "total": total,
            "completed": completed,
            "pending": counts["Pending"],
            "progress_percent": percentage(
                completed,
                total,
            ),
        },
        "decisions": {
            "include": counts["Include"],
            "exclude": counts["Exclude"],
            "uncertain": counts["Uncertain"],
            "pending": counts["Pending"],
        },
        "priorities": build_priority_progress(
            dataframe
        ),
        "abstracts": build_abstract_progress(
            dataframe
        ),
        "duplicates": build_duplicate_progress(
            dataframe
        ),
        "second_review": (
            build_second_review_progress(
                dataframe
            )
        ),
    }


def print_table(
    headers: list[str],
    rows: list[list[str]],
) -> None:
    widths = [
        len(header)
        for header in headers
    ]

    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(
                widths[index],
                len(value),
            )

    header_line = "  ".join(
        header.ljust(widths[index])
        for index, header in enumerate(headers)
    )

    separator = "  ".join(
        "-" * width
        for width in widths
    )

    print(header_line)
    print(separator)

    for row in rows:
        print(
            "  ".join(
                value.ljust(widths[index])
                for index, value in enumerate(row)
            )
        )


def print_report(
    report: dict[str, Any],
    dataframe: pd.DataFrame,
    *,
    pending_limit: int,
) -> None:
    overall = report["overall"]
    decisions = report["decisions"]
    abstracts = report["abstracts"]
    duplicates = report["duplicates"]
    second_review = report["second_review"]

    print()
    print("Screening progress")
    print("==================")
    print(f"Input:      {report['input']}")
    print(f"Total:      {overall['total']}")
    print(f"Completed:  {overall['completed']}")
    print(f"Pending:    {overall['pending']}")
    print(
        "Progress:   "
        f"{overall['progress_percent']:.1f}%"
    )

    print()
    print("Decisions")
    print("---------")
    print(f"Include:    {decisions['include']}")
    print(f"Exclude:    {decisions['exclude']}")
    print(f"Uncertain:  {decisions['uncertain']}")
    print(f"Pending:    {decisions['pending']}")

    print()
    print("Progress by priority")
    print("--------------------")

    priority_rows = []

    for item in report["priorities"]:
        priority_rows.append(
            [
                item["priority"],
                str(item["total"]),
                str(item["completed"]),
                str(item["pending"]),
                str(item["include"]),
                str(item["exclude"]),
                str(item["uncertain"]),
                f"{item['progress_percent']:.1f}%",
            ]
        )

    print_table(
        [
            "Priority",
            "Total",
            "Done",
            "Pending",
            "Include",
            "Exclude",
            "Uncertain",
            "Progress",
        ],
        priority_rows,
    )

    print()
    print("Abstract coverage")
    print("-----------------")
    print(
        "Available abstracts:      "
        f"{abstracts['available_total']}"
    )
    print(
        "Missing abstracts:        "
        f"{abstracts['missing_total']}"
    )
    print(
        "Missing and pending:       "
        f"{abstracts['missing_pending']}"
    )
    print(
        "Missing but screened:      "
        f"{abstracts['missing_screened']}"
    )
    print(
        "Missing and uncertain:     "
        f"{abstracts['missing_uncertain']}"
    )

    print()
    print("Potential duplicates")
    print("--------------------")
    print(
        "Groups:                   "
        f"{duplicates['groups_total']}"
    )
    print(
        "Records:                  "
        f"{duplicates['records_total']}"
    )
    print(
        "Groups with pending work: "
        f"{duplicates['groups_pending']}"
    )
    print(
        "Resolved groups:          "
        f"{duplicates['groups_resolved']}"
    )
    print(
        "Ambiguous groups:         "
        f"{duplicates['groups_ambiguous']}"
    )
    print(
        "Pending records:          "
        f"{duplicates['records_pending']}"
    )

    print()
    print("Second-review flags")
    print("-------------------")
    print(
        "Flagged records:              "
        f"{second_review['flagged_total']}"
    )
    print(
        "Awaiting initial screening:   "
        f"{second_review['awaiting_initial_screening']}"
    )
    print(
        "Screened but still flagged:   "
        f"{second_review['screened_but_still_flagged']}"
    )
    print(
        "Uncertain and flagged:        "
        f"{second_review['uncertain_flagged']}"
    )

    print()
    print(
        "Note: the current matrix has no "
        "second_review_completed field. "
        "A flagged record cannot yet be reported "
        "as having completed its second review."
    )

    if pending_limit > 0:
        pending = dataframe[
            dataframe["screening_decision"]
            .map(clean_text)
            == ""
        ].head(pending_limit)

        print()
        print(
            f"First {min(pending_limit, len(pending))} "
            "pending records"
        )
        print("-" * 24)

        for _, row in pending.iterrows():
            code = priority_code(
                row["final_priority"]
            )

            year = clean_text(row["year"]) or "N/A"

            print(
                f"{clean_text(row['record_id'])} | "
                f"{code} | {year} | "
                f"{clean_text(row['title'])}"
            )


def write_json_report(
    path: Path,
    report: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def summary_rows(
    report: dict[str, Any],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for metric, value in report["overall"].items():
        rows.append(
            {
                "section": "overall",
                "group": "",
                "metric": metric,
                "value": value,
            }
        )

    for metric, value in report["decisions"].items():
        rows.append(
            {
                "section": "decisions",
                "group": "",
                "metric": metric,
                "value": value,
            }
        )

    for priority in report["priorities"]:
        code = priority["priority"]

        for metric, value in priority.items():
            if metric in {
                "priority",
                "name",
            }:
                continue

            rows.append(
                {
                    "section": "priorities",
                    "group": code,
                    "metric": metric,
                    "value": value,
                }
            )

    for section in (
        "abstracts",
        "duplicates",
        "second_review",
    ):
        for metric, value in report[section].items():
            rows.append(
                {
                    "section": section,
                    "group": "",
                    "metric": metric,
                    "value": value,
                }
            )

    return rows


def write_csv_report(
    path: Path,
    report: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe = pd.DataFrame(
        summary_rows(report),
        columns=[
            "section",
            "group",
            "metric",
            "value",
        ],
    )

    dataframe.to_csv(
        path,
        index=False,
        encoding="utf-8-sig",
        lineterminator="\n",
    )


def main() -> int:
    args = parse_args()

    if args.pending_limit < 0:
        print(
            "ERROR: --pending-limit cannot be negative.",
            file=sys.stderr,
        )

        return 2

    try:
        dataframe = read_csv(args.input)

        validate_minimum_structure(dataframe)

        report = build_report(
            dataframe,
            input_path=args.input,
        )

        print_report(
            report,
            dataframe,
            pending_limit=args.pending_limit,
        )

        if args.json_output:
            write_json_report(
                args.json_output,
                report,
            )

            print()
            print(
                "JSON report: "
                f"{args.json_output}"
            )

        if args.csv_output:
            write_csv_report(
                args.csv_output,
                report,
            )

            print(
                "CSV report:  "
                f"{args.csv_output}"
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
