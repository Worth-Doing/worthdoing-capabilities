"""FMP historical prices capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    api_key = os.environ.get("FMP_API_KEY", "")
    symbol = input_data["symbol"].upper()

    params: dict = {"apikey": api_key}
    if "from_date" in input_data:
        params["from"] = input_data["from_date"]
    if "to_date" in input_data:
        params["to"] = input_data["to_date"]
    if "timeseries" in input_data:
        params["timeseries"] = input_data["timeseries"]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}",
            params=params,
        )
        resp.raise_for_status()
        data = resp.json()

    if not data or "historical" not in data:
        raise ValueError(f"No historical data found for symbol: {symbol}")

    historical = [
        {
            "date": day.get("date"),
            "open": day.get("open"),
            "high": day.get("high"),
            "low": day.get("low"),
            "close": day.get("close"),
            "volume": day.get("volume"),
            "change_percent": day.get("changePercent"),
        }
        for day in data["historical"]
    ]

    return {
        "symbol": data.get("symbol", symbol),
        "historical": historical,
    }
