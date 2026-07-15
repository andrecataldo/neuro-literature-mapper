from __future__ import annotations

import os

from neuro_mapper.models import WorkRecord
from neuro_mapper.sources.common import (
    normalize_semantic_scholar_query,
    request_json,
)


def search_semantic_scholar(
    query: str,
    layer_name: str,
    config: dict,
    per_page: int = 20,
) -> list[WorkRecord]:
    """Executa uma busca no Semantic Scholar."""

    api_key = os.getenv(
        "SEMANTIC_SCHOLAR_API_KEY",
        "",
    ).strip()

    headers: dict[str, str] = {}

    if api_key:
        headers["x-api-key"] = api_key

    source_settings = (
        config
        .get("settings", {})
        .get("sources", {})
        .get("semantic_scholar", {})
    )

    minimum_interval = float(
        source_settings.get(
            "minimum_interval_seconds",
            1.05,
        )
    )

    max_retries = int(
        source_settings.get(
            "max_retries",
            3,
        )
    )

    effective_query = (
        normalize_semantic_scholar_query(query)
    )

    params = {
        "query": effective_query,
        "limit": min(per_page, 100),
        "fields": (
            "title,year,authors,venue,"
            "publicationVenue,externalIds,"
            "url,abstract,citationCount"
        ),
    }

    payload = request_json(
        source="Semantic Scholar",
        url=(
            "https://api.semanticscholar.org/"
            "graph/v1/paper/search"
        ),
        params=params,
        headers=headers,
        minimum_interval_seconds=minimum_interval,
        max_retries=max_retries,
        retry_statuses=(
            429,
            500,
            502,
            503,
            504,
        ),
    )

    items = payload.get("data", [])

    if not isinstance(items, list):
        return []

    records: list[WorkRecord] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        title = item.get("title") or ""
        year = item.get("year")

        authors = "; ".join(
            author.get("name", "")
            for author in item.get("authors", [])[:8]
            if author.get("name")
        )

        venue = item.get("venue") or ""

        publication_venue = (
            item.get("publicationVenue")
            or {}
        )

        if publication_venue.get("name"):
            venue = publication_venue["name"]

        external_ids = (
            item.get("externalIds")
            or {}
        )

        doi = external_ids.get("DOI", "")
        url = item.get("url") or ""
        abstract = item.get("abstract") or ""

        records.append(
            WorkRecord(
                source_api="Semantic Scholar",
                query_layer=layer_name,

                # Preserva a query original do protocolo.
                query=query,

                title=title,
                year=year,
                authors=authors,
                venue=venue,
                doi=doi,
                url=url,
                abstract=abstract,
                cited_by_count=item.get(
                    "citationCount"
                ),

                suggested_priority="",
                suggested_tags="",
                corrente="",
            )
        )

    return records
    