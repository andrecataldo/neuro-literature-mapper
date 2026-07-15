from __future__ import annotations

import os

from neuro_mapper.models import WorkRecord
from neuro_mapper.sources.common import request_json


def reconstruct_abstract(
    inverted_index: dict | None,
) -> str:
    """Reconstrói o abstract retornado pelo OpenAlex."""

    if not inverted_index:
        return ""

    positions: list[tuple[int, str]] = []

    for word, indexes in inverted_index.items():
        for index in indexes:
            positions.append((index, word))

    return " ".join(
        word
        for _, word in sorted(positions)
    )


def search_openalex(
    query: str,
    layer_name: str,
    config: dict,
    per_page: int = 20,
) -> list[WorkRecord]:
    """Executa uma busca de trabalhos no OpenAlex."""

    api_key = os.getenv(
        "OPENALEX_API_KEY",
        "",
    ).strip()

    contact_email = os.getenv(
        "OPENALEX_CONTACT_EMAIL",
        "",
    ).strip()

    source_settings = (
        config
        .get("settings", {})
        .get("sources", {})
        .get("openalex", {})
    )

    minimum_interval = float(
        source_settings.get(
            "minimum_interval_seconds",
            0.2,
        )
    )

    max_retries = int(
        source_settings.get(
            "max_retries",
            2,
        )
    )

    params: dict[str, object] = {
        "search": query,
        "per-page": min(per_page, 100),
    }

    if api_key:
        params["api_key"] = api_key

    if contact_email:
        params["mailto"] = contact_email

    payload = request_json(
        source="OpenAlex",
        url="https://api.openalex.org/works",
        params=params,
        minimum_interval_seconds=minimum_interval,
        max_retries=max_retries,

        # Não repetimos automaticamente um 429 do OpenAlex.
        # Ele pode representar esgotamento do orçamento diário.
        retry_statuses=(500, 502, 503, 504),
    )

    results = payload.get("results", [])

    if not isinstance(results, list):
        return []

    records: list[WorkRecord] = []

    for work in results:
        if not isinstance(work, dict):
            continue

        title = work.get("title") or ""
        year = work.get("publication_year")
        doi = work.get("doi") or ""
        url = work.get("id") or ""

        primary_location = (
            work.get("primary_location")
            or {}
        )

        source_info = (
            primary_location.get("source")
            or {}
        )

        venue = (
            source_info.get("display_name")
            or ""
        )

        authors: list[str] = []

        for authorship in work.get("authorships", [])[:8]:
            author = authorship.get("author") or {}
            display_name = author.get("display_name")

            if display_name:
                authors.append(display_name)

        abstract = reconstruct_abstract(
            work.get("abstract_inverted_index")
        )

        records.append(
            WorkRecord(
                source_api="OpenAlex",
                query_layer=layer_name,
                query=query,
                title=title,
                year=year,
                authors="; ".join(authors),
                venue=venue,
                doi=doi,
                url=url,
                abstract=abstract,
                cited_by_count=work.get(
                    "cited_by_count"
                ),

                # A classificação será realizada depois,
                # pelo pipeline, após a deduplicação.
                suggested_priority="",
                suggested_tags="",
                corrente="",
            )
        )

    return records
