from __future__ import annotations

import re
from collections.abc import Iterable


# Termos padrão usados quando o arquivo de configuração não define
# listas específicas para a classificação.
NEURO_TERMS = [
    "brain-computer interface",
    "brain computer interface",
    "brain-machine interface",
    "brain machine interface",
    "bci",
    "bmi",
    "neural interface",
    "neurotechnology",
    "neuroengineering",
    "neural signal",
    "neural data",
    "eeg",
    "ecog",
    "fmri",
    "intracortical",
]

DECODING_TERMS = [
    "neural decoding",
    "speech decoding",
    "semantic decoding",
    "brain-to-text",
    "brain to text",
    "imagined speech",
    "attempted speech",
    "language reconstruction",
    "speech prosthesis",
    "neural speech prosthesis",
]

LLM_TERMS = [
    "large language model",
    "large language models",
    "llm",
    "llms",
    "generative ai",
    "language model",
    "language models",
    "natural language processing",
    "nlp",
    "transformer",
    "gpt",
]

HUMAN_TERMS = [
    "human-ai",
    "human ai",
    "human-computer interaction",
    "human computer interaction",
    "user",
    "patient",
    "trust",
    "reliance",
    "overreliance",
    "human validation",
    "human oversight",
    "decision making",
    "decision-making",
    "usability",
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
    "security",
    "safety",
    "neuroethics",
    "governance",
    "autonomy",
    "consent",
    "accountability",
    "explainability",
    "traceability",
]

