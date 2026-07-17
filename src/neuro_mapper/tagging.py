from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

UNICODE_HYPHEN_TRANSLATION = str.maketrans(
    {
        "\u00ad": "-",  # soft hyphen
        "\u2010": "-",  # hyphen
        "\u2011": "-",  # non-breaking hyphen
        "\u2012": "-",  # figure dash
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2212": "-",  # minus sign
        "\uff0d": "-",  # full-width hyphen-minus
    }
)

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
DEFAULT_STRONG_INTERFACE_TERMS = [
    "brain-computer interface",
    "brain computer interface",
    "brain-machine interface",
    "brain machine interface",
    "brain interface",
    "chatbci",
    "bci speller",
    "p300 speller",
]

DEFAULT_AMBIGUOUS_INTERFACE_TERMS = [
    "neural interface",
]

DEFAULT_NEURAL_INTERFACE_CONTEXT_TERMS = [
    "brain",
    "brain signal",
    "brain signals",
    "brain activity",
    "cortical",
    "intracortical",
    "neural signal",
    "neural signals",
    "neural recording",
    "neural recordings",
    "eeg",
    "ecog",
    "fmri",
    "meg",
    "fnirs",
    "p300",
    "ssvep",
    "motor imagery",
]

DEFAULT_NEURAL_SIGNAL_TERMS = [
    "brain signal",
    "brain signals",
    "brain activity",
    "brain recording",
    "brain recordings",
    "cortical activity",
    "cortical recording",
    "cortical recordings",
    "intracortical",
    "intracranial",
    "intracranial electrode",
    "intracranial electrodes",
    "intracranial depth electrode",
    "intracranial depth electrodes",
    "depth electrode",
    "depth electrodes",
    "neural signal",
    "neural signals",
    "neural activity",
    "neural recording",
    "neural recordings",
    "eeg",
    "ecog",
    "fmri",
    "meg",
    "fnirs",
    "seeg",
    "stereo-electroencephalography",
    "p300",
    "ssvep",
    "motor imagery",
    "neural implant",
    "brain implant",
]

DEFAULT_INTEGRATION_RELATION_TERMS = [
    "use",
    "uses",
    "using",
    "integrate",
    "integrates",
    "integrating",
    "integrated with",
    "leverage",
    "leverages",
    "leveraging",
    "assist",
    "assists",
    "assisted by",
    "powered by",
    "augment",
    "augments",
    "augmented with",
    "guide",
    "guides",
    "guided by",
    "incorporate",
    "incorporates",
    "incorporating",
    "combined with",
    "based on",
    "driven by",
    "enhance",
    "enhances",
    "enhancing",
    "post-processing with",
    "postprocessing with",
    "rerank",
    "reranking",
    "word prediction",
    "integrated into",
    "integration of",
    "built on",
    "built upon",
    "builds on",
    "builds upon",
    "employ",
    "employs",
    "employed",
    "utilize",
    "utilizes",
    "utilizing",
    "coupled with",
]

DEFAULT_WEAK_INTEGRATION_TERMS = [
    "inspired by",
    "similar to",
    "analogous to",
    "compared with",
    "compared to",
    "unlike",
    "without",
    "does not use",
    "do not use",
    "did not use",
    "not using",
    "absence of",
    "prompting us to explore",
]

DEFAULT_STRONG_RISK_TERMS = [
    "bias",
    "cognitive bias",
    "algorithmic bias",
    "confirmation bias",
    "anchoring bias",
    "automation bias",
    "hallucination",
    "error propagation",
    "privacy",
    "neural privacy",
    "mental privacy",
    "security",
    "cybersecurity",
    "safety",
    "neuroethics",
    "neurorights",
    "governance",
    "informed consent",
    "data ownership",
    "neural data ownership",
    "mental integrity",
    "cognitive liberty",
    "threat",
    "threats",
    "vulnerability",
    "vulnerabilities",
]

DEFAULT_NON_NEURAL_DECODING_TERMS = [
    "literature",
    "literary",
    "literary studies",
    "mind style",
    "narratology",
    "fiction",
    "poetics",
]
DEFAULT_PRIOR_WORK_TERMS = [
    "previous studies",
    "previous study",
    "prior studies",
    "prior study",
    "earlier studies",
    "previous work",
    "prior work",
    "earlier work",
    "existing work",
    "existing approaches",
    "previous approaches",
    "prior approaches",
    "recent studies have",
    "the literature has",
    "state of the art",
]

