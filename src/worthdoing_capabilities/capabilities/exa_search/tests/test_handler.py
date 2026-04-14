"""Tests for the exa.search capability handler."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.exa_search.handler import execute

MOCK_RESPONSE = {
    "requestId": "req-abc123",
    "results": [
        {
            "title": "Example Result",
            "url": "https://example.com/article",
            "score": 0.95,
            "publishedDate": "2025-01-15",
            "text": "This is the extracted text content.",
            "highlights": ["extracted text"],
        },
        {
            "title": "Second Result",
            "url": "https://example.com/page2",
            "score": 0.88,
            "publishedDate": "2025-02-01",
            "text": "Another piece of content.",
            "highlights": [],
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
@patch("worthdoing_capabilities.capabilities.exa_search.handler.httpx.AsyncClient")
async def test_execute_returns_proper_structure(mock_client_cls):
    mock_client = _build_mock_client(MOCK_RESPONSE)
    mock_client_cls.return_value = mock_client

    result = await execute({"query": "machine learning"})

    assert result["query"] == "machine learning"
    assert isinstance(result["results"], list)
    assert len(result["results"]) == 2
    assert result["request_id"] == "req-abc123"
    assert result["total"] == 2

    first = result["results"][0]
    assert first["title"] == "Example Result"
    assert first["url"] == "https://example.com/article"
    assert first["score"] == 0.95
    assert first["published_date"] == "2025-01-15"
    assert first["text"] == "This is the extracted text content."
    assert first["highlights"] == ["extracted text"]


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.exa_search.handler.httpx.AsyncClient")
async def test_execute_sends_optional_params(mock_client_cls):
    mock_client = _build_mock_client({"requestId": "req-xyz", "results": []})
    mock_client_cls.return_value = mock_client

    result = await execute({
        "query": "AI news",
        "num_results": 5,
        "type": "neural",
        "category": "news",
        "include_domains": ["example.com"],
        "start_published_date": "2025-01-01",
    })

    assert result["query"] == "AI news"
    assert result["results"] == []
    assert result["total"] == 0

    call_kwargs = mock_client.post.call_args
    payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
    assert payload["numResults"] == 5
    assert payload["type"] == "neural"
    assert payload["category"] == "news"
    assert payload["includeDomains"] == ["example.com"]
    assert payload["startPublishedDate"] == "2025-01-01"


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.exa_search.handler.httpx.AsyncClient")
async def test_execute_handles_empty_results(mock_client_cls):
    mock_client = _build_mock_client({"requestId": "req-empty", "results": []})
    mock_client_cls.return_value = mock_client

    result = await execute({"query": "nonexistent topic xyz"})

    assert result["results"] == []
    assert result["total"] == 0
    assert result["request_id"] == "req-empty"
