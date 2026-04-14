"""HTTP executor for WorthDoing capability contracts."""

from __future__ import annotations

import re
from typing import Any

import httpx

from worthdoing_capabilities.executors.base import BaseExecutor


def _template(value: Any, input_data: dict) -> Any:
    """Replace ``{{ input.xxx }}`` placeholders in strings with input_data values.

    Recursively processes strings, lists, and dicts. Non-string values are
    returned unchanged.
    """
    if isinstance(value, str):
        def _replacer(match: re.Match) -> str:
            key = match.group(1).strip()
            if key.startswith("input."):
                field = key[len("input."):]
                resolved = input_data.get(field, match.group(0))
                return str(resolved)
            return match.group(0)

        return re.sub(r"\{\{\s*(.+?)\s*\}\}", _replacer, value)

    if isinstance(value, dict):
        return {k: _template(v, input_data) for k, v in value.items()}

    if isinstance(value, list):
        return [_template(item, input_data) for item in value]

    return value


class HttpExecutor(BaseExecutor):
    """Executor that makes async HTTP requests using httpx."""

    @property
    def executor_type(self) -> str:
        return "http"

    async def execute(
        self, config: dict, input_data: dict, auth_headers: dict
    ) -> dict:
        """Execute an HTTP request based on the capability configuration.

        Reads ``method``, ``url``, ``query``, ``headers``, and ``body`` from
        *config*, templates any ``{{ input.xxx }}`` placeholders with
        *input_data* values, and performs an async HTTP request.

        Args:
            config: Execution configuration containing HTTP details.
            input_data: Validated input data for placeholder substitution.
            auth_headers: Resolved authentication headers to merge in.

        Returns:
            The parsed JSON response body as a dict.

        Raises:
            httpx.HTTPStatusError: If the response indicates an HTTP error.
            RuntimeError: If the request fails for a network-level reason.
        """
        method: str = config.get("method", "GET").upper()
        url: str = _template(config.get("url", ""), input_data)
        query: dict | None = _template(config.get("query"), input_data)
        body: Any = _template(config.get("body"), input_data)

        # Merge headers: config headers < auth headers
        headers: dict[str, str] = {}
        if config.get("headers"):
            headers.update(_template(config["headers"], input_data))
        headers.update(auth_headers)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=query,
                    headers=headers,
                    json=body if body and method in ("POST", "PUT", "PATCH") else None,
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"HTTP {exc.response.status_code} error from {url}: "
                f"{exc.response.text[:500]}"
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(
                f"HTTP request failed for {url}: {exc}"
            ) from exc