FALSE_POSITIVE_TERMS = [
    "body mass index",
    "body-mass index",
    "obesity",
    "overweight",
    "weight loss",
    "bmi percentile",
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
    """Combina e normaliza campos textuais para comparação."""
    return " ".join(part or "" for part in parts).lower()


def _matches_term(text: str, term: str) -> bool:
    """
    Verifica um termo preservando limites de palavra para siglas curtas.

    Isso reduz falsos positivos como BMI dentro de palavras maiores.
    """
    normalized = term.strip().lower()
    if not normalized:
        return False

    if re.fullmatch(r"[a-z0-9]{2,5}", normalized):
        return re.search(rf"(?<![a-z0-9]){re.escape(normalized)}(?![a-z0-9])", text) is not None

    return normalized in text


def contains_any(text: str, values: Iterable[str]) -> bool:
    """Retorna True quando ao menos um termo aparece no texto."""
    lower = text.lower()
    return any(_matches_term(lower, value) for value in values)


def _config_terms(classification: dict, *keys: str, fallback: list[str]) -> list[str]:
    """Obtém a primeira lista configurada; usa fallback quando ausente."""
    for key in keys:
        values = classification.get(key)
        if isinstance(values, list) and values:
            return [str(value) for value in values]
    return fallback


def suggest_tags(config: dict, *parts: str | None) -> list[str]:
    """
    Sugere tags a partir do bloco `tags` do YAML.

    Formato esperado:
        tags:
          domain:bci:
            - brain-computer interface
            - bci
    """
    text = normalize_text(*parts)
    tags_config = config.get("tags", {})
    tags: set[str] = set()

    if not isinstance(tags_config, dict):
        return []

    for tag, keywords in tags_config.items():
        if isinstance(keywords, str):
            keywords = [keywords]

        if not isinstance(keywords, list):
            continue

        if contains_any(text, [str(keyword) for keyword in keywords]):
            tags.add(str(tag))

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
    Sugere prioridade preliminar.

    Retornos mantidos por compatibilidade com o pipeline existente:
    - A-central
    - B-apoio
    - C-cautela
    - D-descartar
    """
    # `query` é mantida apenas para compatibilidade com chamadas antigas.
    # A classificação usa somente conteúdo e metadados do artigo.
    text = normalize_text(title, abstract, venue, source_api)
    classification = config.get("classification", {})

    if not isinstance(classification, dict):
        classification = {}

    neuro_terms = _config_terms(
        classification,
        "neuro_terms",
        "bci_bmi_terms",
        fallback=NEURO_TERMS,
    )
    decoding_terms = _config_terms(
        classification,
        "decoding_terms",
        fallback=DECODING_TERMS,
    )
    llm_terms = _config_terms(
        classification,
        "llm_terms",
        "language_model_terms",
        fallback=LLM_TERMS,
    )
    human_terms = _config_terms(
        classification,
        "human_terms",
        "interaction_terms",
        fallback=HUMAN_TERMS,
    )
    risk_terms = _config_terms(
        classification,
        "risk_terms",
        "governance_terms",
        fallback=RISK_TERMS,
    )

    central_venues = _config_terms(
        classification,
        "primary_venues",
        "central_venues",
        "neuro_venues",
        "priority_venues",
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

    has_neuro = contains_any(text, neuro_terms)
    has_decoding = contains_any(text, decoding_terms)
    has_llm = contains_any(text, llm_terms)
    has_human = contains_any(text, human_terms)
    has_risk = contains_any(text, risk_terms)
    is_central_venue = contains_any(text, central_venues)
    is_support_venue = contains_any(text, support_venues)
    is_caution_source = contains_any(text, caution_sources)

    # Falso positivo recorrente: BMI como Body Mass Index.
    if contains_any(text, FALSE_POSITIVE_TERMS) and not contains_any(
        text,
        [
            "brain-machine interface",
            "brain machine interface",
            "brain-computer interface",
            "brain computer interface",
            "neural interface",
        ],
    ):
        return "D-descartar"

    # Preprints relevantes permanecem como cautela, não descarte automático.
    if is_caution_source and (has_neuro or has_decoding or has_llm or has_risk):
        return "C-cautela"

    # Integração explícita entre neurotecnologia e modelos de linguagem.
    if has_neuro and has_llm:
        return "A-central"

    # Riscos diretamente associados a BMI/BCI fazem parte do núcleo do projeto.
    if has_neuro and has_risk:
        return "A-central"

    # Estudos que combinam decodificação, linguagem e dimensão humana/de risco.
    if has_neuro and has_decoding and (has_human or has_risk):
        return "A-central"

    # Venue central somente conta como sinal forte quando o conteúdo também é aderente.
    if is_central_venue and has_neuro and (has_decoding or has_llm or has_risk):
        return "A-central"

    # Relevância parcial para fundamentação ou análise de áreas adjacentes.
    if has_neuro and (has_decoding or has_human or has_risk):
        return "B-apoio"

    if has_decoding and (has_llm or has_human or has_risk):
        return "B-apoio"

    if is_support_venue and (has_neuro or has_decoding or has_llm or has_risk):
        return "B-apoio"

    # Benchmark puramente técnico sem ligação com neuro, usuário ou riscos.
    if contains_any(text, PURE_TECHNICAL_TERMS) and not (
        has_neuro or has_human or has_risk
    ):
        return "D-descartar"

    return "B-apoio"


def infer_corrente(*parts: str | None) -> str:
    """Infere a corrente analítica predominante."""
    text = normalize_text(*parts)

    has_neuro = contains_any(text, NEURO_TERMS)
    has_decoding = contains_any(text, DECODING_TERMS)
    has_llm = contains_any(text, LLM_TERMS)
    has_human = contains_any(text, HUMAN_TERMS)
    has_risk = contains_any(text, RISK_TERMS)

    if has_neuro and has_llm:
        return "Integração BMI/BCI e LLMs"

    if contains_any(
        text,
        [
            "privacy",
            "neural privacy",
            "security",
            "safety",
            "neuroethics",
            "governance",
            "autonomy",
            "consent",
            "accountability",
            "regulation",
            "traceability",
        ],
    ):
        return "Segurança, Privacidade Neural e Governança"

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
            "error propagation",
        ],
    ):
        return "Vieses, Erros e Vulnerabilidades"

    if has_human:
        return "Interação Humano-IA, Confiança e Validação"

    if has_decoding:
        return "Decodificação Neural e Brain-to-Text"

    if has_neuro:
        return "BMI/BCI e Aquisição de Sinais Neurais"

    if has_llm:
        return "LLMs e Processamento de Linguagem"

    if has_risk:
        return "Riscos e Governança — A classificar"

    return "Literatura de apoio / A classificar"
