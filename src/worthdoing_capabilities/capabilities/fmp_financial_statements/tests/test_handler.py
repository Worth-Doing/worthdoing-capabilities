"""Tests for the fmp_financial_statements capability handler."""

from unittest.mock import MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.fmp_financial_statements.handler import (
    execute,
)


MOCK_INCOME_RESPONSE = [
    {
        "date": "2023-09-30",
        "symbol": "AAPL",
        "revenue": 383_285_000_000,
        "netIncome": 96_995_000_000,
        "grossProfit": 169_148_000_000,
        "period": "FY",
    },
    {
        "date": "2022-09-24",
        "symbol": "AAPL",
        "revenue": 394_328_000_000,
        "netIncome": 99_803_000_000,
        "grossProfit": 170_782_000_000,
        "period": "FY",
    },
]


def _make_mock_response(json_data):
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


@pytest.mark.asyncio
async def test_execute_returns_income_statement():
    mock_response = _make_mock_response(MOCK_INCOME_RESPONSE)

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await execute(
            {"symbol": "AAPL", "statement_type": "income"}
        )

    assert result["symbol"] == "AAPL"
    assert result["statement_type"] == "income"
    assert result["period"] == "annual"
    assert isinstance(result["data"], list)
    assert len(result["data"]) == 2


@pytest.mark.asyncio
async def test_execute_maps_statement_type_to_url():
    test_cases = {
        "income": "income-statement",
        "balance_sheet": "balance-sheet-statement",
        "cash_flow": "cash-flow-statement",
    }

    for stmt_type, expected_path in test_cases.items():
        mock_response = _make_mock_response([{"symbol": "AAPL"}])

        with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
            await execute({"symbol": "AAPL", "statement_type": stmt_type})

        call_url = mock_get.call_args[0][0]
        assert expected_path in call_url, (
            f"Expected '{expected_path}' in URL for statement_type '{stmt_type}'"
        )


@pytest.mark.asyncio
async def test_execute_passes_period_and_limit():
    mock_response = _make_mock_response([{"symbol": "AAPL"}])

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        await execute(
            {
                "symbol": "AAPL",
                "statement_type": "income",
                "period": "quarter",
                "limit": 10,
            }
        )

    call_params = mock_get.call_args[1]["params"]
    assert call_params["period"] == "quarter"
    assert call_params["limit"] == 10


@pytest.mark.asyncio
async def test_execute_raises_on_invalid_statement_type():
    with pytest.raises(ValueError, match="Invalid statement_type"):
        await execute({"symbol": "AAPL", "statement_type": "invalid"})


@pytest.mark.asyncio
async def test_execute_raises_on_empty_data():
    mock_response = _make_mock_response([])

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(ValueError, match="No income data found"):
            await execute({"symbol": "INVALID", "statement_type": "income"})
