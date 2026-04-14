"""Tests for the firecrawl_map capability handler."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from worthdoing_capabilities.capabilities.firecrawl_map.handler import execute


@pytest.mark.asyncio
async def test_execute_returns_links():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "links": [
            "https://example.com/",
            "https://example.com/about",
            "https://example.com/contact",
            "https://example.com/blog",
        ],
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "worthdoing_capabilities.capabilities.firecrawl_map.handler.httpx.AsyncClient",
        return_value=mock_client,
    ):
        result = await execute({"url": "https://example.com"})

    assert result["success"] is True
    assert isinstance(result["links"], list)
    assert len(result["links"]) == 4
    assert "https://example.com/about" in result["links"]


@pytest.mark.asyncio
async def test_execute_sends_correct_payload():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "links": []}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "worthdoing_capabilities.capabilities.firecrawl_map.handler.httpx.AsyncClient",
        return_value=mock_client,
    ):
        await execute({"url": "https://example.com", "limit": 50, "search": "blog"})

    call_args = mock_client.post.call_args
    payload = call_args[1]["json"]
    assert payload["url"] == "https://example.com"
    assert payload["limit"] == 50
    assert payload["search"] == "blog"


@pytest.mark.asyncio
async def test_execute_omits_search_when_not_provided():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "links": []}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "worthdoing_capabilities.capabilities.firecrawl_map.handler.httpx.AsyncClient",
        return_value=mock_client,
    ):
        await execute({"url": "https://example.com"})

    call_args = mock_client.post.call_args
    payload = call_args[1]["json"]
    assert "search" not in payload
    assert payload["limit"] == 100
