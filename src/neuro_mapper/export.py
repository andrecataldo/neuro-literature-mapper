from __future__ import annotations

from pathlib import Path
import csv

import pandas as pd

from neuro_mapper.models import WorkRecord


def records_to_dataframe(records: list[WorkRecord]) -> pd.DataFrame:
    return pd.DataFrame([record.to_dict() for record in records])


def export_records_csv(records: list[WorkRecord], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = records_to_dataframe(records)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")


def export_rows_csv(rows: list[dict], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        output_path.write_text("", encoding="utf-8")
        return

    with output_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
