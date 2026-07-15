from __future__ import annotations

import re
from collections.abc import Iterable


INTERFACE_PHRASES = [
    "brain-computer interface",
    "brain computer interface",
    "brain-machine interface",
    "brain machine interface",
    "neural interface",
    "brain interface",
]

INTERFACE_ABBREVIATIONS = ["bci", "bmi"]

INTERFACE_CONTEXT_TERMS = [
    "brain",
    "neural",
    "eeg",
    "ecog",
    "fmri",
    "intracortical",
    "p300",
    "ssvep",
    "motor imagery",
    "neurotechnology",
    "neuroengineering",
    "interface",
]

BROAD_NEURO_TERMS = [
    "neurotechnology",
    "neuroengineering",
    "neural engineering",
    "neuroscience",
    "neural signal",
    "brain data",
    "eeg",
    "ecog",
    "fmri",
    "meg",
    "fnirs",
    "intracortical",
]

DECODING_TERMS = [
    "neural decoding",
    "speech decoding",
    "semantic decoding",
    "language decoding",
    "brain-to-text",
    "brain to text",
    "imagined speech",
    "attempted speech",
    "silent speech",
    "language reconstruction",
    "speech reconstruction",
    "speech prosthesis",
    "neural speech prosthesis",
]

LLM_TERMS = [
    "large language model",
    "large language models",
    "llm",
    "llms",
    "generative ai",
    "genai",
    "gpt",
    "chatgpt",
]

LANGUAGE_MODEL_TERMS = [
    "language model",
    "language models",
    "language modeling",
    "language modelling",
]

NLP_TERMS = [
    "natural language processing",
    "text generation",
    "language generation",
    "word prediction",
    "predictive text",
]

HUMAN_TERMS = [
    "human-ai interaction",
    "human ai interaction",
    "human-computer interaction",
    "human computer interaction",
    "user",
    "patient",
    "trust",
    "reliance",
    "overreliance",
    "human validation",
    "human oversight",
    "human-in-the-loop",
    "decision making",
    "decision-making",
    "usability",
    "assistive communication",
]

RISK_TERMS = [
    "bias",
    "cognitive bias",
    "algorithmic bias",
    "confirmation bias",
    "anchoring bias",
    "automation bias",
    "hallucination",
    "uncertainty",
    "error propagation",
    "privacy",
    "neural privacy",
    "mental privacy",
    "security",
    "safety",
    "neuroethics",
    "neurorights",
    "governance",
    "autonomy",
    "consent",
    "accountability",
    "explainability",
    "traceability",
    "auditability",
]

FALSE_POSITIVE_TERMS = [
    "body mass index",
    "body-mass index",
    "obesity",
    "overweight",
    "weight loss",
    "bmi percentile",
    "bayesian cue integration",
    "neuro-linguistic programming",
    "neurolinguistic programming",
]

AMBIGUOUS_BCI_TERMS = [
    "bayesian cue integration",
    "business continuity index",
    "building cost index",
]

AMBIGUOUS_NLP_TERMS = [
    "neuro-linguistic programming",
    "neurolinguistic programming",
]

NON_BRAIN_NEURAL_TERMS = [
    "neural network",
    "neural networks",
    "neural architecture",
    "neural data augmentation",
    "neural machine translation",
]

PURE_TECHNICAL_TERMS = [
    "technical architecture",
    "benchmark",
    "model performance",
    "parameter count",
    "training efficiency",
    "inference throughput",
]


def normalize_text(*parts: str | None) -> str:
    return " ".join(part or "" for part in parts).lower()


def _matches_term(text: str, term: str) -> bool:
    normalized = term.strip().lower()
    if not normalized:
        return False

    if re.fullmatch(r"[a-z0-9]{2,5}", normalized):
        return (
            re.search(
                rf"(?<![a-z0-9]){re.escape(normalized)}(?![a-z0-9])",
                text,
            )
            is not None
        )

    return normalized in text


def contains_any(text: str, values: Iterable[str]) -> bool:
    lower = text.lower()
    return any(_matches_term(lower, value) for value in values)


def _config_terms(
    classification: dict,
    *keys: str,
    fallback: list[str],
) -> list[str]:
    for key in keys:
        values = classification.get(key)
        if isinstance(values, list) and values:
            return [str(value) for value in values]
    return fallback


