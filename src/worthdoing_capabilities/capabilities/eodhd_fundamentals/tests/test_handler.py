"""Tests for the eodhd_fundamentals capability handler."""

from unittest.mock import MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.eodhd_fundamentals.handler import execute


MOCK_FUNDAMENTALS_RESPONSE = {
    "General": {
        "Code": "AAPL",
        "Name": "Apple Inc",
        "Sector": "Technology",
        "Industry": "Consumer Electronics",
        "Country": "US",
    },
    "Financials": {
        "Income_Statement": {
            "yearly": {
                "2023-09-30": {
                    "totalRevenue": 383_285_000_000,
                    "netIncome": 96_995_000_000,
                }
            }
        },
        "Balance_Sheet": {},
        "Cash_Flow": {},
    },
    "Highlights": {
        "MarketCapitalization": 2_800_000_000_000,
        "PERatio": 29.5,
        "EarningsShare": 6.05,
        "DividendYield": 0.0055,
    },
}


def _make_mock_response(json_data):
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


@pytest.mark.asyncio
async def test_execute_returns_fundamentals():
    mock_response = _make_mock_response(MOCK_FUNDAMENTALS_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await execute({"symbol": "AAPL.US"})

    assert "general" in result
    assert "financials" in result
    assert "highlights" in result

    assert result["general"]["Code"] == "AAPL"
    assert result["general"]["Sector"] == "Technology"
    assert result["highlights"]["MarketCapitalization"] == 2_800_000_000_000
    assert result["highlights"]["PERatio"] == 29.5


@pytest.mark.asyncio
async def test_execute_uses_correct_url():
    mock_response = _make_mock_response(MOCK_FUNDAMENTALS_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        await execute({"symbol": "MSFT.US"})

    call_url = mock_get.call_args[0][0]
    assert call_url == "https://eodhd.com/api/fundamentals/MSFT.US"
    call_params = mock_get.call_args[1]["params"]
    assert call_params["fmt"] == "json"


@pytest.mark.asyncio
async def test_execute_returns_empty_sections_gracefully():
    mock_response = _make_mock_response({"General": {"Code": "TEST"}})

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await execute({"symbol": "TEST.US"})

    assert result["general"] == {"Code": "TEST"}
    assert result["financials"] == {}
    assert result["highlights"] == {}


@pytest.mark.asyncio
async def test_execute_raises_on_empty_data():
    mock_response = _make_mock_response({})

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(ValueError, match="No fundamentals data found"):
            await execute({"symbol": "INVALID.US"})
