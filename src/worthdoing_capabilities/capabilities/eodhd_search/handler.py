"""EODHD ticker search capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    api_token = os.environ.get("EODHD_API_KEY", "")
    query = input_data["query"]

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"https://eodhd.com/api/search/{query}",
            params={"api_token": api_token, "fmt": "json"},
        )
        resp.raise_for_status()
        data = resp.json()

    if not isinstance(data, list):
        data = []

    results = [
        {
            "code": item.get("Code"),
            "exchange": item.get("Exchange"),
            "name": item.get("Name"),
            "type": item.get("Type"),
            "currency": item.get("Currency"),
        }
        for item in data
    ]

    return {"results": results}
