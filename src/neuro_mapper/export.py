from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd

from neuro_mapper.models import WorkRecord


def records_to_dataframe(records: list[WorkRecord]) -> pd.DataFrame:
    """
    Converte registros em DataFrame com ordem estável de colunas.

    Mesmo sem resultados, o DataFrame mantém os cabeçalhos esperados.
    """
    rows = [record.to_dict() for record in records]
    return pd.DataFrame(rows, columns=WorkRecord.CSV_FIELDS)


def export_records_csv(
    records: list[WorkRecord],
    output_path: str | Path,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    dataframe = records_to_dataframe(records)
    dataframe.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
        lineterminator="\n",
    )


def _collect_fieldnames(rows: list[dict[str, Any]]) -> list[str]:
    """Coleta todas as colunas preservando a ordem da primeira ocorrência."""
    fieldnames: list[str] = []
    seen: set[str] = set()

    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)

    return fieldnames


def export_rows_csv(
    rows: list[dict[str, Any]],
    output_path: str | Path,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        output_path.write_text("", encoding="utf-8")
        return

    fieldnames = _collect_fieldnames(rows)

    with output_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
