from __future__ import annotations

import re


def normalize_text(*parts: str | None) -> str:
    return " ".join([p or "" for p in parts]).lower()


def suggest_tags(config: dict, *parts: str | None) -> list[str]:
    text = normalize_text(*parts)
    tags_config = config.get("tags", {})
    tags = set()

    for tag, keywords in tags_config.items():
        for keyword in keywords:
            if keyword.lower() in text:
                tags.add(tag)
                break

    return sorted(tags)


def contains_any(text: str, values: list[str]) -> bool:
    lower = text.lower()
    return any(value.lower() in lower for value in values)


def suggest_priority(config: dict, title: str, venue: str, query: str, source_api: str = "") -> str:
    text = normalize_text(title, venue, query, source_api)
    classification = config.get("classification", {})

    if contains_any(text, classification.get("si_venues", [])):
        return "A-central"

    if "information systems" in text and any(
        term in text
        for term in [
            "generative ai",
            "large language model",
            "llm",
            "chatgpt",
            "decision",
            "trust",
            "cognitive bias",
            "human-ai",
        ]
    ):
        return "A-central"

    if contains_any(text, classification.get("support_venues", [])):
        return "B-apoio"

    if contains_any(text, classification.get("caution_sources", [])):
        return "C-cautela"

    if any(term in text for term in ["technical architecture", "benchmark", "model performance"]) and not any(
        term in text for term in ["user", "decision", "trust", "information systems", "human-ai"]
    ):
        return "D-descartar"

    return "B-apoio"


def infer_corrente(*parts: str | None) -> str:
    text = normalize_text(*parts)

    if any(term in text for term in ["trust", "reliance", "overreliance", "algorithm aversion", "algorithm appreciation"]):
        return "Interação Humano-IA, Confiança e Decisão"

    if any(term in text for term in ["cognitive bias", "confirmation bias", "anchoring bias", "automation bias", "availability bias"]):
        return "Vieses Cognitivos na Interação com IA"

    if any(term in text for term in ["generative ai", "large language model", "llm", "chatgpt"]):
        return "IA Generativa e LLMs em SI"

    if any(term in text for term in ["governance", "risk", "information quality", "explainability"]):
        return "Qualidade Informacional, Decisão e Governança"

    return "Literatura central de SI / A classificar"
