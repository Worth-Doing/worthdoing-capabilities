"""Tests for the eodhd_eod capability handler."""

from unittest.mock import MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.eodhd_eod.handler import execute


MOCK_EOD_RESPONSE = [
    {
        "date": "2023-11-17",
        "open": 189.89,
        "high": 190.67,
        "low": 188.90,
        "close": 189.69,
        "adjusted_close": 189.69,
        "volume": 50_000_000,
    },
    {
        "date": "2023-11-16",
        "open": 188.50,
        "high": 189.90,
        "low": 187.45,
        "close": 189.71,
        "adjusted_close": 189.71,
        "volume": 48_000_000,
    },
]


def _make_mock_response(json_data):
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


@pytest.mark.asyncio
async def test_execute_returns_eod_data():
    mock_response = _make_mock_response(MOCK_EOD_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await execute({"symbol": "AAPL.US"})

    assert result["symbol"] == "AAPL.US"
    assert isinstance(result["data"], list)
    assert len(result["data"]) == 2

    day = result["data"][0]
    assert day["date"] == "2023-11-17"
    assert day["open"] == 189.89
    assert day["high"] == 190.67
    assert day["low"] == 188.90
    assert day["close"] == 189.69
    assert day["adjusted_close"] == 189.69
    assert day["volume"] == 50_000_000


@pytest.mark.asyncio
async def test_execute_passes_date_params():
    mock_response = _make_mock_response(MOCK_EOD_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        await execute(
            {
                "symbol": "AAPL.US",
                "from_date": "2023-01-01",
                "to_date": "2023-12-31",
            }
        )

    call_params = mock_get.call_args[1]["params"]
    assert call_params["from"] == "2023-01-01"
    assert call_params["to"] == "2023-12-31"
    assert call_params["fmt"] == "json"


@pytest.mark.asyncio
async def test_execute_uses_correct_url():
    mock_response = _make_mock_response(MOCK_EOD_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        await execute({"symbol": "MSFT.US"})

    call_url = mock_get.call_args[0][0]
    assert call_url == "https://eodhd.com/api/eod/MSFT.US"


@pytest.mark.asyncio
async def test_execute_raises_on_empty_data():
    mock_response = _make_mock_response([])

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(ValueError, match="No EOD data found"):
            await execute({"symbol": "INVALID.US"})
