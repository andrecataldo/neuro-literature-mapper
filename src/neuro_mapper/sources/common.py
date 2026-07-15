from __future__ import annotations

import re
import time
from collections.abc import Iterable
from typing import Any

import requests


_LAST_REQUEST_AT: dict[str, float] = {}


class ApiRequestError(RuntimeError):
    """Erro controlado ao acessar uma API bibliográfica."""

    def __init__(
        self,
        source: str,
        status_code: int | None,
        message: str,
    ) -> None:
        self.source = source
        self.status_code = status_code

        status_text = (
            f"HTTP {status_code}"
            if status_code is not None
            else "erro de rede"
        )

        super().__init__(f"{source}: {status_text}: {message}")


def normalize_semantic_scholar_query(query: str) -> str:
    """
    Converte a query do protocolo para texto simples.

    O endpoint /paper/search do Semantic Scholar não utiliza a mesma
    sintaxe de frases e operadores usada em outros buscadores.
    """

    normalized = query.replace('"', " ")

    # Converte hífens e travessões em espaços.
    normalized = re.sub(
        r"[-‐-‒–—]+",
        " ",
        normalized,
    )

    # Remove espaços repetidos.
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def _wait_for_request_slot(
    source: str,
    minimum_interval_seconds: float,
) -> None:
    """Garante um intervalo mínimo entre chamadas da mesma fonte."""

    if minimum_interval_seconds <= 0:
        return

    source_key = source.strip().lower()
    previous_request = _LAST_REQUEST_AT.get(source_key)

    if previous_request is not None:
        elapsed = time.monotonic() - previous_request
        remaining = minimum_interval_seconds - elapsed

        if remaining > 0:
            time.sleep(remaining)

    _LAST_REQUEST_AT[source_key] = time.monotonic()


def _retry_delay(
    response: requests.Response | None,
    attempt: int,
) -> float:
    """Calcula o tempo de espera usando Retry-After ou backoff."""

    if response is not None:
        retry_after = response.headers.get("Retry-After")

        if retry_after:
            try:
                return max(float(retry_after), 0.0)
            except ValueError:
                pass

    # 1, 2, 4, 8... até o máximo de 30 segundos.
    return min(float(2**attempt), 30.0)


def request_json(
    source: str,
    url: str,
    *,
    params: dict[str, Any],
    headers: dict[str, str] | None = None,
    timeout: int = 30,
    minimum_interval_seconds: float = 0.0,
    max_retries: int = 3,
    retry_statuses: Iterable[int] = (
        429,
        500,
        502,
        503,
        504,
    ),
) -> dict[str, Any]:
    """
    Executa uma requisição GET com controle de intervalo e retries.

    A mensagem de erro não inclui a URL completa, evitando que chaves
    enviadas como query parameter apareçam nos logs.
    """

    retry_status_set = set(retry_statuses)
    headers = headers or {}

    for attempt in range(max_retries + 1):
        _wait_for_request_slot(
            source,
            minimum_interval_seconds,
        )

        response: requests.Response | None = None

        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            if attempt >= max_retries:
                raise ApiRequestError(
                    source=source,
                    status_code=None,
                    message=(
                        "falha de comunicação "
                        f"({exc.__class__.__name__})"
                    ),
                ) from exc

            time.sleep(_retry_delay(None, attempt))
            continue

        if 200 <= response.status_code < 300:
            try:
                payload = response.json()
            except ValueError as exc:
                raise ApiRequestError(
                    source=source,
                    status_code=response.status_code,
                    message="resposta JSON inválida",
                ) from exc

            if not isinstance(payload, dict):
                raise ApiRequestError(
                    source=source,
                    status_code=response.status_code,
                    message="a raiz da resposta não é um objeto JSON",
                )

            return payload

        if (
            response.status_code in retry_status_set
            and attempt < max_retries
        ):
            time.sleep(_retry_delay(response, attempt))
            continue

        response_text = re.sub(
            r"\s+",
            " ",
            response.text or "",
        ).strip()[:300]

        raise ApiRequestError(
            source=source,
            status_code=response.status_code,
            message=response_text or "resposta sem detalhes",
        )

    raise ApiRequestError(
        source=source,
        status_code=None,
        message="número máximo de tentativas excedido",
    )