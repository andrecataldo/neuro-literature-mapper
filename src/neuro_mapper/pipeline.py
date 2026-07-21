from __future__ import annotations

import re
import unicodedata
from copy import deepcopy
from typing import Iterable

from neuro_mapper.models import WorkRecord
from neuro_mapper.sources.common import ApiRequestError
from neuro_mapper.sources.crossref import search_crossref
from neuro_mapper.sources.openalex import search_openalex
from neuro_mapper.sources.semantic_scholar import search_semantic_scholar
from neuro_mapper.tagging import infer_corrente, suggest_priority, suggest_tags


SOURCE_QUALITY = {
    "openalex": 3,
    "semantic scholar": 2,
    "crossref": 1,
}

SOURCE_CANONICAL_NAMES = {
    "crossref": "Crossref",
    "openalex": "OpenAlex",
    "semantic scholar": "Semantic Scholar",
}

SOURCE_CANONICAL_ORDER = {
    "crossref": 0,
    "openalex": 1,
    "semantic scholar": 2,
}

SUPPLEMENTARY_PATTERNS = [
    # Materiais explicitamente identificados como anexos.
    r"\b(?:supplementary|supplemental)\s+"
    r"(?:material|materials|file|files|data|dataset|appendix|"
    r"figure|figures|table|tables)\b",

    # Exemplos: _supp1, -supp4-, supp2.xlsx.
    r"(?:^|[_\-\s])supp\d+(?:[_\-\s.]|$)",

    # Extensões típicas de arquivos auxiliares.
    r"\.(?:png|jpe?g|gif|tiff?|xlsx?|xls|docx?|pptx?|"
    r"zip|rar|7z|csv)(?:$|[?#])",

        # Ativos editoriais retornados como registros independentes.
    # Exemplos: "Figure 4:", "Fig. 2:", "Table 3:".
    r"^\s*(?:fig(?:ure)?\.?|table)\s+"
    r"\d+[a-z]?\s*[:.\-]",

    # DOI ou URL de figuras e tabelas.
    # Exemplos: /fig-4, /figure-2, /table-3.
    r"(?:/|#)(?:fig(?:ure)?|table)-?"
    r"\d+[a-z]?(?:$|[?#\s])",
]

SOURCE_HANDLERS = [
    ("openalex", "OpenAlex", search_openalex),
    ("crossref", "Crossref", search_crossref),
    (
        "semantic_scholar",
        "Semantic Scholar",
        search_semantic_scholar,
    ),
]

def run_api_search(
    config: dict,
) -> list[WorkRecord]:
    """
    Executa buscas, filtra por ano, deduplica e classifica.

    Cada adaptador controla seu próprio intervalo de chamadas,
    tentativas e tratamento de rate limit.
    """

    settings = config.get("settings", {})
    per_page = int(settings.get("per_page", 20))
    layers = config.get("api_layers", [])

    configured_sources = settings.get(
        "enabled_sources",
        [
            "openalex",
            "crossref",
            "semantic_scholar",
        ],
    )

    enabled_sources = {
        str(source).strip().lower()
        for source in configured_sources
    }

    all_records: list[WorkRecord] = []
    blocked_sources: set[str] = set()

    for layer in layers:
        layer_name = str(
            layer.get("name", "")
        ).strip()

        for query in layer.get("queries", []):
            for (
                source_key,
                source_name,
                search_fn,
            ) in SOURCE_HANDLERS:
                if source_key not in enabled_sources:
                    continue

                if source_key in blocked_sources:
                    continue

                try:
                    print(
                        f"[{source_name}] "
                        f"{layer_name} :: {query}"
                    )

                    records = search_fn(
                        query,
                        layer_name,
                        config,
                        per_page=per_page,
                    )

                    all_records.extend(records)

                    print(
                        f"[{source_name}] "
                        f"{len(records)} registros"
                    )

                except ApiRequestError as exc:
                    print(
                        f"ERRO em {source_name} "
                        f"para query {query}: {exc}"
                    )

                    # Evita repetir dezenas de chamadas quando
                    # a chave está inválida, o acesso foi proibido
                    # ou o limite da fonte foi atingido.
                    if exc.status_code in {
                        401,
                        403,
                        429,
                    }:
                        blocked_sources.add(source_key)

                        print(
                            f"[{source_name}] suspensa "
                            "pelo restante desta execução."
                        )

                except Exception as exc:
                    print(
                        f"ERRO inesperado em "
                        f"{source_name} para query "
                        f"{query}: "
                        f"{exc.__class__.__name__}: "
                        f"{exc}"
                    )

    filtered = filter_records_by_year(
        all_records,
        config,
    )

    unique = deduplicate_records(filtered)

    return classify_records(
        unique,
        config,
    )