def _has_explicit_interface(text: str, classification: dict) -> bool:
    phrases = _config_terms(
        classification,
        "interface_terms",
        fallback=INTERFACE_PHRASES,
    )
    abbreviations = _config_terms(
        classification,
        "interface_abbreviations",
        fallback=INTERFACE_ABBREVIATIONS,
    )
    context_terms = _config_terms(
        classification,
        "interface_context_terms",
        fallback=INTERFACE_CONTEXT_TERMS,
    )
    ambiguous_bci = _config_terms(
        classification,
        "ambiguous_bci_terms",
        fallback=AMBIGUOUS_BCI_TERMS,
    )

    if contains_any(text, ambiguous_bci):
        return False

    if contains_any(text, phrases):
        return True

    return contains_any(text, abbreviations) and contains_any(
        text,
        context_terms,
    )


def _is_false_positive(text: str, classification: dict) -> bool:
    false_terms = _config_terms(
        classification,
        "false_positive_terms",
        fallback=FALSE_POSITIVE_TERMS,
    )
    return contains_any(text, false_terms)


def suggest_tags(config: dict, *parts: str | None) -> list[str]:
    text = normalize_text(*parts)
    tags_config = config.get("tags", {})
    classification = config.get("classification", {})

    if not isinstance(tags_config, dict):
        return []
    if not isinstance(classification, dict):
        classification = {}

    tags: set[str] = set()

    for tag, keywords in tags_config.items():
        if isinstance(keywords, str):
            keywords = [keywords]
        if not isinstance(keywords, list):
            continue

        if contains_any(text, [str(keyword) for keyword in keywords]):
            tags.add(str(tag))

    if contains_any(
        text,
        _config_terms(
            classification,
            "ambiguous_bci_terms",
            fallback=AMBIGUOUS_BCI_TERMS,
        ),
    ):
        tags.discard("domain:bci")

    if contains_any(
        text,
        _config_terms(
            classification,
            "ambiguous_nlp_terms",
            fallback=AMBIGUOUS_NLP_TERMS,
        ),
    ):
        tags.discard("ai:nlp")

    if contains_any(text, ["body mass index", "body-mass index"]):
        tags.discard("domain:bmi")

    non_brain_terms = _config_terms(
        classification,
        "non_brain_neural_terms",
        fallback=NON_BRAIN_NEURAL_TERMS,
    )
    if contains_any(text, non_brain_terms) and not _has_explicit_interface(
        text,
        classification,
    ):
        tags = {
            tag
            for tag in tags
            if not tag.startswith("domain:neuro")
            and not tag.startswith("signal:")
        }

    return sorted(tags)


