"""Tests for the eodhd_search capability handler."""

from unittest.mock import MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.eodhd_search.handler import execute


MOCK_SEARCH_RESPONSE = [
    {
        "Code": "AAPL",
        "Exchange": "US",
        "Name": "Apple Inc",
        "Type": "Common Stock",
        "Currency": "USD",
    },
    {
        "Code": "AAPL",
        "Exchange": "NEO",
        "Name": "Apple Inc",
        "Type": "Common Stock",
        "Currency": "CAD",
    },
]


def _make_mock_response(json_data):
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


@pytest.mark.asyncio
async def test_execute_returns_search_results():
    mock_response = _make_mock_response(MOCK_SEARCH_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await execute({"query": "Apple"})

    assert "results" in result
    assert isinstance(result["results"], list)
    assert len(result["results"]) == 2

    first = result["results"][0]
    assert first["code"] == "AAPL"
    assert first["exchange"] == "US"
    assert first["name"] == "Apple Inc"
    assert first["type"] == "Common Stock"
    assert first["currency"] == "USD"


@pytest.mark.asyncio
async def test_execute_uses_correct_url():
    mock_response = _make_mock_response(MOCK_SEARCH_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        await execute({"query": "Microsoft"})

    call_url = mock_get.call_args[0][0]
    assert call_url == "https://eodhd.com/api/search/Microsoft"
    call_params = mock_get.call_args[1]["params"]
    assert call_params["fmt"] == "json"


@pytest.mark.asyncio
async def test_execute_returns_empty_on_no_results():
    mock_response = _make_mock_response([])

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await execute({"query": "xyznonexistent"})

    assert result["results"] == []


@pytest.mark.asyncio
async def test_execute_handles_non_list_response():
    mock_response = _make_mock_response({"error": "something went wrong"})

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await execute({"query": "test"})

    assert result["results"] == []
