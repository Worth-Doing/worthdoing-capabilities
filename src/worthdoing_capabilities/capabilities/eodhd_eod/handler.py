"""EODHD end-of-day historical prices capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    api_token = os.environ.get("EODHD_API_KEY", "")
    symbol = input_data["symbol"]

    params: dict = {"api_token": api_token, "fmt": "json"}
    if "from_date" in input_data:
        params["from"] = input_data["from_date"]
    if "to_date" in input_data:
        params["to"] = input_data["to_date"]

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"https://eodhd.com/api/eod/{symbol}",
            params=params,
        )
        resp.raise_for_status()
        data = resp.json()

    if not data or isinstance(data, dict) and "error" in data:
        raise ValueError(f"No EOD data found for symbol: {symbol}")

    records = [
        {
            "date": record.get("date"),
            "open": record.get("open"),
            "high": record.get("high"),
            "low": record.get("low"),
            "close": record.get("close"),
            "adjusted_close": record.get("adjusted_close"),
            "volume": record.get("volume"),
        }
        for record in data
    ]

    return {
        "symbol": symbol,
        "data": records,
    }
