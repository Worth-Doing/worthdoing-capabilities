"""Tests for the firecrawl_scrape capability handler."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


from worthdoing_capabilities.capabilities.firecrawl_scrape.handler import execute


@pytest.mark.asyncio
async def test_execute_returns_expected_fields():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": {
            "markdown": "# Hello World\nSome content here.",
            "html": "<h1>Hello World</h1><p>Some content here.</p>",
            "links": ["https://example.com/page1", "https://example.com/page2"],
            "metadata": {"title": "Hello World", "language": "en"},
        },
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "worthdoing_capabilities.capabilities.firecrawl_scrape.handler.httpx.AsyncClient",
        return_value=mock_client,
    ):
        result = await execute({"url": "https://example.com"})

    assert result["success"] is True
    assert result["markdown"] == "# Hello World\nSome content here."
    assert result["html"] == "<h1>Hello World</h1><p>Some content here.</p>"
    assert isinstance(result["links"], list)
    assert len(result["links"]) == 2
    assert result["metadata"]["title"] == "Hello World"


@pytest.mark.asyncio
async def test_execute_sends_correct_payload():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "data": {}}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "worthdoing_capabilities.capabilities.firecrawl_scrape.handler.httpx.AsyncClient",
        return_value=mock_client,
    ):
        await execute({
            "url": "https://example.com",
            "formats": ["markdown", "html"],
            "only_main_content": False,
        })

    call_args = mock_client.post.call_args
    assert call_args[1]["json"]["url"] == "https://example.com"
    assert call_args[1]["json"]["formats"] == ["markdown", "html"]
    assert call_args[1]["json"]["onlyMainContent"] is False


@pytest.mark.asyncio
async def test_execute_uses_default_formats():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "data": {}}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "worthdoing_capabilities.capabilities.firecrawl_scrape.handler.httpx.AsyncClient",
        return_value=mock_client,
    ):
        await execute({"url": "https://example.com"})

    call_args = mock_client.post.call_args
    assert call_args[1]["json"]["formats"] == ["markdown"]
    assert call_args[1]["json"]["onlyMainContent"] is True
