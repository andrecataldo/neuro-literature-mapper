from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass


DEFAULT_INTERFACE_TERMS = [
    "brain-computer interface",
    "brain computer interface",
    "brain-machine interface",
    "brain machine interface",
    "neural interface",
    "brain interface",
    "chatbci",
    "bci speller",
    "p300 speller",
]
DEFAULT_INTERFACE_ABBREVIATIONS = ["bci", "bmi"]
DEFAULT_INTERFACE_CONTEXT_TERMS = [
    "brain",
    "neural",
    "eeg",
    "ecog",
    "fmri",
    "intracortical",
    "p300",
    "ssvep",
    "motor imagery",
    "speller",
    "neurotechnology",
    "neuroengineering",
    "interface",
]
DEFAULT_BRAIN_CONTEXT_TERMS = [
    "brain",
    "cortical",
    "intracortical",
    "neural signal",
    "neural activity",
    "neural recording",
    "neural data",
    "eeg",
    "ecog",
    "fmri",
    "meg",
    "fnirs",
    "p300",
    "ssvep",
    "motor imagery",
]
DEFAULT_DECODING_TERMS = [
    "neural decoding",
    "speech decoding",
    "semantic decoding",
    "language decoding",
    "brain-to-text",
    "brain to text",
    "eeg-to-text",
    "eeg to text",
    "imagined speech",
    "attempted speech",
    "covert speech",
    "silent speech",
    "language reconstruction",
    "speech reconstruction",
    "speech synthesis",
    "speech neuroprosthesis",
    "neural speech prosthesis",
    "imagined handwriting",
]
DEFAULT_STRONG_LLM_TERMS = [
    "large language model",
    "large language models",
    "llm",
    "llms",
    "generative ai",
    "genai",
    "gpt",
    "chatgpt",
]
DEFAULT_LANGUAGE_ASSISTANCE_TERMS = [
    "language model",
    "language models",
    "language modeling",
    "language modelling",
    "natural language processing",
    "text generation",
    "language generation",
    "word prediction",
    "predictive text",
    "context-driven word prediction",
]
DEFAULT_HUMAN_TERMS = [
    "human-ai interaction",
    "human ai interaction",
    "human-computer interaction",
    "human computer interaction",
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
DEFAULT_RISK_TERMS = [
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
    "data ownership",
    "neural data ownership",
    "mental integrity",
    "cognitive liberty",
    "agency",
    "liability",
    "responsibility",
]
DEFAULT_FALSE_POSITIVE_TERMS = [
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
DEFAULT_AMBIGUOUS_BCI_TERMS = [
    "bayesian cue integration",
    "business continuity index",
    "building cost index",
]
DEFAULT_AMBIGUOUS_NLP_TERMS = [
    "neuro-linguistic programming",
    "neurolinguistic programming",
]
DEFAULT_NON_BRAIN_NEURAL_TERMS = [
    "neural network",
    "neural networks",
    "neural architecture",
    "neural data augmentation",
    "neural machine translation",
]
DEFAULT_REVIEW_PREFIXES = [
    "review of:",
    "review of ",
    "comment on:",
    "commentary on:",
    "response to:",
    "author response:",
    "peer review of:",
]


@dataclass(frozen=True)
class SemanticEvidence:
    interface_title: bool
    interface_abstract: bool
    brain_title: bool
    brain_abstract: bool
    decoding_title: bool
    decoding_abstract: bool
    llm_title: bool
    llm_abstract: bool
    language_title: bool
    language_abstract: bool
    human_title: bool
    human_abstract: bool
    risk_title: bool
    risk_abstract: bool
    interface_language_same_sentence: bool
    brain_decoding_same_sentence: bool
    interface_risk_same_sentence: bool


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


def _sentences(text: str) -> list[str]:
    return [
        part.strip()
        for part in re.split(r"(?<=[.!?;])\s+|\n+", text.lower())
        if part.strip()
    ]


def _same_sentence_has(
    text: str,
    first_terms: Iterable[str],
    second_terms: Iterable[str],
) -> bool:
    return any(
        contains_any(sentence, first_terms)
        and contains_any(sentence, second_terms)
        for sentence in _sentences(text)
    )


def _mask_negated_mentions(
    text: str,
    terms: Iterable[str],
) -> str:
    """
    Remove trechos que negam explicitamente o uso de uma tecnologia.

    Exemplos tratados:
    - "without a large language model"
    - "no brain-computer interface is used"
    - "does not use an LLM"
    """
    result = text.lower()
    negators = (
        r"no|without|not using|does not use|do not use|"
        r"did not use|absence of|unrelated to"
    )

    for term in sorted(
        {str(value).strip().lower() for value in terms if str(value).strip()},
        key=len,
        reverse=True,
    ):
        escaped = re.escape(term)
        pattern = (
            rf"\b(?:{negators})\b"
            rf"[^.!?;]{{0,80}}?"
            rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"
        )
        result = re.sub(pattern, " ", result, flags=re.IGNORECASE)

    return result


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


def _is_review_comment(title: str, classification: dict) -> bool:
    prefixes = _config_terms(
        classification,
        "review_comment_prefixes",
        fallback=DEFAULT_REVIEW_PREFIXES,
    )
    lowered = title.strip().lower()
    return any(lowered.startswith(prefix.lower()) for prefix in prefixes)


def _has_explicit_interface(text: str, classification: dict) -> bool:
    phrases = _config_terms(
        classification,
        "explicit_interface_terms",
        "interface_terms",
        fallback=DEFAULT_INTERFACE_TERMS,
    )
    abbreviations = _config_terms(
        classification,
        "interface_abbreviations",
        fallback=DEFAULT_INTERFACE_ABBREVIATIONS,
    )
    context_terms = _config_terms(
        classification,
        "interface_context_terms",
        fallback=DEFAULT_INTERFACE_CONTEXT_TERMS,
    )
    ambiguous_terms = _config_terms(
        classification,
        "ambiguous_bci_terms",
        fallback=DEFAULT_AMBIGUOUS_BCI_TERMS,
    )

    if contains_any(text, ambiguous_terms):
        return False

    if contains_any(text, phrases):
        return True

    # A sigla precisa compartilhar a mesma sentença com contexto cerebral/BCI.
    return _same_sentence_has(text, abbreviations, context_terms)


def _semantic_evidence(
    title: str,
    abstract: str,
    classification: dict,
) -> SemanticEvidence:
    interface_terms = _config_terms(
        classification,
        "explicit_interface_terms",
        "interface_terms",
        fallback=DEFAULT_INTERFACE_TERMS,
    ) + _config_terms(
        classification,
        "interface_abbreviations",
        fallback=DEFAULT_INTERFACE_ABBREVIATIONS,
    )
    brain_terms = _config_terms(
        classification,
        "brain_context_terms",
        "broad_neuro_terms",
        fallback=DEFAULT_BRAIN_CONTEXT_TERMS,
    )
    decoding_terms = _config_terms(
        classification,
        "language_decoding_terms",
        "decoding_terms",
        fallback=DEFAULT_DECODING_TERMS,
    )
    llm_terms = _config_terms(
        classification,
        "strong_llm_terms",
        "llm_terms",
        fallback=DEFAULT_STRONG_LLM_TERMS,
    )
    language_terms = _config_terms(
        classification,
        "language_assistance_terms",
        "language_model_terms",
        "nlp_terms",
        fallback=DEFAULT_LANGUAGE_ASSISTANCE_TERMS,
    )
    human_terms = _config_terms(
        classification,
        "human_terms",
        fallback=DEFAULT_HUMAN_TERMS,
    )
    risk_terms = _config_terms(
        classification,
        "risk_governance_terms",
        "risk_terms",
        fallback=DEFAULT_RISK_TERMS,
    )

    title_text = title.lower()

    semantic_terms = [
        *interface_terms,
        *brain_terms,
        *decoding_terms,
        *llm_terms,
        *language_terms,
        *human_terms,
        *risk_terms,
    ]
    abstract_text = _mask_negated_mentions(
        abstract.lower(),
        semantic_terms,
    )

    return SemanticEvidence(
        interface_title=_has_explicit_interface(title_text, classification),
        interface_abstract=_has_explicit_interface(
            abstract_text, classification
        ),
        brain_title=contains_any(title_text, brain_terms),
        brain_abstract=contains_any(abstract_text, brain_terms),
        decoding_title=contains_any(title_text, decoding_terms),
        decoding_abstract=contains_any(abstract_text, decoding_terms),
        llm_title=contains_any(title_text, llm_terms),
        llm_abstract=contains_any(abstract_text, llm_terms),
        language_title=contains_any(title_text, language_terms),
        language_abstract=contains_any(abstract_text, language_terms),
        human_title=contains_any(title_text, human_terms),
        human_abstract=contains_any(abstract_text, human_terms),
        risk_title=contains_any(title_text, risk_terms),
        risk_abstract=contains_any(abstract_text, risk_terms),
        interface_language_same_sentence=_same_sentence_has(
            abstract_text,
            interface_terms,
            [*llm_terms, *language_terms],
        ),
        brain_decoding_same_sentence=_same_sentence_has(
            abstract_text,
            brain_terms,
            decoding_terms,
        ),
        interface_risk_same_sentence=_same_sentence_has(
            abstract_text,
            interface_terms,
            risk_terms,
        ),
    )


def suggest_priority(
    config: dict,
    title: str,
    venue: str = "",
    query: str = "",
    source_api: str = "",
    abstract: str = "",
) -> str:
    """
    Sugere relevância temática usando somente título e resumo.

    `venue`, `query` e `source_api` são mantidos na assinatura por
    compatibilidade, mas não participam da classificação semântica.
    """
    classification = config.get("classification", {})
    if not isinstance(classification, dict):
        classification = {}

    semantic_text = normalize_text(title, abstract)

    if _is_review_comment(title, classification):
        return "D-descartar"

    false_terms = _config_terms(
        classification,
        "false_positive_terms",
        fallback=DEFAULT_FALSE_POSITIVE_TERMS,
    )
    if contains_any(semantic_text, false_terms):
        return "D-descartar"

    evidence = _semantic_evidence(title, abstract, classification)

    # A1: integração com LLM/modelos de linguagem.
    if (
        evidence.interface_title
        and (
            evidence.llm_title
            or evidence.language_title
            or evidence.llm_abstract
        )
    ):
        return "A1-central-integracao-llm"

    if (
        evidence.llm_title
        and (
            evidence.interface_abstract
            or evidence.decoding_abstract
        )
    ):
        return "A1-central-integracao-llm"

    if (
        evidence.decoding_title
        and (
            evidence.llm_title
            or evidence.llm_abstract
            or evidence.language_title
        )
    ):
        return "A1-central-integracao-llm"

    if evidence.interface_language_same_sentence:
        return "A1-central-integracao-llm"

    # A2: decodificação neural de linguagem, sem exigir LLM.
    if evidence.decoding_title and (
        evidence.brain_title
        or evidence.brain_abstract
        or evidence.interface_title
        or evidence.interface_abstract
    ):
        return "A2-central-decoding-linguagem"

    if evidence.interface_title and evidence.decoding_abstract:
        return "A2-central-decoding-linguagem"

    if evidence.brain_decoding_same_sentence:
        return "A2-central-decoding-linguagem"

    # A3: risco/governança diretamente ligado a BMI/BCI.
    if evidence.interface_title and (
        evidence.risk_title or evidence.risk_abstract
    ):
        return "A3-central-riscos-governanca"

    if evidence.risk_title and evidence.interface_abstract:
        return "A3-central-riscos-governanca"

    if evidence.interface_risk_same_sentence:
        return "A3-central-riscos-governanca"

    # Falsos "neural" de redes neurais devem ser excluídos antes das
    # regras amplas de apoio.
    non_brain_terms = _config_terms(
        classification,
        "non_brain_neural_terms",
        fallback=DEFAULT_NON_BRAIN_NEURAL_TERMS,
    )
    if contains_any(semantic_text, non_brain_terms) and not (
        evidence.brain_title
        or evidence.brain_abstract
        or evidence.interface_title
        or evidence.interface_abstract
        or evidence.decoding_title
        or evidence.decoding_abstract
    ):
        return "D-descartar"

    # Apoio: componentes importantes, mas sem acoplamento central.
    if (
        evidence.interface_title
        or evidence.interface_abstract
        or evidence.brain_title
        or evidence.decoding_title
    ):
        return "B-apoio"

    if (
        (evidence.llm_title or evidence.llm_abstract)
        and (
            evidence.risk_title
            or evidence.risk_abstract
            or evidence.human_title
            or evidence.human_abstract
        )
    ):
        return "B-apoio"

    return "B-apoio"


def suggest_tags(config: dict, *parts: str | None) -> list[str]:
    """
    Sugere tags usando somente os campos fornecidos pelo chamador.

    No pipeline v4, são fornecidos apenas título e resumo.
    """
    text = normalize_text(*parts)
    tags_config = config.get("tags", {})
    classification = config.get("classification", {})

    if not isinstance(tags_config, dict):
        return []
    if not isinstance(classification, dict):
        classification = {}

    all_tag_terms: list[str] = []
    for keywords in tags_config.values():
        values = [keywords] if isinstance(keywords, str) else keywords
        if isinstance(values, list):
            all_tag_terms.extend(str(value) for value in values)

    text = _mask_negated_mentions(text, all_tag_terms)

    tags: set[str] = set()

    for tag, keywords in tags_config.items():
        values = [keywords] if isinstance(keywords, str) else keywords
        if not isinstance(values, list):
            continue
        if contains_any(text, [str(value) for value in values]):
            tags.add(str(tag))

    if _has_explicit_interface(text, classification):
        if contains_any(
            text,
            ["brain-computer interface", "brain computer interface", "bci"],
        ):
            tags.add("domain:bci")
        if contains_any(
            text,
            ["brain-machine interface", "brain machine interface", "bmi"],
        ):
            tags.add("domain:bmi")

    if contains_any(
        text,
        _config_terms(
            classification,
            "ambiguous_bci_terms",
            fallback=DEFAULT_AMBIGUOUS_BCI_TERMS,
        ),
    ):
        tags.discard("domain:bci")

    if contains_any(
        text,
        _config_terms(
            classification,
            "ambiguous_nlp_terms",
            fallback=DEFAULT_AMBIGUOUS_NLP_TERMS,
        ),
    ):
        tags.discard("ai:nlp")

    if contains_any(text, ["body mass index", "body-mass index"]):
        tags.discard("domain:bmi")

    # LLM é uma subclasse mais específica; evita redundância no Zotero.
    if "ai:llm" in tags:
        tags.discard("ai:language-model")

    return sorted(tags)


def infer_corrente(
    *parts: str | dict | None,
    config: dict | None = None,
) -> str:
    """
    Infere a corrente analítica com compatibilidade retroativa.

    Chamadas aceitas:
    - infer_corrente(title)
    - infer_corrente(title, abstract)
    - infer_corrente(title, abstract, config)
    - infer_corrente(title, abstract, venue, query)  # adaptadores antigos

    Apenas título e resumo são usados semanticamente. Argumentos extras de
    adaptadores antigos são ignorados.
    """
    values = list(parts)

    if config is None and values and isinstance(values[-1], dict):
        config = values.pop()

    title = str(values[0] or "") if values else ""
    abstract = str(values[1] or "") if len(values) > 1 else ""

    classification = (
        config.get("classification", {})
        if isinstance(config, dict)
        else {}
    )
    if not isinstance(classification, dict):
        classification = {}

    evidence = _semantic_evidence(
        title or "",
        abstract or "",
        classification,
    )

    if suggest_priority(
        config or {},
        title or "",
        abstract=abstract or "",
    ) == "A1-central-integracao-llm":
        return "Integração BMI/BCI e LLMs"

    if (
        evidence.decoding_title
        or evidence.brain_decoding_same_sentence
    ):
        return "Decodificação Neural de Linguagem"

    if (
        evidence.interface_title
        and (evidence.risk_title or evidence.risk_abstract)
    ) or evidence.interface_risk_same_sentence:
        return "Riscos e Governança em BMI/BCI"

    if (
        evidence.brain_title
        or evidence.brain_abstract
        or evidence.interface_title
        or evidence.interface_abstract
    ) and (evidence.risk_title or evidence.risk_abstract):
        return "Neurotecnologia, Segurança e Governança"

    if evidence.human_title or evidence.human_abstract:
        return "Interação Humano-IA, Confiança e Validação"

    if evidence.risk_title or evidence.risk_abstract:
        return "Vieses, Erros e Vulnerabilidades"

    if evidence.interface_title or evidence.interface_abstract:
        return "BMI/BCI e Neurotecnologia"

    if evidence.llm_title or evidence.llm_abstract:
        return "LLMs e Processamento de Linguagem"

    return "Literatura de apoio / A classificar"
