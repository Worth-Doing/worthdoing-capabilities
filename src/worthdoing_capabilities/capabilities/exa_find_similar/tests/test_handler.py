"""Tests for the exa.find_similar capability handler."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.exa_find_similar.handler import execute

MOCK_RESPONSE = {
    "requestId": "req-sim-001",
    "results": [
        {
            "title": "Similar Page One",
            "url": "https://similar.com/page1",
            "score": 0.92,
            "publishedDate": "2025-03-10",
            "text": "Content of a similar page.",
            "highlights": ["similar page"],
        },
    ],
}


def _build_mock_client(response_data):
    mock_response = MagicMock()
    mock_response.json.return_value = response_data
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = False
    return mock_client


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.exa_find_similar.handler.httpx.AsyncClient")
async def test_execute_returns_proper_structure(mock_client_cls):
    mock_client = _build_mock_client(MOCK_RESPONSE)
    mock_client_cls.return_value = mock_client

    result = await execute({"url": "https://example.com/article"})

    assert result["url"] == "https://example.com/article"
    assert isinstance(result["results"], list)
    assert len(result["results"]) == 1
    assert result["request_id"] == "req-sim-001"
    assert result["total"] == 1

    first = result["results"][0]
    assert first["title"] == "Similar Page One"
    assert first["url"] == "https://similar.com/page1"
    assert first["score"] == 0.92


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.exa_find_similar.handler.httpx.AsyncClient")
async def test_execute_with_exclude_source_domain(mock_client_cls):
    mock_client = _build_mock_client({"requestId": "req-sim-002", "results": []})
    mock_client_cls.return_value = mock_client

    result = await execute({
        "url": "https://example.com/page",
        "num_results": 5,
        "exclude_source_domain": True,
    })

    assert result["results"] == []
    assert result["total"] == 0

    call_kwargs = mock_client.post.call_args
    payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
    assert payload["excludeSourceDomain"] is True
    assert payload["numResults"] == 5


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.exa_find_similar.handler.httpx.AsyncClient")
async def test_execute_handles_empty_results(mock_client_cls):
    mock_client = _build_mock_client({"requestId": "req-sim-empty", "results": []})
    mock_client_cls.return_value = mock_client

    result = await execute({"url": "https://obscure-site.example.org"})

    assert result["results"] == []
    assert result["total"] == 0
    assert result["request_id"] == "req-sim-empty"
