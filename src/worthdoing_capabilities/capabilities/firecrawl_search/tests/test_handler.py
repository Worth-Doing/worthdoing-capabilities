"""Tests for the firecrawl_search capability handler."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from worthdoing_capabilities.capabilities.firecrawl_search.handler import execute


@pytest.mark.asyncio
async def test_execute_returns_results():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": [
            {
                "title": "Python Tutorial",
                "url": "https://example.com/python",
                "markdown": "# Python\nLearn Python.",
                "description": "A comprehensive Python tutorial.",
            },
            {
                "title": "Python Docs",
                "url": "https://docs.python.org",
                "markdown": "# Python Docs\nOfficial docs.",
                "description": "Official Python documentation.",
            },
        ],
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "worthdoing_capabilities.capabilities.firecrawl_search.handler.httpx.AsyncClient",
        return_value=mock_client,
    ):
        result = await execute({"query": "python tutorial"})

    assert result["success"] is True
    assert isinstance(result["results"], list)
    assert len(result["results"]) == 2
    assert result["results"][0]["title"] == "Python Tutorial"
    assert result["results"][0]["url"] == "https://example.com/python"
    assert result["results"][0]["markdown"] == "# Python\nLearn Python."
    assert result["results"][0]["description"] == "A comprehensive Python tutorial."


@pytest.mark.asyncio
async def test_execute_sends_correct_payload():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "data": []}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "worthdoing_capabilities.capabilities.firecrawl_search.handler.httpx.AsyncClient",
        return_value=mock_client,
    ):
        await execute({"query": "test query", "limit": 10, "country": "us"})

    call_args = mock_client.post.call_args
    payload = call_args[1]["json"]
    assert payload["query"] == "test query"
    assert payload["limit"] == 10
    assert payload["country"] == "us"
    assert payload["scrapeOptions"] == {"formats": ["markdown"]}


@pytest.mark.asyncio
async def test_execute_omits_country_when_not_provided():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "data": []}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "worthdoing_capabilities.capabilities.firecrawl_search.handler.httpx.AsyncClient",
        return_value=mock_client,
    ):
        await execute({"query": "test"})

    call_args = mock_client.post.call_args
    payload = call_args[1]["json"]
    assert "country" not in payload
    assert payload["limit"] == 5
