from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from neuro_mapper.pipeline import normalize_doi, normalize_title


V4_2_PATH = Path(
    "outputs/resultados_neuro_piloto_v4_2.csv"
)

V4_3_PATH = Path(
    "outputs/resultados_neuro_piloto_v4_3.csv"
)

TRANSITIONS_OUTPUT = Path(
    "outputs/comparacao_v4_2_v4_3_transicoes.csv"
)

CHANGED_RECORDS_OUTPUT = Path(
    "outputs/comparacao_v4_2_v4_3_registros_alterados.csv"
)

CENTRAL_PRIORITIES = {
    "A1-central-integracao-llm",
    "A2-central-decoding-linguagem",
    "A3-central-riscos-governanca",
}

SOURCE_ORDER = {
    "crossref": 0,
    "openalex": 1,
    "semantic scholar": 2,
}


def load_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise SystemExit(f"Arquivo não encontrado: {path}")

    dataframe = pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )

    for column in dataframe.columns:
        dataframe[column] = (
            dataframe[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    return dataframe


def record_key(row: pd.Series) -> str:
    doi = normalize_doi(
        row.get("doi", "")
    )

    if doi:
        return f"doi:{doi}"

    title = normalize_title(
        row.get("title", "")
    )

    if title:
        return f"title:{title}"

    return ""


def numeric_sum(
    dataframe: pd.DataFrame,
    column: str,
) -> int:
    if column not in dataframe.columns:
        return 0

    values = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    ).fillna(0)

    return int(values.sum())


def print_distribution(
    dataframe: pd.DataFrame,
    column: str,
    label: str,
) -> None:
    print(f"\n{label}")

    if column not in dataframe.columns:
        print(f"Coluna ausente: {column}")
        return

    counts = (
        dataframe[column]
        .replace("", "(vazio)")
        .value_counts(dropna=False)
    )

    total = len(dataframe)

    for value, count in counts.items():
        percentage = (
            100 * count / total
            if total
            else 0
        )

        print(
            f"  {value}: "
            f"{count} "
            f"({percentage:.1f}%)"
        )


def canonical_source_value(value: str) -> str:
    parts = [
        part.strip()
        for part in str(value or "").split("|")
        if part.strip()
    ]

    unique: dict[str, str] = {}

    for part in parts:
        key = re.sub(
            r"[_\s]+",
            " ",
            part.casefold(),
        ).strip()

        unique.setdefault(key, part)

    ordered = sorted(
        unique.items(),
        key=lambda item: (
            SOURCE_ORDER.get(
                item[0],
                99,
            ),
            item[0],
        ),
    )

    canonical_names = {
        "crossref": "Crossref",
        "openalex": "OpenAlex",
        "semantic scholar": "Semantic Scholar",
    }

    return " | ".join(
        canonical_names.get(key, display)
        for key, display in ordered
    )


def validate_hygiene(
    dataframe: pd.DataFrame,
    path: Path,
) -> None:
    priority = dataframe.get(
        "suggested_priority",
        pd.Series("", index=dataframe.index),
    )

    publication_status = dataframe.get(
        "publication_status",
        pd.Series("", index=dataframe.index),
    )

    title = dataframe.get(
        "title",
        pd.Series("", index=dataframe.index),
    )

    central_mask = priority.isin(
        CENTRAL_PRIORITIES
    )

    supplementary_central = dataframe[
        publication_status.eq(
            "supplementary-material"
        )
        & central_mask
    ]

    missing_title_central = dataframe[
        title.str.strip().eq("")
        & central_mask
    ]

    source_values = dataframe.get(
        "source_api",
        pd.Series("", index=dataframe.index),
    )

    source_order_errors = dataframe[
        source_values.map(
            canonical_source_value
        )
        != source_values
    ]

    integer_columns = [
        "year",
        "cited_by_count",
        "duplicate_count",
    ]

    decimal_suffix_errors: dict[str, int] = {}

    for column in integer_columns:
        if column not in dataframe.columns:
            decimal_suffix_errors[column] = 0
            continue

        values = (
            dataframe[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        decimal_suffix_errors[column] = int(
            values.str.fullmatch(
                r"[+-]?\d+\.0",
                na=False,
            ).sum()
        )

    total_decimal_suffix_errors = sum(
        decimal_suffix_errors.values()
    )

    print("\nVALIDAÇÕES DE HIGIENE")
    print(
        "  Suplementares classificados como centrais:",
        len(supplementary_central),
    )
    print(
        "  Registros sem título classificados como centrais:",
        len(missing_title_central),
    )
    print(
        "  Registros com source_api fora da ordem canônica:",
        len(source_order_errors),
    )
    print(
        "  Valores inteiros exportados com sufixo .0:",
        total_decimal_suffix_errors,
    )

    for column, errors in decimal_suffix_errors.items():
        print(
            f"    {column}: {errors}"
        )


def prepare_comparison(
    dataframe: pd.DataFrame,
    suffix: str,
) -> pd.DataFrame:
    prepared = dataframe.copy()

    prepared["record_key"] = prepared.apply(
        record_key,
        axis=1,
    )

    prepared = prepared[
        prepared["record_key"].ne("")
    ].copy()

    selected_columns = [
        "record_key",
        "title",
        "doi",
        "source_api",
        "suggested_priority",
        "suggested_tags",
        "corrente",
        "publication_status",
        "metadata_completeness",
        "duplicate_count",
    ]

    selected_columns = [
        column
        for column in selected_columns
        if column in prepared.columns
    ]

    prepared = prepared[
        selected_columns
    ].copy()

    return prepared.rename(
        columns={
            column: f"{column}_{suffix}"
            for column in selected_columns
            if column != "record_key"
        }
    )


def main() -> None:
    v4_2 = load_csv(V4_2_PATH)
    v4_3 = load_csv(V4_3_PATH)

    print("=" * 72)
    print("COMPARAÇÃO V4.2 × V4.3")
    print("=" * 72)

    print("\nVOLUMES")
    print("  Registros v4.2:", len(v4_2))
    print("  Registros v4.3:", len(v4_3))
    print(
        "  Variação:",
        len(v4_3) - len(v4_2),
    )

    print(
        "  Ocorrências antes da deduplicação v4.2:",
        numeric_sum(v4_2, "duplicate_count"),
    )
    print(
        "  Ocorrências antes da deduplicação v4.3:",
        numeric_sum(v4_3, "duplicate_count"),
    )

    print_distribution(
        v4_2,
        "suggested_priority",
        "PRIORIDADES V4.2",
    )

    print_distribution(
        v4_3,
        "suggested_priority",
        "PRIORIDADES V4.3",
    )

    print_distribution(
        v4_2,
        "publication_status",
        "STATUS DE PUBLICAÇÃO V4.2",
    )

    print_distribution(
        v4_3,
        "publication_status",
        "STATUS DE PUBLICAÇÃO V4.3",
    )

    print_distribution(
        v4_2,
        "metadata_completeness",
        "COMPLETUDE V4.2",
    )

    print_distribution(
        v4_3,
        "metadata_completeness",
        "COMPLETUDE V4.3",
    )

    validate_hygiene(v4_3)

    left = prepare_comparison(
        v4_2,
        "v4_2",
    )

    right = prepare_comparison(
        v4_3,
        "v4_3",
    )

    comparison = left.merge(
        right,
        on="record_key",
        how="outer",
        indicator=True,
    )

    print("\nCOBERTURA ENTRE AS EXECUÇÕES")
    print(
        "  Presentes nas duas:",
        int((comparison["_merge"] == "both").sum()),
    )
    print(
        "  Somente na v4.2:",
        int((comparison["_merge"] == "left_only").sum()),
    )
    print(
        "  Somente na v4.3:",
        int((comparison["_merge"] == "right_only").sum()),
    )

    both = comparison[
        comparison["_merge"].eq("both")
    ].copy()

    priority_v4_2 = both[
        "suggested_priority_v4_2"
    ]

    priority_v4_3 = both[
        "suggested_priority_v4_3"
    ]

    changed = both[
        priority_v4_2.ne(priority_v4_3)
    ].copy()

    transitions = (
        changed.groupby(
            [
                "suggested_priority_v4_2",
                "suggested_priority_v4_3",
            ],
            dropna=False,
        )
        .size()
        .reset_index(name="records")
        .sort_values(
            "records",
            ascending=False,
        )
    )

    print("\nTRANSIÇÕES DE PRIORIDADE")
    print("  Registros comparáveis:", len(both))
    print(
        "  Prioridade alterada:",
        len(changed),
    )

    if transitions.empty:
        print("  Nenhuma transição encontrada.")
    else:
        print(
            transitions.to_string(
                index=False
            )
        )

    central_v4_2 = priority_v4_2.isin(
        CENTRAL_PRIORITIES
    )

    central_v4_3 = priority_v4_3.isin(
        CENTRAL_PRIORITIES
    )

    print("\nMOVIMENTOS DO NÚCLEO CENTRAL")
    print(
        "  Central → B/D:",
        int(
            (
                central_v4_2
                & ~central_v4_3
            ).sum()
        ),
    )
    print(
        "  B/D → Central:",
        int(
            (
                ~central_v4_2
                & central_v4_3
            ).sum()
        ),
    )
    print(
        "  Central mantido:",
        int(
            (
                central_v4_2
                & central_v4_3
            ).sum()
        ),
    )

    TRANSITIONS_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    transitions.to_csv(
        TRANSITIONS_OUTPUT,
        index=False,
        encoding="utf-8-sig",
    )

    changed_columns = [
        "record_key",
        "title_v4_2",
        "title_v4_3",
        "suggested_priority_v4_2",
        "suggested_priority_v4_3",
        "corrente_v4_2",
        "corrente_v4_3",
        "publication_status_v4_2",
        "publication_status_v4_3",
        "source_api_v4_2",
        "source_api_v4_3",
    ]

    changed_columns = [
        column
        for column in changed_columns
        if column in changed.columns
    ]

    changed[
        changed_columns
    ].to_csv(
        CHANGED_RECORDS_OUTPUT,
        index=False,
        encoding="utf-8-sig",
    )

    print("\nARQUIVOS GERADOS")
    print(" ", TRANSITIONS_OUTPUT)
    print(" ", CHANGED_RECORDS_OUTPUT)


if __name__ == "__main__":
    main()