def filter_records_by_year(
    records: Iterable[WorkRecord],
    config: dict,
) -> list[WorkRecord]:
    """
    Aplica `year_min` e `year_max` após a recuperação.

    Registros sem ano são mantidos para revisão manual. O filtro pode ser
    desativado com `settings.enforce_year_filter: false`.
    """
    settings = config.get("settings", {})

    if not bool(settings.get("enforce_year_filter", True)):
        return list(records)

    year_min = _optional_int(settings.get("year_min"))
    year_max = _optional_int(settings.get("year_max"))

    filtered: list[WorkRecord] = []

    for record in records:
        if record.year is None:
            filtered.append(record)
            continue

        if year_min is not None and record.year < year_min:
            continue

        if year_max is not None and record.year > year_max:
            continue

        filtered.append(record)

    return filtered


def classify_records(
    records: Iterable[WorkRecord],
    config: dict,
) -> list[WorkRecord]:
    """
    Classifica relevância usando apenas título e resumo.

    Venue, query e fonte são usados para rastreabilidade, status da publicação
    e completude dos metadados, nunca como evidência semântica.

    Registros inválidos ou materiais suplementares são descartados antes da
    classificação temática.
    """

    classified: list[WorkRecord] = []

    for record in records:
        record.publication_status = infer_publication_status(
            record,
            config,
        )

        has_title = bool(
            (record.title or "").strip()
        )

        discard_for_hygiene = (
            not has_title
            or record.publication_status == "supplementary-material"
        )

        if discard_for_hygiene:
            record.suggested_priority = "D-descartar"
            record.suggested_tags = ""
            record.corrente = (
                "Literatura de apoio / A classificar"
            )
        else:
            record.suggested_priority = suggest_priority(
                config=config,
                title=record.title,
                abstract=record.abstract,
                venue=record.venue,
                query="",
                source_api=record.source_api,
            )

            record.suggested_tags = "; ".join(
                suggest_tags(
                    config,
                    record.title,
                    record.abstract,
                )
            )

            record.corrente = infer_corrente(
                record.title,
                record.abstract,
                config,
            )

        record.metadata_completeness = (
            infer_metadata_completeness(record)
        )

        record.classification_confidence = ""
        classified.append(record)

    return classified

def is_supplementary_material(
    record: WorkRecord,
) -> bool:
    """
    Detecta arquivos auxiliares, materiais suplementares e ativos
    editoriais.

    A análise usa título, URL e DOI. A palavra isolada
    "supplementary" não é suficiente, evitando falsos positivos
    como "supplementary motor area".
    """

    text = " ".join(
        [
            record.title or "",
            record.url or "",
            record.doi or "",
        ]
    ).strip().lower()

    if not text:
        return False

    return any(
        re.search(pattern, text, flags=re.IGNORECASE)
        is not None
        for pattern in SUPPLEMENTARY_PATTERNS
    )

def infer_publication_status(
    record: WorkRecord,
    config: dict,
) -> str:
    """
    Infere o status bibliográfico sem confundi-lo com relevância temática.

    Valores:
    - supplementary-material
    - review-comment
    - preprint
    - published-record
    - unknown
    """
    classification = config.get("classification", {})
    if not isinstance(classification, dict):
        classification = {}
    if is_supplementary_material(record):
        return "supplementary-material"

    review_prefixes = classification.get(
        "review_comment_prefixes",
        [
            "review of:",
            "review of ",
            "comment on:",
            "commentary on:",
            "response to:",
            "author response:",
            "peer review of:",
        ],
    )
    title = (record.title or "").strip().lower()

    if any(title.startswith(str(prefix).lower()) for prefix in review_prefixes):
        return "review-comment"

    preprint_terms = classification.get(
        "preprint_terms",
        ["arxiv", "biorxiv", "medrxiv", "ssrn", "preprint"],
    )
    publication_text = " ".join(
        [
            record.source_api or "",
            record.venue or "",
            record.url or "",
            record.title or "",
        ]
    ).lower()

    if any(str(term).lower() in publication_text for term in preprint_terms):
        return "preprint"

    if (record.doi or "").strip() or (record.venue or "").strip():
        return "published-record"

    return "unknown"


