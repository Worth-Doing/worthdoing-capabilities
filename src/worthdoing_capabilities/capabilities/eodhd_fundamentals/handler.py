"""EODHD fundamentals capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    api_token = os.environ.get("EODHD_API_KEY", "")
    symbol = input_data["symbol"]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"https://eodhd.com/api/fundamentals/{symbol}",
            params={"api_token": api_token, "fmt": "json"},
        )
        resp.raise_for_status()
        data = resp.json()

    if not data or not isinstance(data, dict):
        raise ValueError(f"No fundamentals data found for symbol: {symbol}")

    return {
        "general": data.get("General", {}),
        "financials": data.get("Financials", {}),
        "highlights": data.get("Highlights", {}),
    }
