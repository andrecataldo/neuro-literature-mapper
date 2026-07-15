from __future__ import annotations

import re
import time
import unicodedata
from copy import deepcopy
from typing import Iterable

from neuro_mapper.models import WorkRecord
from neuro_mapper.sources.crossref import search_crossref
from neuro_mapper.sources.openalex import search_openalex
from neuro_mapper.sources.semantic_scholar import search_semantic_scholar
from neuro_mapper.tagging import infer_corrente, suggest_priority, suggest_tags


SOURCE_QUALITY = {
    "openalex": 3,
    "semantic scholar": 2,
    "crossref": 1,
}


def run_api_search(config: dict) -> list[WorkRecord]:
    """
    Executa as buscas, aplica o filtro temporal, deduplica e só então classifica.

    A query é preservada para rastreabilidade, mas não é usada para sugerir
    tags, corrente ou prioridade.
    """
    settings = config.get("settings", {})
    per_page = int(settings.get("per_page", 20))
    layers = config.get("api_layers", [])

    all_records: list[WorkRecord] = []

    for layer in layers:
        layer_name = str(layer.get("name", "")).strip()

        for query in layer.get("queries", []):
            for source_name, search_fn in [
                ("OpenAlex", search_openalex),
                ("Crossref", search_crossref),
                ("Semantic Scholar", search_semantic_scholar),
            ]:
                try:
                    print(f"[{source_name}] {layer_name} :: {query}")
                    records = search_fn(
                        query,
                        layer_name,
                        config,
                        per_page=per_page,
                    )
                    all_records.extend(records)
                    time.sleep(float(settings.get("request_delay_seconds", 1)))
                except Exception as exc:
                    print(
                        f"ERRO em {source_name} para query {query}: {exc}"
                    )

    filtered = filter_records_by_year(all_records, config)
    unique = deduplicate_records(filtered)

    return classify_records(unique, config)


def filter_records_by_year(
    records: Iterable[WorkRecord],
    config: dict,
) -> list[WorkRecord]:
    """
    Aplica `year_min` e `year_max` após a recuperação.

    Registros sem ano são mantidos para revisão manual. O filtro pode ser
    desativado com `settings.enforce_year_filter: false`.
    """
    settings = config.get("settings", {})

    if not bool(settings.get("enforce_year_filter", True)):
        return list(records)

    year_min = _optional_int(settings.get("year_min"))
    year_max = _optional_int(settings.get("year_max"))

    filtered: list[WorkRecord] = []

    for record in records:
        if record.year is None:
            filtered.append(record)
            continue

        if year_min is not None and record.year < year_min:
            continue

        if year_max is not None and record.year > year_max:
            continue

        filtered.append(record)

    return filtered


def classify_records(
    records: Iterable[WorkRecord],
    config: dict,
) -> list[WorkRecord]:
    """
    Recalcula classificação usando somente conteúdo e metadados do artigo.

    A query de busca não entra no texto classificatório. Isso impede que os
    termos da consulta façam um artigo irrelevante parecer central.
    """
    classified: list[WorkRecord] = []

    for record in records:
        content_parts = (
            record.title,
            record.abstract,
            record.venue,
        )

        record.suggested_priority = suggest_priority(
            config=config,
            title=record.title,
            venue=record.venue,
            query="",
            source_api=record.source_api,
            abstract=record.abstract,
        )
        record.suggested_tags = "; ".join(
            suggest_tags(config, *content_parts)
        )
        record.corrente = infer_corrente(*content_parts)
        record.classification_confidence = infer_classification_confidence(
            record
        )
        classified.append(record)

    return classified


def infer_classification_confidence(record: WorkRecord) -> str:
    """
    Estima a confiança da triagem automática com base na completude.

    - high: resumo informativo e venue disponível;
    - medium: resumo curto ou venue ausente;
    - low: sem resumo.
    """
    abstract = (record.abstract or "").strip()
    venue = (record.venue or "").strip()

    if not abstract:
        return "low"

    if len(abstract) >= 200 and venue:
        return "high"

    return "medium"


def deduplicate_records(
    records: Iterable[WorkRecord],
) -> list[WorkRecord]:
    """
    Deduplica por DOI normalizado e por título normalizado.

    Quando várias fontes descrevem o mesmo trabalho, preserva o registro mais
    completo e combina proveniência, queries e metadados complementares.
    """
    groups: list[list[WorkRecord]] = []
    doi_to_group: dict[str, int] = {}
    title_to_group: dict[str, int] = {}

    for record in records:
        doi_key = normalize_doi(record.doi)
        title_key = normalize_title(record.title)

        matching_groups = {
            group_index
            for key, mapping in (
                (doi_key, doi_to_group),
                (title_key, title_to_group),
            )
            if key and (group_index := mapping.get(key)) is not None
        }

        if not matching_groups:
            group_index = len(groups)
            groups.append([record])
        else:
            group_index = min(matching_groups)
            groups[group_index].append(record)

            # Se DOI e título apontaram para grupos distintos, unifique-os.
            for other_index in sorted(matching_groups - {group_index}, reverse=True):
                groups[group_index].extend(groups[other_index])
                groups[other_index] = []

                for mapping in (doi_to_group, title_to_group):
                    for key, index in list(mapping.items()):
                        if index == other_index:
                            mapping[key] = group_index

        if doi_key:
            doi_to_group[doi_key] = group_index

        if title_key:
            title_to_group[title_key] = group_index

    return [
        merge_duplicate_group(group)
        for group in groups
        if group
    ]


