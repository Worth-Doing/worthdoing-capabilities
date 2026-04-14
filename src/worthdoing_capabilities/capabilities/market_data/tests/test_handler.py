"""Tests for the market_data capability handler."""

import pytest

from worthdoing_capabilities.capabilities.market_data.handler import execute


@pytest.mark.asyncio
async def test_execute_returns_quote():
    result = await execute({"symbol": "AAPL"})
    assert result["symbol"] == "AAPL"
    assert isinstance(result["price"], (int, float))
    assert result["currency"] == "USD"
    assert "change" in result
    assert "change_percent" in result
    assert "volume" in result
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_execute_normalizes_symbol():
    result = await execute({"symbol": "msft"})
    assert result["symbol"] == "MSFT"
