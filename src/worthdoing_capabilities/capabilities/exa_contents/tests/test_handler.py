"""Tests for the exa.contents capability handler."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.exa_contents.handler import execute

MOCK_RESPONSE = {
    "results": [
        {
            "title": "Example Article",
            "url": "https://example.com/article",
            "text": "Full text content of the article goes here.",
            "highlights": ["Full text content"],
            "publishedDate": "2025-04-01",
        },
        {
            "title": "Another Page",
            "url": "https://example.com/page2",
            "text": "Second page content.",
            "highlights": [],
            "publishedDate": "2025-03-15",
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
@patch("worthdoing_capabilities.capabilities.exa_contents.handler.httpx.AsyncClient")
async def test_execute_returns_proper_structure(mock_client_cls):
    mock_client = _build_mock_client(MOCK_RESPONSE)
    mock_client_cls.return_value = mock_client

    result = await execute({
        "urls": ["https://example.com/article", "https://example.com/page2"]
    })

    assert isinstance(result["results"], list)
    assert len(result["results"]) == 2
    assert result["total"] == 2

    first = result["results"][0]
    assert first["title"] == "Example Article"
    assert first["url"] == "https://example.com/article"
    assert first["text"] == "Full text content of the article goes here."
    assert first["highlights"] == ["Full text content"]
    assert first["published_date"] == "2025-04-01"


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.exa_contents.handler.httpx.AsyncClient")
async def test_execute_sends_top_level_content_options(mock_client_cls):
    mock_client = _build_mock_client({"results": []})
    mock_client_cls.return_value = mock_client

    await execute({"urls": ["https://example.com"]})

    call_kwargs = mock_client.post.call_args
    payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
    assert payload["text"] is True
    assert payload["highlights"] is True
    assert payload["urls"] == ["https://example.com"]


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.exa_contents.handler.httpx.AsyncClient")
async def test_execute_handles_empty_results(mock_client_cls):
    mock_client = _build_mock_client({"results": []})
    mock_client_cls.return_value = mock_client

    result = await execute({"urls": []})

    assert result["results"] == []
    assert result["total"] == 0
