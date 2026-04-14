"""FMP real-time quote capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    api_key = os.environ.get("FMP_API_KEY", "")
    symbol = input_data["symbol"].upper()

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"https://financialmodelingprep.com/api/v3/quote/{symbol}",
            params={"apikey": api_key},
        )
        resp.raise_for_status()
        data = resp.json()

    if not data or isinstance(data, dict) and "Error Message" in data:
        raise ValueError(f"No data found for symbol: {symbol}")

    q = data[0]
    return {
        "symbol": q.get("symbol"),
        "name": q.get("name"),
        "price": q.get("price"),
        "change": q.get("change"),
        "change_percent": q.get("changesPercentage"),
        "volume": q.get("volume"),
        "market_cap": q.get("marketCap"),
        "pe": q.get("pe"),
        "eps": q.get("eps"),
        "day_high": q.get("dayHigh"),
        "day_low": q.get("dayLow"),
        "year_high": q.get("yearHigh"),
        "year_low": q.get("yearLow"),
        "open": q.get("open"),
        "previous_close": q.get("previousClose"),
        "exchange": q.get("exchange"),
        "timestamp": q.get("timestamp"),
    }
