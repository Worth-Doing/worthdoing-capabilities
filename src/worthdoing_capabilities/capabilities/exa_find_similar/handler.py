"""Exa find-similar capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    """Find web pages similar to a given URL using the Exa API."""
    api_key = os.environ.get("EXA_API_KEY", "")
    url = input_data["url"]

    payload: dict = {
        "url": url,
        "numResults": input_data.get("num_results", 10),
        "contents": {
            "text": {"maxCharacters": 2000},
            "highlights": True,
        },
    }

    if "exclude_source_domain" in input_data:
        payload["excludeSourceDomain"] = input_data["exclude_source_domain"]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://api.exa.ai/findSimilar",
            json=payload,
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()

    return {
        "url": url,
        "results": [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "score": r.get("score"),
                "published_date": r.get("publishedDate"),
                "text": r.get("text", ""),
                "highlights": r.get("highlights", []),
            }
            for r in data.get("results", [])
        ],
        "request_id": data.get("requestId", ""),
        "total": len(data.get("results", [])),
    }
