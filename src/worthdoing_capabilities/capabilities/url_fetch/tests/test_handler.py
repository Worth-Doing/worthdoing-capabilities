"""Tests for the url_fetch capability handler."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from worthdoing_capabilities.capabilities.url_fetch.handler import execute


@pytest.mark.asyncio
async def test_execute_returns_expected_fields():
    mock_response = MagicMock()
    mock_response.url = "https://example.com"
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/html; charset=utf-8"}
    mock_response.text = "<html><body>Hello</body></html>"

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("worthdoing_capabilities.capabilities.url_fetch.handler.httpx.AsyncClient", return_value=mock_client):
        result = await execute({"url": "https://example.com"})

    assert result["url"] == "https://example.com"
    assert result["status_code"] == 200
    assert "text/html" in result["content_type"]
    assert "Hello" in result["content"]
    assert result["length"] > 0
