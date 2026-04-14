"""Tests for the fmp_quote capability handler."""

from unittest.mock import MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.fmp_quote.handler import execute


MOCK_QUOTE_RESPONSE = [
    {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "price": 178.72,
        "change": 2.15,
        "changesPercentage": 1.22,
        "volume": 55_000_000,
        "marketCap": 2_800_000_000_000,
        "pe": 29.5,
        "eps": 6.05,
        "dayHigh": 179.50,
        "dayLow": 176.30,
        "yearHigh": 199.62,
        "yearLow": 124.17,
        "open": 176.80,
        "previousClose": 176.57,
        "exchange": "NASDAQ",
        "timestamp": 1700000000,
    }
]


def _make_mock_response(json_data):
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


@pytest.mark.asyncio
async def test_execute_returns_quote():
    mock_response = _make_mock_response(MOCK_QUOTE_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await execute({"symbol": "AAPL"})

    assert result["symbol"] == "AAPL"
    assert result["name"] == "Apple Inc."
    assert result["price"] == 178.72
    assert result["change"] == 2.15
    assert result["change_percent"] == 1.22
    assert result["volume"] == 55_000_000
    assert result["market_cap"] == 2_800_000_000_000
    assert result["pe"] == 29.5
    assert result["eps"] == 6.05
    assert result["day_high"] == 179.50
    assert result["day_low"] == 176.30
    assert result["year_high"] == 199.62
    assert result["year_low"] == 124.17
    assert result["open"] == 176.80
    assert result["previous_close"] == 176.57
    assert result["exchange"] == "NASDAQ"
    assert result["timestamp"] == 1700000000


@pytest.mark.asyncio
async def test_execute_normalizes_symbol():
    mock_response = _make_mock_response([{"symbol": "MSFT"}])

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        await execute({"symbol": "msft"})

    call_args = mock_get.call_args
    assert "MSFT" in call_args[0][0]


@pytest.mark.asyncio
async def test_execute_raises_on_empty_data():
    mock_response = _make_mock_response([])

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(ValueError, match="No data found"):
            await execute({"symbol": "INVALID"})


@pytest.mark.asyncio
async def test_execute_raises_on_error_message():
    mock_response = _make_mock_response({"Error Message": "Invalid API KEY."})

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(ValueError, match="No data found"):
            await execute({"symbol": "AAPL"})
