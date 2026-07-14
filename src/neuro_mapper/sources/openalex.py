from __future__ import annotations

import os
from urllib.parse import quote

import requests

from neuro_mapper.models import WorkRecord
from neuro_mapper.tagging import suggest_tags, suggest_priority, infer_corrente


def reconstruct_abstract(inverted_index: dict | None) -> str:
    if not inverted_index:
        return ""

    positions = []
    for word, indexes in inverted_index.items():
        for index in indexes:
            positions.append((index, word))

    return " ".join(word for _, word in sorted(positions))


def search_openalex(query: str, layer_name: str, config: dict, per_page: int = 20) -> list[WorkRecord]:
    contact_email = os.getenv("CONTACT_EMAIL", "").strip()

    params = {
        "search": query,
        "per-page": per_page,
    }

    if contact_email:
        params["mailto"] = contact_email

    response = requests.get(
        "https://api.openalex.org/works",
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    results = response.json().get("results", [])

    records: list[WorkRecord] = []

    for work in results:
        title = work.get("title") or ""
        year = work.get("publication_year")
        doi = work.get("doi") or ""
        url = work.get("id") or ""

        primary_location = work.get("primary_location") or {}
        source_info = primary_location.get("source") or {}
        venue = source_info.get("display_name") or ""

        authors = []
        for authorship in work.get("authorships", [])[:8]:
            author = authorship.get("author") or {}
            if author.get("display_name"):
                authors.append(author["display_name"])

        abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
        tags = suggest_tags(config, title, venue, abstract, query)
        priority = suggest_priority(config, title, venue, query, "OpenAlex")
        corrente = infer_corrente(title, venue, abstract, query)

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
                cited_by_count=work.get("cited_by_count"),
                suggested_priority=priority,
                suggested_tags="; ".join(tags),
                corrente=corrente,
            )
        )

    return records