DEFAULT_EXTERNAL_ANALYSIS_TERMS = [
    "public perception",
    "social media",
    "social network",
    "posts",
    "tweets",
    "sentiment analysis",
    "topic modeling",
    "topic modelling",
    "discourse analysis",
    "bibliometric analysis",
    "bibliometric study",
    "literature analysis",
    "literature review",
    "thematic analysis",
    "research thematics",
]

DEFAULT_RISK_CONTRIBUTION_TERMS = [
    "analyze",
    "analyzes",
    "analyse",
    "analyses",
    "examines",
    "examine",
    "investigates",
    "investigate",
    "assesses",
    "assess",
    "evaluates",
    "evaluate",
    "addresses",
    "address",
    "focuses on",
    "risk",
    "risks",
    "threat",
    "threats",
    "vulnerability",
    "vulnerabilities",
    "privacy concern",
    "privacy concerns",
    "security concern",
    "security concerns",
    "ethical implication",
    "ethical implications",
]

DEFAULT_PERIPHERAL_SIGNAL_TERMS = [
    "electromyographic",
    "electromyography",
    "surface electromyography",
    "surface emg",
    "emg signal",
    "emg signals",
    "muscle signal",
    "muscle signals",
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
    "eeg2text",
    "imagined speech",
    "speech imagery",
    "attempted speech",
    "covert speech",
    "silent speech",
    "language reconstruction",
    "semantic reconstruction",
    "speech reconstruction",
    "reconstructing speech",
    "reconstructed speech",
    "speech is reconstructed",
    "speech synthesis",
    "synthesize speech",
    "synthesizing speech",
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
DEFAULT_A1_LANGUAGE_TECHNOLOGY_TERMS = [
    "language model",
    "language models",
    "pretrained language model",
    "pre-trained language model",
    "generative language model",
    "natural language processing",
    "nlp",
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

    neural_signal_title: bool
    neural_signal_abstract: bool

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

    strong_risk_title: bool
    strong_risk_abstract: bool

    integration_title: bool
    integration_abstract: bool

    weak_integration_title: bool
    weak_integration_abstract: bool

    interface_language_same_sentence: bool
    decoding_language_same_sentence: bool

    brain_decoding_same_sentence: bool
    neural_signal_decoding_same_sentence: bool

    interface_risk_same_sentence: bool
    interface_strong_risk_same_sentence: bool


def _normalize_semantic_text(
    value: str | None,
) -> str:
    """
    Normaliza texto para comparação semântica.

    Padroniza hífens tipográficos, espaços não separáveis,
    capitalização e sequências de espaços.
    """

    normalized = str(value or "").translate(
        UNICODE_HYPHEN_TRANSLATION
    )

    normalized = normalized.replace(
        "\u00a0",
        " ",
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized.strip().lower()


def normalize_text(*parts: str | None) -> str:
    return _normalize_semantic_text(
        " ".join(part or "" for part in parts)
    )


def _matches_term(
    text: str,
    term: str,
) -> bool:
    normalized_text = _normalize_semantic_text(text)
    normalized_term = _normalize_semantic_text(term)

    if not normalized_term:
        return False

    if re.fullmatch(
        r"[a-z0-9]{2,5}",
        normalized_term,
    ):
        return (
            re.search(
                rf"(?<![a-z0-9])"
                rf"{re.escape(normalized_term)}"
                rf"(?![a-z0-9])",
                normalized_text,
            )
            is not None
        )

    return normalized_term in normalized_text


def contains_any(
    text: str,
    values: Iterable[str],
) -> bool:
    return any(
        _matches_term(text, value)
        for value in values
    )


def _sentences(text: str) -> list[str]:
    normalized = _normalize_semantic_text(text)

    return [
        part.strip()
        for part in re.split(
            r"(?<=[.!?;])\s+|\n+",
            normalized,
        )
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

def _same_sentence_has_valid_interface_and(
    text: str,
    classification: dict,
    second_terms: Iterable[str],
) -> bool:
    """
    Exige uma interface BMI/BCI válida na sentença.

    Isso impede que expressões de software, como "neural interface
    layer", sejam interpretadas automaticamente como interface neural
    humana.
    """

    return any(
        _has_explicit_interface(sentence, classification)
        and contains_any(sentence, second_terms)
        for sentence in _sentences(text)
    )


def _has_integration_relation(
    text: str,
    classification: dict,
    technology_terms: Iterable[str],
) -> bool:
    """
    Identifica uma relação operacional com tecnologia de linguagem.

    O bloqueio de negação, comparação ou inspiração é aplicado somente
    à sentença analisada. Menções a trabalhos anteriores também não
    contam como evidência da contribuição atual.
    """

    relation_terms = _config_terms(
        classification,
        "integration_relation_terms",
        fallback=DEFAULT_INTEGRATION_RELATION_TERMS,
    )

    weak_terms = _config_terms(
        classification,
        "weak_integration_terms",
        fallback=DEFAULT_WEAK_INTEGRATION_TERMS,
    )

    prior_work_terms = _config_terms(
        classification,
        "prior_work_terms",
        fallback=DEFAULT_PRIOR_WORK_TERMS,
    )

    for sentence in _sentences(text):
        if not contains_any(
            sentence,
            technology_terms,
        ):
            continue

        if contains_any(
            sentence,
            weak_terms,
        ):
            continue

        if contains_any(
            sentence,
            prior_work_terms,
        ):
            continue

        if contains_any(
            sentence,
            relation_terms,
        ):
            return True

    return False

def _has_weak_integration_relation(
    text: str,
    classification: dict,
    technology_terms: Iterable[str],
) -> bool:
    weak_terms = _config_terms(
        classification,
        "weak_integration_terms",
        fallback=DEFAULT_WEAK_INTEGRATION_TERMS,
    )

    return any(
        contains_any(sentence, technology_terms)
        and contains_any(sentence, weak_terms)
        for sentence in _sentences(text)
    )

def _has_risk_contribution_sentence(
    text: str,
    classification: dict,
) -> bool:
    """
    Verifica se risco ou governança aparecem como objeto da
    contribuição, não apenas em uma lista de aplicações ou temas.
    """

    strong_risk_terms = _config_terms(
        classification,
        "strong_risk_governance_terms",
        fallback=DEFAULT_STRONG_RISK_TERMS,
    )

    contribution_terms = _config_terms(
        classification,
        "risk_contribution_terms",
        fallback=DEFAULT_RISK_CONTRIBUTION_TERMS,
    )

    return any(
        contains_any(
            sentence,
            strong_risk_terms,
        )
        and contains_any(
            sentence,
            contribution_terms,
        )
        for sentence in _sentences(text)
    )

def _has_neural_privacy_context(
    text: str,
    classification: dict,
) -> bool:
    """
    Distingue privacidade cerebral de privacidade de redes neurais
    artificiais.
    """

    if contains_any(
        text,
        [
            "mental privacy",
            "brain data privacy",
            "brain privacy",
        ],
    ):
        return True

    if not contains_any(text, ["neural privacy"]):
        return False

    context_terms = _config_terms(
        classification,
        "neural_signal_terms",
        fallback=DEFAULT_NEURAL_SIGNAL_TERMS,
    ) + [
        "brain",
        "neurotechnology",
        "neurotechnologies",
        "neuroethics",
        "neurorights",
    ]

    return (
        _has_explicit_interface(text, classification)
        or contains_any(text, context_terms)
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
    result = _normalize_semantic_text(text)
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

    normalized_title = _normalize_semantic_text(title)

    return any(
        normalized_title.startswith(
            _normalize_semantic_text(prefix)
        )
        for prefix in prefixes
    )


def _has_explicit_interface(
    text: str,
    classification: dict,
) -> bool:
    """
    Identifica BMI/BCI evitando interpretar automaticamente
    "neural interface" como interface neural humana.
    """

    strong_phrases = _config_terms(
        classification,
        "strong_interface_terms",
        "explicit_interface_terms",
        "interface_terms",
        fallback=DEFAULT_STRONG_INTERFACE_TERMS,
    )

    ambiguous_interface_terms = _config_terms(
        classification,
        "ambiguous_interface_terms",
        fallback=DEFAULT_AMBIGUOUS_INTERFACE_TERMS,
    )

    # Mesmo que uma configuração antiga ainda inclua "neural interface"
    # na lista explícita, ela será removida da evidência forte.
    ambiguous_keys = {
        value.strip().casefold()
        for value in ambiguous_interface_terms
    }

    strong_phrases = [
        value
        for value in strong_phrases
        if value.strip().casefold() not in ambiguous_keys
    ]

    abbreviations = _config_terms(
        classification,
        "interface_abbreviations",
        fallback=DEFAULT_INTERFACE_ABBREVIATIONS,
    )

    abbreviation_context_terms = _config_terms(
        classification,
        "interface_context_terms",
        fallback=DEFAULT_INTERFACE_CONTEXT_TERMS,
    )

    neural_interface_context_terms = _config_terms(
        classification,
        "neural_interface_context_terms",
        fallback=DEFAULT_NEURAL_INTERFACE_CONTEXT_TERMS,
    )

    ambiguous_bci_terms = _config_terms(
        classification,
        "ambiguous_bci_terms",
        fallback=DEFAULT_AMBIGUOUS_BCI_TERMS,
    )

    if contains_any(text, ambiguous_bci_terms):
        return False

    if contains_any(text, strong_phrases):
        return True

    # "Neural interface" só conta quando compartilha sentença com
    # evidência cerebral, fisiológica ou neurotecnológica.
    if _same_sentence_has(
        text,
        ambiguous_interface_terms,
        neural_interface_context_terms,
    ):
        return True

    # BCI/BMI só contam com contexto cerebral na mesma sentença.
    return _same_sentence_has(
        text,
        abbreviations,
        abbreviation_context_terms,
    )


def _semantic_evidence(
    title: str,
    abstract: str,
    classification: dict,
) -> SemanticEvidence:
    interface_terms = (
        _config_terms(
            classification,
            "strong_interface_terms",
            "explicit_interface_terms",
            "interface_terms",
            fallback=DEFAULT_STRONG_INTERFACE_TERMS,
        )
        + _config_terms(
            classification,
            "ambiguous_interface_terms",
            fallback=DEFAULT_AMBIGUOUS_INTERFACE_TERMS,
        )
        + _config_terms(
            classification,
            "interface_abbreviations",
            fallback=DEFAULT_INTERFACE_ABBREVIATIONS,
        )
    )

    brain_terms = _config_terms(
        classification,
        "brain_context_terms",
        "broad_neuro_terms",
        fallback=DEFAULT_BRAIN_CONTEXT_TERMS,
    )

    neural_signal_terms = _config_terms(
        classification,
        "neural_signal_terms",
        fallback=DEFAULT_NEURAL_SIGNAL_TERMS,
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
        "a1_language_technology_terms",
        fallback=DEFAULT_A1_LANGUAGE_TECHNOLOGY_TERMS,
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

    strong_risk_terms = _config_terms(
        classification,
        "strong_risk_governance_terms",
        fallback=DEFAULT_STRONG_RISK_TERMS,
    )

    technology_terms = [
        *llm_terms,
        *language_terms,
    ]

    title_text = _normalize_semantic_text(title)

    semantic_terms = [
        *interface_terms,
        *brain_terms,
        *neural_signal_terms,
        *decoding_terms,
        *technology_terms,
        *human_terms,
        *risk_terms,
        *strong_risk_terms,
    ]

    abstract_text = _mask_negated_mentions(
        abstract.lower(),
        semantic_terms,
    )

    return SemanticEvidence(
        interface_title=_has_explicit_interface(
            title_text,
            classification,
        ),
        interface_abstract=_has_explicit_interface(
            abstract_text,
            classification,
        ),

        brain_title=contains_any(
            title_text,
            brain_terms,
        ),
        brain_abstract=contains_any(
            abstract_text,
            brain_terms,
        ),

        neural_signal_title=contains_any(
            title_text,
            neural_signal_terms,
        ),
        neural_signal_abstract=contains_any(
            abstract_text,
            neural_signal_terms,
        ),

        decoding_title=contains_any(
            title_text,
            decoding_terms,
        ),
        decoding_abstract=contains_any(
            abstract_text,
            decoding_terms,
        ),

        llm_title=contains_any(
            title_text,
            llm_terms,
        ),
        llm_abstract=contains_any(
            abstract_text,
            llm_terms,
        ),

        language_title=contains_any(
            title_text,
            language_terms,
        ),
        language_abstract=contains_any(
            abstract_text,
            language_terms,
        ),

        human_title=contains_any(
            title_text,
            human_terms,
        ),
        human_abstract=contains_any(
            abstract_text,
            human_terms,
        ),

        risk_title=contains_any(
            title_text,
            risk_terms,
        ),
        risk_abstract=contains_any(
            abstract_text,
            risk_terms,
        ),

        strong_risk_title=contains_any(
            title_text,
            strong_risk_terms,
        ),
        strong_risk_abstract=contains_any(
            abstract_text,
            strong_risk_terms,
        ),

        integration_title=_has_integration_relation(
            title_text,
            classification,
            technology_terms,
        ),
        integration_abstract=_has_integration_relation(
            abstract_text,
            classification,
            technology_terms,
        ),

        weak_integration_title=_has_weak_integration_relation(
            title_text,
            classification,
            technology_terms,
        ),
        weak_integration_abstract=_has_weak_integration_relation(
            abstract_text,
            classification,
            technology_terms,
        ),

        interface_language_same_sentence=(
            _same_sentence_has_valid_interface_and(
                abstract_text,
                classification,
                technology_terms,
            )
        ),

        decoding_language_same_sentence=_same_sentence_has(
            abstract_text,
            decoding_terms,
            technology_terms,
        ),

        brain_decoding_same_sentence=_same_sentence_has(
            abstract_text,
            brain_terms,
            decoding_terms,
        ),

        neural_signal_decoding_same_sentence=_same_sentence_has(
            abstract_text,
            neural_signal_terms,
            decoding_terms,
        ),

        interface_risk_same_sentence=(
            _same_sentence_has_valid_interface_and(
                abstract_text,
                classification,
                risk_terms,
            )
        ),

        interface_strong_risk_same_sentence=(
            _same_sentence_has_valid_interface_and(
                abstract_text,
                classification,
                strong_risk_terms,
            )
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

    `venue`, `query` e `source_api` são mantidos por compatibilidade,
    mas não participam da classificação semântica.
    """

    classification = config.get("classification", {})

    if not isinstance(classification, dict):
        classification = {}

    clean_title = (title or "").strip()

    if not clean_title:
        return "D-descartar"

    semantic_text = normalize_text(
        clean_title,
        abstract,
    )

    if _is_review_comment(
        clean_title,
        classification,
    ):
        return "D-descartar"

    false_terms = _config_terms(
        classification,
        "false_positive_terms",
        fallback=DEFAULT_FALSE_POSITIVE_TERMS,
    )

    if contains_any(semantic_text, false_terms):
        return "D-descartar"

    evidence = _semantic_evidence(
        clean_title,
        abstract,
        classification,
    )

    ambiguous_interface_terms = _config_terms(
        classification,
        "ambiguous_interface_terms",
        fallback=DEFAULT_AMBIGUOUS_INTERFACE_TERMS,
    )

    # "Neural interface" sem cérebro, sinal neural ou BCI é uma
    # interface entre componentes de software, não uma BMI/BCI.
    if (
        contains_any(
            semantic_text,
            ambiguous_interface_terms,
        )
        and not (
            evidence.interface_title
            or evidence.interface_abstract
            or evidence.neural_signal_title
            or evidence.neural_signal_abstract
            or evidence.decoding_title
            or evidence.decoding_abstract
        )
    ):
        return "D-descartar"

    non_neural_decoding_terms = _config_terms(
        classification,
        "non_neural_decoding_terms",
        fallback=DEFAULT_NON_NEURAL_DECODING_TERMS,
    )

    # Evita interpretar metáforas ou estudos literários como
    # decodificação neural.
    if (
        (
            evidence.decoding_title
            or evidence.decoding_abstract
        )
        and contains_any(
            semantic_text,
            non_neural_decoding_terms,
        )
        and not (
            evidence.interface_title
            or evidence.interface_abstract
            or evidence.neural_signal_title
            or evidence.neural_signal_abstract
        )
    ):
        return "D-descartar"

    external_analysis_terms = _config_terms(
        classification,
        "external_analysis_terms",
        fallback=DEFAULT_EXTERNAL_ANALYSIS_TERMS,
    )

    external_analysis_context = (
        contains_any(
            semantic_text,
            external_analysis_terms,
        )
        and not (
            evidence.decoding_title
            or evidence.decoding_abstract
            or evidence.neural_signal_title
            or evidence.neural_signal_abstract
        )
    )

    neural_domain_title = (
        evidence.interface_title
        or evidence.decoding_title
        or evidence.neural_signal_title
    )

    technology_title = (
        evidence.llm_title
        or evidence.language_title
    )

    technology_abstract = (
        evidence.llm_abstract
        or evidence.language_abstract
    )

    # A1 — integração entre BMI/BCI, sinais neurais ou decodificação
    # e modelos de linguagem.
    if (
        neural_domain_title
        and technology_title
        and not evidence.weak_integration_title
        and not external_analysis_context
    ):
        return "A1-central-integracao-llm"

    # O helper de integração já rejeita negação, comparação,
    # inspiração e descrição de trabalhos anteriores por sentença.
    if (
        neural_domain_title
        and technology_abstract
        and evidence.integration_abstract
        and not external_analysis_context
    ):
        return "A1-central-integracao-llm"

    if (
        technology_title
        and (
            evidence.interface_abstract
            or evidence.decoding_abstract
            or evidence.neural_signal_abstract
        )
        and evidence.integration_abstract
        and not external_analysis_context
    ):
        return "A1-central-integracao-llm"

    if (
        (
            evidence.interface_language_same_sentence
            or evidence.decoding_language_same_sentence
        )
        and evidence.integration_abstract
        and not external_analysis_context
    ):
        return "A1-central-integracao-llm"

    peripheral_signal_terms = _config_terms(
        classification,
        "peripheral_signal_terms",
        fallback=DEFAULT_PERIPHERAL_SIGNAL_TERMS,
    )

    peripheral_only = (
        contains_any(
            semantic_text,
            peripheral_signal_terms,
        )
        and not (
            evidence.interface_title
            or evidence.interface_abstract
            or evidence.neural_signal_title
            or evidence.neural_signal_abstract
        )
    )

    if peripheral_only:
        return "B-apoio"

    # A2 — decodificação neural de linguagem.
    #
    # A presença de "brain-to-text" ou "neural decoding" não basta:
    # deve haver interface real ou evidência de sinais/registro neural.
    if (
        evidence.decoding_title
        and (
            evidence.interface_title
            or evidence.interface_abstract
            or evidence.neural_signal_title
            or evidence.neural_signal_abstract
        )
    ):
        return "A2-central-decoding-linguagem"

    if (
        evidence.interface_title
        and evidence.decoding_abstract
        and evidence.neural_signal_abstract
    ):
        return "A2-central-decoding-linguagem"

    if evidence.neural_signal_decoding_same_sentence:
        return "A2-central-decoding-linguagem"

    # A3 — risco ou governança diretamente relacionado à BMI/BCI.
    #
    # Termos genéricos como autonomia, responsabilidade e
    # explicabilidade continuam gerando tags, mas não são suficientes
    # para promover um trabalho a A3.
    if (
        evidence.interface_title
        and evidence.strong_risk_title
    ):
        return "A3-central-riscos-governanca"

    if (
        evidence.strong_risk_title
        and evidence.interface_abstract
    ):
        return "A3-central-riscos-governanca"

    if (
        evidence.interface_title
        and _has_risk_contribution_sentence(
            abstract,
            classification,
        )
    ):
        return "A3-central-riscos-governanca"

    non_brain_terms = _config_terms(
        classification,
        "non_brain_neural_terms",
        fallback=DEFAULT_NON_BRAIN_NEURAL_TERMS,
    )

    if (
        contains_any(
            semantic_text,
            non_brain_terms,
        )
        and not (
            evidence.brain_title
            or evidence.brain_abstract
            or evidence.neural_signal_title
            or evidence.neural_signal_abstract
            or evidence.interface_title
            or evidence.interface_abstract
            or evidence.decoding_title
            or evidence.decoding_abstract
        )
    ):
        return "D-descartar"

    # Literatura de apoio.
    if (
        evidence.interface_title
        or evidence.interface_abstract
        or evidence.brain_title
        or evidence.neural_signal_title
        or evidence.decoding_title
    ):
        return "B-apoio"

    if (
        (
            evidence.llm_title
            or evidence.llm_abstract
        )
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

    if contains_any(
        text,
        ["body mass index", "body-mass index"],
    ):
        tags.discard("domain:bmi")

    # "Neural interface" de software não recebe tag de interface
    # neural humana.
    if (
        "domain:neural-interface" in tags
        and not _has_explicit_interface(
            text,
            classification,
        )
    ):
        tags.discard("domain:neural-interface")

    # "Neural privacy" só recebe a tag específica quando há
    # contexto cerebral ou neurotecnológico.
    if (
        "governance:neural-privacy" in tags
        and not _has_neural_privacy_context(
            text,
            classification,
        )
    ):
        tags.discard("governance:neural-privacy")

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

    priority = suggest_priority(
        config or {},
        title or "",
        abstract=abstract or "",
    )

    if priority == "A1-central-integracao-llm":
        return "Integração BMI/BCI e LLMs"

    if priority == "A2-central-decoding-linguagem":
        return "Decodificação Neural de Linguagem"

    if priority == "A3-central-riscos-governanca":
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
