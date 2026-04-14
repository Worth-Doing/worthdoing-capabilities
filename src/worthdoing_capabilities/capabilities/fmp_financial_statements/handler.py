"""FMP financial statements capability handler."""

import os

import httpx

STATEMENT_TYPE_MAP = {
    "income": "income-statement",
    "balance_sheet": "balance-sheet-statement",
    "cash_flow": "cash-flow-statement",
}


async def execute(input_data: dict) -> dict:
    api_key = os.environ.get("FMP_API_KEY", "")
    symbol = input_data["symbol"].upper()
    statement_type = input_data["statement_type"]
    period = input_data.get("period", "annual")
    limit = input_data.get("limit", 5)

    if statement_type not in STATEMENT_TYPE_MAP:
        raise ValueError(
            f"Invalid statement_type: {statement_type}. "
            f"Must be one of: {', '.join(STATEMENT_TYPE_MAP.keys())}"
        )

    endpoint = STATEMENT_TYPE_MAP[statement_type]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"https://financialmodelingprep.com/api/v3/{endpoint}/{symbol}",
            params={"apikey": api_key, "period": period, "limit": limit},
        )
        resp.raise_for_status()
        data = resp.json()

    if not data or isinstance(data, dict) and "Error Message" in data:
        raise ValueError(
            f"No {statement_type} data found for symbol: {symbol}"
        )

    return {
        "symbol": symbol,
        "statement_type": statement_type,
        "period": period,
        "data": data,
    }