def merge_duplicate_group(records: list[WorkRecord]) -> WorkRecord:
    """Combina registros duplicados priorizando metadados mais completos."""
    if not records:
        raise ValueError("O grupo de duplicatas não pode ser vazio.")

    ranked = sorted(
        records,
        key=record_quality_score,
        reverse=True,
    )
    merged = deepcopy(ranked[0])

    merged.source_api = _join_unique(
        record.source_api for record in records
    )
    merged.query_layer = _join_unique(
        record.query_layer for record in records
    )
    merged.query = _join_unique(
        record.query for record in records
    )

    merged.title = _best_text(records, "title", prefer_longest=False)
    merged.authors = _best_text(records, "authors", prefer_longest=True)
    merged.venue = _best_text(records, "venue", prefer_longest=False)
    merged.abstract = _best_text(records, "abstract", prefer_longest=True)
    merged.notes = _join_unique(record.notes for record in records)
    merged.decision = _first_nonempty(record.decision for record in ranked)

    merged.seed_source = _join_unique(
        (
            record.seed_source or record.professor_source
            for record in records
        )
    )
    merged.professor_source = ""

    merged.doi = _first_nonempty(
        normalize_doi(record.doi) for record in ranked
    )
    merged.url = _select_url(ranked, merged.doi)
    merged.year = _first_non_none(record.year for record in ranked)

    citation_counts = [
        record.cited_by_count
        for record in records
        if record.cited_by_count is not None
    ]
    merged.cited_by_count = max(citation_counts) if citation_counts else None

    merged.duplicate_count = sum(
        max(1, int(getattr(record, "duplicate_count", 1)))
        for record in records
    )

    # A classificação será recalculada após a deduplicação.
    merged.suggested_priority = ""
    merged.suggested_tags = ""
    merged.corrente = ""
    merged.classification_confidence = ""

    return merged


def record_quality_score(record: WorkRecord) -> tuple[int, int, int]:
    """Pontua completude e confiabilidade relativa do registro."""
    score = 0

    if normalize_doi(record.doi):
        score += 6
    if record.abstract.strip():
        score += 6
    if record.venue.strip():
        score += 4
    if record.authors.strip():
        score += 3
    if record.url.strip():
        score += 2
    if record.year is not None:
        score += 2
    if record.cited_by_count is not None:
        score += 1

    source_score = max(
        (
            SOURCE_QUALITY.get(source.strip().lower(), 0)
            for source in record.source_api.split("|")
        ),
        default=0,
    )

    return score, source_score, len(record.abstract or "")


def normalize_doi(doi: str | None) -> str:
    """Normaliza DOI removendo URL, prefixo e pontuação externa."""
    value = (doi or "").strip().lower()

    value = re.sub(
        r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)",
        "",
        value,
    )
    return value.strip().rstrip(".,;)")


def normalize_title(title: str | None) -> str:
    """Normaliza título para deduplicação exata tolerante a pontuação."""
    value = unicodedata.normalize("NFKD", title or "")
    value = "".join(
        character
        for character in value
        if not unicodedata.combining(character)
    )
    value = value.casefold()

    # Remove marcadores finais de versão, mas não remove "Review of".
    value = re.sub(
        r"^(?:preprint|accepted manuscript)\s*[:\-]?\s*",
        "",
        value,
    )
    value = re.sub(
        r"\s*[\[(]?(?:preprint|accepted manuscript)[\])]?$",
        "",
        value,
    )
    value = re.sub(r"\b(?:version|v)\s*\d+\b\s*$", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _select_url(
    ranked_records: list[WorkRecord],
    doi: str,
) -> str:
    if doi:
        return f"https://doi.org/{doi}"

    return _first_nonempty(
        record.url.strip() for record in ranked_records
    )


def _best_text(
    records: list[WorkRecord],
    field_name: str,
    *,
    prefer_longest: bool,
) -> str:
    values = [
        str(getattr(record, field_name, "") or "").strip()
        for record in records
    ]
    values = [value for value in values if value]

    if not values:
        return ""

    if prefer_longest:
        return max(values, key=len)

    ranked_records = sorted(
        records,
        key=record_quality_score,
        reverse=True,
    )
    return _first_nonempty(
        str(getattr(record, field_name, "") or "").strip()
        for record in ranked_records
    )


def _join_unique(values: Iterable[str]) -> str:
    unique: list[str] = []
    seen: set[str] = set()

    for value in values:
        for part in str(value or "").split("|"):
            cleaned = part.strip()
            key = cleaned.casefold()

            if cleaned and key not in seen:
                seen.add(key)
                unique.append(cleaned)

    return " | ".join(unique)


def _first_nonempty(values: Iterable[str]) -> str:
    return next((value for value in values if value), "")


def _first_non_none(values: Iterable[int | None]) -> int | None:
    return next((value for value in values if value is not None), None)


def _optional_int(value: object) -> int | None:
    if value in (None, ""):
        return None

    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Valor de ano inválido na configuração: {value!r}"
        ) from exc
