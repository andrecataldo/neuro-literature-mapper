from __future__ import annotations

import os
import requests

from neuro_mapper.models import WorkRecord
from neuro_mapper.tagging import suggest_tags, suggest_priority, infer_corrente


def search_crossref(query: str, layer_name: str, config: dict, per_page: int = 20) -> list[WorkRecord]:
    contact_email = os.getenv("CONTACT_EMAIL", "").strip()

    params = {
        "query": query,
        "rows": per_page,
    }

    if contact_email:
        params["mailto"] = contact_email

    response = requests.get("https://api.crossref.org/works", params=params, timeout=30)
    response.raise_for_status()
    items = response.json().get("message", {}).get("items", [])

    records: list[WorkRecord] = []

    for item in items:
        title = " ".join(item.get("title") or []) if isinstance(item.get("title"), list) else item.get("title", "")
        year = None

        date_parts = item.get("published-print", item.get("published-online", item.get("issued", {}))).get("date-parts", [])
        if date_parts and date_parts[0]:
            year = date_parts[0][0]

        authors = []
        for author in item.get("author", [])[:8]:
            given = author.get("given", "")
            family = author.get("family", "")
            full_name = f"{given} {family}".strip()
            if full_name:
                authors.append(full_name)

        venue = ""
        container = item.get("container-title") or []
        if container:
            venue = container[0]

        doi = item.get("DOI", "")
        url = item.get("URL", "")
        abstract = item.get("abstract", "")

        tags = suggest_tags(config, title, venue, abstract, query)
        priority = suggest_priority(config, title, venue, query, "Crossref")
        corrente = infer_corrente(title, venue, abstract, query)

        records.append(
            WorkRecord(
                source_api="Crossref",
                query_layer=layer_name,
                query=query,
                title=title,
                year=year,
                authors="; ".join(authors),
                venue=venue,
                doi=doi,
                url=url,
                abstract=abstract,
                cited_by_count=item.get("is-referenced-by-count"),
                suggested_priority=priority,
                suggested_tags="; ".join(tags),
                corrente=corrente,
            )
        )

    return records
