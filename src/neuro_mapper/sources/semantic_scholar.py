from __future__ import annotations

import os
import requests

from neuro_mapper.models import WorkRecord
from neuro_mapper.tagging import suggest_tags, suggest_priority, infer_corrente


def search_semantic_scholar(query: str, layer_name: str, config: dict, per_page: int = 20) -> list[WorkRecord]:
    headers = {}
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "").strip()
    if api_key:
        headers["x-api-key"] = api_key

    params = {
        "query": query,
        "limit": min(per_page, 100),
        "fields": "title,year,authors,venue,publicationVenue,externalIds,url,abstract,citationCount",
    }

    response = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params=params,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    items = response.json().get("data", [])

    records: list[WorkRecord] = []

    for item in items:
        title = item.get("title") or ""
        year = item.get("year")
        authors = "; ".join([a.get("name", "") for a in item.get("authors", [])[:8] if a.get("name")])

        venue = item.get("venue") or ""
        publication_venue = item.get("publicationVenue") or {}
        if publication_venue.get("name"):
            venue = publication_venue["name"]

        external_ids = item.get("externalIds") or {}
        doi = external_ids.get("DOI", "")
        url = item.get("url", "")
        abstract = item.get("abstract") or ""

        tags = suggest_tags(config, title, venue, abstract, query)
        priority = suggest_priority(config, title, venue, query, "Semantic Scholar")
        corrente = infer_corrente(title, venue, abstract, query)

        records.append(
            WorkRecord(
                source_api="Semantic Scholar",
                query_layer=layer_name,
                query=query,
                title=title,
                year=year,
                authors=authors,
                venue=venue,
                doi=doi,
                url=url,
                abstract=abstract,
                cited_by_count=item.get("citationCount"),
                suggested_priority=priority,
                suggested_tags="; ".join(tags),
                corrente=corrente,
            )
        )

    return records