def infer_metadata_completeness(record: WorkRecord) -> str:
    """
    Mede completude dos metadados, não confiança epistemológica.

    - high: resumo informativo, venue, autores, ano e DOI;
    - medium: resumo presente, mas algum metadado importante está ausente;
    - low: resumo ausente.
    """
    title = (record.title or "").strip()
    abstract = (record.abstract or "").strip()

    if not title or not abstract:
        return "low"

    complete_core = all(
        [
            len(abstract) >= 200,
            bool((record.venue or "").strip()),
            bool((record.authors or "").strip()),
            record.year is not None,
            bool((record.doi or "").strip()),
        ]
    )

    return "high" if complete_core else "medium"


def deduplicate_records(
    records: Iterable[WorkRecord],
) -> list[WorkRecord]:
    """
    Deduplica por DOI normalizado e por título normalizado.

    Quando várias fontes descrevem o mesmo trabalho, preserva o registro mais
    completo e combina proveniência, queries e metadados complementares.
    """
    groups: list[list[WorkRecord]] = []
    doi_to_group: dict[str, int] = {}
    title_to_group: dict[str, int] = {}

    for record in records:
        doi_key = normalize_doi(record.doi)
        title_key = normalize_title(record.title)

        matching_groups = {
            group_index
            for key, mapping in (
                (doi_key, doi_to_group),
                (title_key, title_to_group),
            )
            if key and (group_index := mapping.get(key)) is not None
        }

        if not matching_groups:
            group_index = len(groups)
            groups.append([record])
        else:
            group_index = min(matching_groups)
            groups[group_index].append(record)

            # Se DOI e título apontaram para grupos distintos, unifique-os.
            for other_index in sorted(matching_groups - {group_index}, reverse=True):
                groups[group_index].extend(groups[other_index])
                groups[other_index] = []

                for mapping in (doi_to_group, title_to_group):
                    for key, index in list(mapping.items()):
                        if index == other_index:
                            mapping[key] = group_index

        if doi_key:
            doi_to_group[doi_key] = group_index

        if title_key:
            title_to_group[title_key] = group_index

    return [
        merge_duplicate_group(group)
        for group in groups
        if group
    ]


def merge_duplicate_group(records: list[WorkRecord]) -> WorkRecord:
    """Combina registros duplicados priorizando metadados mais completos."""
    if not records:
        raise ValueError("O grupo de duplicatas não pode ser vazio.")

    ranked = sorted(
        records,
        key=record_quality_score,
        reverse=True,
    )
    merged = deepcopy(ranked[0])

    merged.source_api = _join_sources(
        record.source_api for record in records
    )
    merged.query_layer = _join_unique(
        record.query_layer for record in records
    )
    merged.query = _join_unique(
        record.query for record in records
    )

    merged.title = _best_text(records, "title", prefer_longest=False)
    merged.authors = _best_text(records, "authors", prefer_longest=True)
    merged.venue = _best_text(records, "venue", prefer_longest=False)
    merged.abstract = _best_text(records, "abstract", prefer_longest=True)
    merged.notes = _join_unique(record.notes for record in records)
    merged.decision = _first_nonempty(record.decision for record in ranked)

    merged.seed_source = _join_unique(
        (
            record.seed_source or record.professor_source
            for record in records
        )
    )
    merged.professor_source = ""

    merged.doi = _first_nonempty(
        normalize_doi(record.doi) for record in ranked
    )
    merged.url = _select_url(ranked, merged.doi)
    merged.year = _first_non_none(record.year for record in ranked)

    citation_counts = [
        record.cited_by_count
        for record in records
        if record.cited_by_count is not None
    ]
    merged.cited_by_count = max(citation_counts) if citation_counts else None

    merged.duplicate_count = sum(
        max(1, int(getattr(record, "duplicate_count", 1)))
        for record in records
    )

    # A classificação será recalculada após a deduplicação.
    merged.suggested_priority = ""
    merged.suggested_tags = ""
    merged.corrente = ""
    merged.publication_status = ""
    merged.metadata_completeness = ""
    merged.classification_confidence = ""

    return merged