def suggest_priority(
    config: dict,
    title: str,
    venue: str,
    query: str = "",
    source_api: str = "",
    abstract: str = "",
) -> str:
    """
    Classifica somente pelo conteúdo e metadados do artigo.

    `query` é mantida para compatibilidade, mas não participa da decisão.
    """
    text = normalize_text(title, abstract, venue, source_api)
    classification = config.get("classification", {})
    if not isinstance(classification, dict):
        classification = {}

    if title.strip().lower().startswith(
        ("review of:", "review of ", "comment on:", "response to:")
    ):
        return "D-descartar"

    if _is_false_positive(text, classification):
        return "D-descartar"

    non_brain_terms = _config_terms(
        classification,
        "non_brain_neural_terms",
        fallback=NON_BRAIN_NEURAL_TERMS,
    )
    has_non_brain_neural = contains_any(text, non_brain_terms)

    broad_neuro_terms = _config_terms(
        classification,
        "broad_neuro_terms",
        "neuro_terms",
        fallback=BROAD_NEURO_TERMS,
    )
    decoding_terms = _config_terms(
        classification,
        "decoding_terms",
        fallback=DECODING_TERMS,
    )
    llm_terms = _config_terms(
        classification,
        "llm_terms",
        fallback=LLM_TERMS,
    )
    language_model_terms = _config_terms(
        classification,
        "language_model_terms",
        fallback=LANGUAGE_MODEL_TERMS,
    )
    nlp_terms = _config_terms(
        classification,
        "nlp_terms",
        fallback=NLP_TERMS,
    )
    human_terms = _config_terms(
        classification,
        "human_terms",
        fallback=HUMAN_TERMS,
    )
    risk_terms = _config_terms(
        classification,
        "risk_terms",
        fallback=RISK_TERMS,
    )
    central_venues = _config_terms(
        classification,
        "primary_venues",
        "central_venues",
        fallback=[],
    )
    support_venues = _config_terms(
        classification,
        "support_venues",
        fallback=[],
    )
    caution_sources = _config_terms(
        classification,
        "caution_sources",
        fallback=["arxiv", "biorxiv", "medrxiv", "preprint"],
    )
    pure_technical_terms = _config_terms(
        classification,
        "pure_technical_terms",
        fallback=PURE_TECHNICAL_TERMS,
    )

    has_interface = _has_explicit_interface(text, classification)
    has_broad_neuro = contains_any(text, broad_neuro_terms)
    has_decoding = contains_any(text, decoding_terms)
    has_llm = contains_any(text, llm_terms)
    has_language_model = contains_any(text, language_model_terms)
    has_nlp = contains_any(text, nlp_terms)
    has_human = contains_any(text, human_terms)
    has_risk = contains_any(text, risk_terms)
    is_central_venue = contains_any(text, central_venues)
    is_support_venue = contains_any(text, support_venues)
    is_caution_source = contains_any(text, caution_sources)

    if is_caution_source and (
        has_interface
        or has_broad_neuro
        or has_decoding
        or has_llm
        or has_risk
    ):
        return "C-cautela"

    if has_interface and (
        has_llm
        or has_language_model
        or has_nlp
        or has_decoding
    ):
        return "A1-central-integracao"

    if has_interface and has_risk:
        return "A2-central-riscos"

    if has_broad_neuro and has_risk:
        return "B-apoio"

    if has_decoding and (
        has_llm
        or has_language_model
        or has_nlp
        or has_human
    ):
        return "B-apoio"

    if has_interface or has_broad_neuro or has_decoding:
        return "B-apoio"

    if has_llm and (has_human or has_risk):
        return "B-apoio"

    if is_central_venue and (
        has_broad_neuro
        or has_decoding
        or has_llm
        or has_risk
    ):
        return "B-apoio"

    if is_support_venue and (
        has_broad_neuro
        or has_decoding
        or has_llm
        or has_risk
    ):
        return "B-apoio"

    if contains_any(text, pure_technical_terms) and not (
        has_interface
        or has_broad_neuro
        or has_human
        or has_risk
    ):
        return "D-descartar"

    if has_non_brain_neural and not (
        has_interface or has_broad_neuro or has_decoding
    ):
        return "D-descartar"

    return "B-apoio"


def infer_corrente(*parts: str | None) -> str:
    text = normalize_text(*parts)
    empty_classification: dict = {}

    has_interface = _has_explicit_interface(text, empty_classification)
    has_broad_neuro = contains_any(text, BROAD_NEURO_TERMS)
    has_decoding = contains_any(text, DECODING_TERMS)
    has_llm = contains_any(text, LLM_TERMS)
    has_language_model = contains_any(text, LANGUAGE_MODEL_TERMS)
    has_nlp = contains_any(text, NLP_TERMS)
    has_human = contains_any(text, HUMAN_TERMS)
    has_risk = contains_any(text, RISK_TERMS)

    if has_interface and (has_llm or has_language_model or has_nlp):
        return "Integração BMI/BCI e Modelos de Linguagem"

    if has_interface and has_risk:
        return "Riscos e Governança em BMI/BCI"

    if has_decoding:
        return "Decodificação Neural e Brain-to-Text"

    if has_broad_neuro and has_risk:
        return "Neurotecnologia, Segurança e Governança"

    if has_human:
        return "Interação Humano-IA, Confiança e Validação"

    if contains_any(
        text,
        [
            "bias",
            "cognitive bias",
            "algorithmic bias",
            "confirmation bias",
            "anchoring bias",
            "automation bias",
            "hallucination",
            "uncertainty",
        ],
    ):
        return "Vieses, Erros e Vulnerabilidades"

    if has_interface or has_broad_neuro:
        return "BMI/BCI e Neurotecnologia"

    if has_llm or has_language_model or has_nlp:
        return "LLMs e Processamento de Linguagem"

    return "Literatura de apoio / A classificar"
