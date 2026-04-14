"""Tests for the fmp_profile capability handler."""

from unittest.mock import MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.fmp_profile.handler import execute


MOCK_PROFILE_RESPONSE = [
    {
        "symbol": "AAPL",
        "companyName": "Apple Inc.",
        "description": "Apple Inc. designs, manufactures, and markets smartphones.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "ceo": "Mr. Timothy D. Cook",
        "website": "https://www.apple.com",
        "country": "US",
        "fullTimeEmployees": 164000,
        "mktCap": 2_800_000_000_000,
        "ipoDate": "1980-12-12",
        "exchange": "NASDAQ",
        "image": "https://financialmodelingprep.com/image-stock/AAPL.png",
    }
]


def _make_mock_response(json_data):
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


@pytest.mark.asyncio
async def test_execute_returns_profile():
    mock_response = _make_mock_response(MOCK_PROFILE_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await execute({"symbol": "AAPL"})

    assert result["symbol"] == "AAPL"
    assert result["company_name"] == "Apple Inc."
    assert result["description"].startswith("Apple Inc.")
    assert result["sector"] == "Technology"
    assert result["industry"] == "Consumer Electronics"
    assert result["ceo"] == "Mr. Timothy D. Cook"
    assert result["website"] == "https://www.apple.com"
    assert result["country"] == "US"
    assert result["employees"] == 164000
    assert result["market_cap"] == 2_800_000_000_000
    assert result["ipo_date"] == "1980-12-12"
    assert result["exchange"] == "NASDAQ"
    assert result["image"].endswith(".png")


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
        with pytest.raises(ValueError, match="No profile found"):
            await execute({"symbol": "INVALID"})