def record_quality_score(record: WorkRecord) -> tuple[int, int, int]:
    """Pontua completude e confiabilidade relativa do registro."""
    score = 0

    if normalize_doi(record.doi):
        score += 6
    if record.abstract.strip():
        score += 6
    if record.venue.strip():
        score += 4
    if record.authors.strip():
        score += 3
    if record.url.strip():
        score += 2
    if record.year is not None:
        score += 2
    if record.cited_by_count is not None:
        score += 1

    source_score = max(
        (
            SOURCE_QUALITY.get(source.strip().lower(), 0)
            for source in record.source_api.split("|")
        ),
        default=0,
    )

    return score, source_score, len(record.abstract or "")


def normalize_doi(doi: str | None) -> str:
    """Normaliza DOI removendo URL, prefixo e pontuação externa."""
    value = (doi or "").strip().lower()

    value = re.sub(
        r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)",
        "",
        value,
    )
    return value.strip().rstrip(".,;)")


def normalize_title(title: str | None) -> str:
    """Normaliza título para deduplicação exata tolerante a pontuação."""
    value = unicodedata.normalize("NFKD", title or "")
    value = "".join(
        character
        for character in value
        if not unicodedata.combining(character)
    )
    value = value.casefold()

    # Remove prefixos editoriais que não fazem parte do título.
    value = re.sub(
        r"^(?:(?:paper|article|manuscript)\s+)?"
        r"title\s*[:\-]\s*",
        "",
        value,
    )

    # Remove marcadores finais de versão, mas não remove "Review of".
    value = re.sub(
        r"^(?:preprint|accepted manuscript)\s*[:\-]?\s*",
        "",
        value,
    )
    value = re.sub(
        r"\s*[\[(]?(?:preprint|accepted manuscript)[\])]?$",
        "",
        value,
    )
    value = re.sub(r"\b(?:version|v)\s*\d+\b\s*$", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _select_url(
    ranked_records: list[WorkRecord],
    doi: str,
) -> str:
    if doi:
        return f"https://doi.org/{doi}"

    return _first_nonempty(
        record.url.strip() for record in ranked_records
    )


def _best_text(
    records: list[WorkRecord],
    field_name: str,
    *,
    prefer_longest: bool,
) -> str:
    values = [
        str(getattr(record, field_name, "") or "").strip()
        for record in records
    ]
    values = [value for value in values if value]

    if not values:
        return ""

    if prefer_longest:
        return max(values, key=len)

    ranked_records = sorted(
        records,
        key=record_quality_score,
        reverse=True,
    )
    return _first_nonempty(
        str(getattr(record, field_name, "") or "").strip()
        for record in ranked_records
    )

def _normalize_source_key(source: str) -> str:
    """Normaliza o identificador de uma fonte bibliográfica."""

    value = source.strip().casefold()
    value = re.sub(r"[_\s]+", " ", value)

    return value.strip()


def _join_sources(values: Iterable[str]) -> str:
    """
    Combina fontes em ordem canônica e sem duplicatas.

    Ordem:
    Crossref | OpenAlex | Semantic Scholar
    """

    sources: dict[str, str] = {}

    for value in values:
        for part in str(value or "").split("|"):
            cleaned = part.strip()

            if not cleaned:
                continue

            source_key = _normalize_source_key(cleaned)

            canonical_name = SOURCE_CANONICAL_NAMES.get(
                source_key,
                cleaned,
            )

            sources.setdefault(
                source_key,
                canonical_name,
            )

    ordered_sources = sorted(
        sources.items(),
        key=lambda item: (
            SOURCE_CANONICAL_ORDER.get(
                item[0],
                99,
            ),
            item[0],
        ),
    )

    return " | ".join(
        display_name
        for _, display_name in ordered_sources
    )

def _join_unique(values: Iterable[str]) -> str:
    unique: list[str] = []
    seen: set[str] = set()

    for value in values:
        for part in str(value or "").split("|"):
            cleaned = part.strip()
            key = cleaned.casefold()

            if cleaned and key not in seen:
                seen.add(key)
                unique.append(cleaned)

    return " | ".join(unique)


def _first_nonempty(values: Iterable[str]) -> str:
    return next((value for value in values if value), "")


def _first_non_none(values: Iterable[int | None]) -> int | None:
    return next((value for value in values if value is not None), None)


def _optional_int(value: object) -> int | None:
    if value in (None, ""):
        return None

    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Valor de ano inválido na configuração: {value!r}"
        ) from exc
