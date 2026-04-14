"""Exa contents capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    """Retrieve full page contents for a list of URLs using the Exa API."""
    api_key = os.environ.get("EXA_API_KEY", "")
    urls = input_data["urls"]

    payload: dict = {
        "urls": urls,
        "text": True,
        "highlights": True,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            "https://api.exa.ai/contents",
            json=payload,
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()

    return {
        "results": [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "text": r.get("text", ""),
                "highlights": r.get("highlights", []),
                "published_date": r.get("publishedDate"),
            }
            for r in data.get("results", [])
        ],
        "total": len(data.get("results", [])),
    }
