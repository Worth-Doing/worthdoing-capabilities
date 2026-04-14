"""Firecrawl search capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    api_key = os.environ.get("FIRECRAWL_API_KEY", "")
    payload: dict = {
        "query": input_data["query"],
        "limit": input_data.get("limit", 5),
        "scrapeOptions": {
            "formats": ["markdown"],
        },
    }

    country = input_data.get("country")
    if country:
        payload["country"] = country

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://api.firecrawl.dev/v2/search",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    raw_results = data.get("data", [])
    results = [
        {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "markdown": item.get("markdown", ""),
            "description": item.get("description", ""),
        }
        for item in raw_results
    ]

    return {
        "success": data.get("success", False),
        "results": results,
    }
