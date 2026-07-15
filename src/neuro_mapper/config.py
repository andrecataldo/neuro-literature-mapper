from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


DEFAULT_TAXONOMY_FILENAME = "taxonomy_neuro.yaml"
DEFAULT_VENUES_FILENAME = "venues_neuro.yaml"

# Metadados dos arquivos complementares não devem substituir
# os metadados principais definidos em queries_neuro.yaml.
SUPPLEMENTAL_METADATA_KEYS = {"schema_version", "project"}


class ConfigError(ValueError):
    """Erro de leitura, estrutura ou combinação dos arquivos de configuração."""


def _read_yaml(path: Path) -> dict[str, Any]:
    """Lê um YAML e garante que sua raiz seja um mapeamento."""
    if not path.exists():
        raise ConfigError(f"Arquivo de configuração não encontrado: {path}")

    if not path.is_file():
        raise ConfigError(f"O caminho de configuração não é um arquivo: {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise ConfigError(f"YAML inválido em {path}: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"Não foi possível ler {path}: {exc}") from exc

    if data is None:
        raise ConfigError(f"Arquivo de configuração vazio: {path}")

    if not isinstance(data, dict):
        raise ConfigError(
            f"A raiz de {path} deve ser um mapeamento YAML, "
            f"mas foi encontrado {type(data).__name__}."
        )

    return data


def deep_merge(
    base: dict[str, Any],
    override: dict[str, Any],
) -> dict[str, Any]:
    """
    Mescla dois dicionários recursivamente sem alterar os originais.

    Regras:
    - dicionário + dicionário: mesclagem recursiva;
    - listas: a lista de `override` substitui a lista de `base`;
    - valores escalares: `override` substitui `base`.

    A substituição de listas é intencional: evita combinar taxonomias antigas
    com as novas e reduz duplicações ou resíduos do projeto anterior.
    """
    result = deepcopy(base)

    for key, override_value in override.items():
        base_value = result.get(key)

        if isinstance(base_value, dict) and isinstance(override_value, dict):
            result[key] = deep_merge(base_value, override_value)
        else:
            result[key] = deepcopy(override_value)

    return result


def _supplemental_payload(config: dict[str, Any]) -> dict[str, Any]:
    """
    Remove metadados de arquivos complementares antes da mesclagem.

    `queries_neuro.yaml` permanece como fonte principal para `project` e
    `schema_version`. Taxonomia e venues fornecem apenas seus blocos funcionais.
    """
    return {
        key: deepcopy(value)
        for key, value in config.items()
        if key not in SUPPLEMENTAL_METADATA_KEYS
    }


def _resolve_supplemental_path(
    queries_path: Path,
    queries_config: dict[str, Any],
    include_key: str,
    explicit_path: str | Path | None,
    default_filename: str,
) -> Path:
    """
    Resolve o caminho de um arquivo complementar.

    Ordem de precedência:
    1. caminho passado explicitamente para `load_config`;
    2. caminho definido em `includes` no YAML principal;
    3. nome padrão no mesmo diretório de `queries_neuro.yaml`.
    """
    if explicit_path is not None:
        candidate = Path(explicit_path)
    else:
        includes = queries_config.get("includes", {})

        if includes is None:
            includes = {}

        if not isinstance(includes, dict):
            raise ConfigError(
                "O bloco 'includes' de queries_neuro.yaml deve ser um mapeamento."
            )

        configured_path = includes.get(include_key, default_filename)
        candidate = Path(str(configured_path))

    if not candidate.is_absolute():
        candidate = queries_path.parent / candidate

    return candidate.resolve()


def _validate_list(config: dict[str, Any], key: str) -> None:
    value = config.get(key)
    if not isinstance(value, list):
        raise ConfigError(
            f"O bloco '{key}' deve existir e ser uma lista após a mesclagem."
        )


def _validate_dict(config: dict[str, Any], key: str) -> None:
    value = config.get(key)
    if not isinstance(value, dict):
        raise ConfigError(
            f"O bloco '{key}' deve existir e ser um mapeamento após a mesclagem."
        )


def validate_config(config: dict[str, Any]) -> None:
    """Valida os blocos mínimos esperados pelo pipeline."""
    _validate_dict(config, "project")
    _validate_dict(config, "settings")
    _validate_list(config, "api_layers")
    _validate_list(config, "venue_search_layers")
    _validate_dict(config, "classification")
    _validate_dict(config, "tags")

    classification = config["classification"]

    expected_classification_groups = (
        "neuro_terms",
        "decoding_terms",
        "llm_terms",
        "human_terms",
        "risk_terms",
        "primary_venues",
        "support_venues",
        "caution_sources",
    )

    missing = [
        key
        for key in expected_classification_groups
        if not isinstance(classification.get(key), list)
    ]

    if missing:
        formatted = ", ".join(missing)
        raise ConfigError(
            "A configuração combinada não possui todas as listas de "
            f"classificação esperadas: {formatted}"
        )


def load_config(
    config_path: str | Path,
    taxonomy_path: str | Path | None = None,
    venues_path: str | Path | None = None,
) -> dict[str, Any]:
    """
    Carrega e combina os três arquivos de configuração do projeto.

    Ordem de precedência:
    1. queries_neuro.yaml — base;
    2. taxonomy_neuro.yaml — sobrescreve classificação temática e tags;
    3. venues_neuro.yaml — sobrescreve buscas por venue e adiciona venues.

    Os caminhos de taxonomia e venues podem ser definidos explicitamente,
    pelo bloco `includes` do YAML principal ou pelos nomes padrão.
    """
    queries_path = Path(config_path).expanduser().resolve()
    queries_config = _read_yaml(queries_path)

    resolved_taxonomy_path = _resolve_supplemental_path(
        queries_path=queries_path,
        queries_config=queries_config,
        include_key="taxonomy",
        explicit_path=taxonomy_path,
        default_filename=DEFAULT_TAXONOMY_FILENAME,
    )
    resolved_venues_path = _resolve_supplemental_path(
        queries_path=queries_path,
        queries_config=queries_config,
        include_key="venues",
        explicit_path=venues_path,
        default_filename=DEFAULT_VENUES_FILENAME,
    )

    taxonomy_config = _read_yaml(resolved_taxonomy_path)
    venues_config = _read_yaml(resolved_venues_path)

    merged = deep_merge(
        queries_config,
        _supplemental_payload(taxonomy_config),
    )
    merged = deep_merge(
        merged,
        _supplemental_payload(venues_config),
    )

    validate_config(merged)
    return merged
