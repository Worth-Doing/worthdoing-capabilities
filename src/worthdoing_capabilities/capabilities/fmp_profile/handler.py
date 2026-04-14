"""FMP company profile capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    api_key = os.environ.get("FMP_API_KEY", "")
    symbol = input_data["symbol"].upper()

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"https://financialmodelingprep.com/api/v3/profile/{symbol}",
            params={"apikey": api_key},
        )
        resp.raise_for_status()
        data = resp.json()

    if not data or isinstance(data, dict) and "Error Message" in data:
        raise ValueError(f"No profile found for symbol: {symbol}")

    p = data[0]
    return {
        "symbol": p.get("symbol"),
        "company_name": p.get("companyName"),
        "description": p.get("description"),
        "sector": p.get("sector"),
        "industry": p.get("industry"),
        "ceo": p.get("ceo"),
        "website": p.get("website"),
        "country": p.get("country"),
        "employees": p.get("fullTimeEmployees"),
        "market_cap": p.get("mktCap"),
        "ipo_date": p.get("ipoDate"),
        "exchange": p.get("exchange"),
        "image": p.get("image"),
    }
