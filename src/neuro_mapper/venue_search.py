from __future__ import annotations

from urllib.parse import quote_plus
from datetime import date


def build_google_search_url(query: str) -> str:
    return "https://www.google.com/search?q=" + quote_plus(query)


def build_google_scholar_url(query: str) -> str:
    return "https://scholar.google.com/scholar?q=" + quote_plus(query)


def generate_venue_searches(config: dict) -> list[dict]:
    rows = []
    today = date.today().isoformat()

    for layer in config.get("venue_search_layers", []):
        venue_group = layer.get("venue_group", "")
        base_site = layer.get("base_site", "")

        for raw_query in layer.get("queries", []):
            if base_site:
                query = f"site:{base_site} {raw_query}"
            else:
                query = raw_query

            rows.append(
                {
                    "date": today,
                    "venue_group": venue_group,
                    "base_site": base_site,
                    "query": query,
                    "google_url": build_google_search_url(query),
                    "google_scholar_url": build_google_scholar_url(query),
                    "approx_results": "",
                    "selected_articles": "",
                    "discarded_articles": "",
                    "notes": "",
                    "status": "a_executar",
                }
            )

    return rows
