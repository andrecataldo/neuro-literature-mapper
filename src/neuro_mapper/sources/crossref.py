from __future__ import annotations

import os

from neuro_mapper.models import WorkRecord
from neuro_mapper.sources.common import request_json


def search_crossref(
    query: str,
    layer_name: str,
    config: dict,
    per_page: int = 20,
) -> list[WorkRecord]:
    """Executa uma busca de trabalhos no Crossref."""

    contact_email = os.getenv(
        "CROSSREF_CONTACT_EMAIL",
        "",
    ).strip()

    user_agent = os.getenv(
        "NEURO_MAPPER_USER_AGENT",
        "neuro-literature-mapper/0.1",
    ).strip()

    if contact_email and "mailto:" not in user_agent:
        user_agent = (
            f"{user_agent} "
            f"(mailto:{contact_email})"
        )

    headers = {
        "User-Agent": user_agent,
    }

    source_settings = (
        config
        .get("settings", {})
        .get("sources", {})
        .get("crossref", {})
    )

    minimum_interval = float(
        source_settings.get(
            "minimum_interval_seconds",
            0.25,
        )
    )

    max_retries = int(
        source_settings.get(
            "max_retries",
            3,
        )
    )

    params: dict[str, object] = {
        "query": query,
        "rows": per_page,
    }

    if contact_email:
        params["mailto"] = contact_email

    payload = request_json(
        source="Crossref",
        url="https://api.crossref.org/works",
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

    message = payload.get("message", {})

    if not isinstance(message, dict):
        return []

    items = message.get("items", [])

    if not isinstance(items, list):
        return []

    records: list[WorkRecord] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        raw_title = item.get("title") or []

        if isinstance(raw_title, list):
            title = " ".join(raw_title)
        else:
            title = str(raw_title)

        year = None

        date_data = item.get(
            "published-print",
            item.get(
                "published-online",
                item.get("issued", {}),
            ),
        )

        date_parts = (
            date_data.get("date-parts", [])
            if isinstance(date_data, dict)
            else []
        )

        if date_parts and date_parts[0]:
            year = date_parts[0][0]

        authors: list[str] = []

        for author in item.get("author", [])[:8]:
            given = author.get("given", "")
            family = author.get("family", "")

            full_name = (
                f"{given} {family}"
                .strip()
            )

            if full_name:
                authors.append(full_name)

        venue = ""
        container = item.get("container-title") or []

        if container:
            venue = container[0]

        doi = item.get("DOI") or ""
        url = item.get("URL") or ""
        abstract = item.get("abstract") or ""

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
                cited_by_count=item.get(
                    "is-referenced-by-count"
                ),
                suggested_priority="",
                suggested_tags="",
                corrente="",
            )
        )

    return records
    