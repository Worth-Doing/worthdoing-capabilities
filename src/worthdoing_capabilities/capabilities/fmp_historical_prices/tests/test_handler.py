"""Tests for the fmp_historical_prices capability handler."""

from unittest.mock import MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.fmp_historical_prices.handler import execute


MOCK_HISTORICAL_RESPONSE = {
    "symbol": "AAPL",
    "historical": [
        {
            "date": "2023-11-17",
            "open": 189.89,
            "high": 190.67,
            "low": 188.90,
            "close": 189.69,
            "volume": 50_000_000,
            "changePercent": 0.45,
        },
        {
            "date": "2023-11-16",
            "open": 188.50,
            "high": 189.90,
            "low": 187.45,
            "close": 189.71,
            "volume": 48_000_000,
            "changePercent": 0.64,
        },
    ],
}


def _make_mock_response(json_data):
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


@pytest.mark.asyncio
async def test_execute_returns_historical_data():
    mock_response = _make_mock_response(MOCK_HISTORICAL_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await execute({"symbol": "AAPL"})

    assert result["symbol"] == "AAPL"
    assert isinstance(result["historical"], list)
    assert len(result["historical"]) == 2

    day = result["historical"][0]
    assert day["date"] == "2023-11-17"
    assert day["open"] == 189.89
    assert day["high"] == 190.67
    assert day["low"] == 188.90
    assert day["close"] == 189.69
    assert day["volume"] == 50_000_000
    assert day["change_percent"] == 0.45


@pytest.mark.asyncio
async def test_execute_passes_date_params():
    mock_response = _make_mock_response(MOCK_HISTORICAL_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        await execute(
            {
                "symbol": "AAPL",
                "from_date": "2023-01-01",
                "to_date": "2023-12-31",
            }
        )

    call_params = mock_get.call_args[1]["params"]
    assert call_params["from"] == "2023-01-01"
    assert call_params["to"] == "2023-12-31"


@pytest.mark.asyncio
async def test_execute_passes_timeseries_param():
    mock_response = _make_mock_response(MOCK_HISTORICAL_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        await execute({"symbol": "AAPL", "timeseries": 30})

    call_params = mock_get.call_args[1]["params"]
    assert call_params["timeseries"] == 30


@pytest.mark.asyncio
async def test_execute_raises_on_no_historical_key():
    mock_response = _make_mock_response({})

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(ValueError, match="No historical data found"):
            await execute({"symbol": "INVALID"})


@pytest.mark.asyncio
async def test_execute_normalizes_symbol():
    mock_response = _make_mock_response(MOCK_HISTORICAL_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        await execute({"symbol": "aapl"})

    call_url = mock_get.call_args[0][0]
    assert "AAPL" in call_url
