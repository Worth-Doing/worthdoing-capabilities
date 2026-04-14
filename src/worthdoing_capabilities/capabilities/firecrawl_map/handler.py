"""Firecrawl map capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    api_key = os.environ.get("FIRECRAWL_API_KEY", "")
    payload: dict = {
        "url": input_data["url"],
        "limit": input_data.get("limit", 100),
    }

    search = input_data.get("search")
    if search:
        payload["search"] = search

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://api.firecrawl.dev/v2/map",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    return {
        "success": data.get("success", False),
        "links": data.get("links", []),
    }
