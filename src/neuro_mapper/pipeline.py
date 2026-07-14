from __future__ import annotations

import time
from typing import Iterable

from tqdm import tqdm

from neuro_mapper.models import WorkRecord
from neuro_mapper.sources.openalex import search_openalex
from neuro_mapper.sources.crossref import search_crossref
from neuro_mapper.sources.semantic_scholar import search_semantic_scholar


def run_api_search(config: dict) -> list[WorkRecord]:
    per_page = int(config.get("settings", {}).get("per_page", 20))
    layers = config.get("api_layers", [])

    all_records: list[WorkRecord] = []

    for layer in layers:
        layer_name = layer["name"]
        for query in layer.get("queries", []):
            for source_name, search_fn in [
                ("OpenAlex", search_openalex),
                ("Crossref", search_crossref),
                ("Semantic Scholar", search_semantic_scholar),
            ]:
                try:
                    print(f"[{source_name}] {layer_name} :: {query}")
                    records = search_fn(query, layer_name, config, per_page=per_page)
                    all_records.extend(records)
                    time.sleep(1)
                except Exception as exc:
                    print(f"ERRO em {source_name} para query {query}: {exc}")

    return deduplicate_records(all_records)


def deduplicate_records(records: Iterable[WorkRecord]) -> list[WorkRecord]:
    seen: set[str] = set()
    unique: list[WorkRecord] = []

    for record in records:
        key = ""
        if record.doi:
            key = f"doi::{record.doi.lower().strip()}"
        elif record.title:
            key = f"title::{record.title.lower().strip()}"

        if not key:
            continue

        if key not in seen:
            seen.add(key)
            unique.append(record)

    return unique
