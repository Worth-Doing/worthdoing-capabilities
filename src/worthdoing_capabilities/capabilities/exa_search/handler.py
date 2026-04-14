"""Exa search capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    """Search the web using the Exa API."""
    api_key = os.environ.get("EXA_API_KEY", "")
    query = input_data["query"]

    payload: dict = {
        "query": query,
        "numResults": input_data.get("num_results", 10),
        "type": input_data.get("type", "auto"),
        "contents": {
            "text": {"maxCharacters": 2000},
            "highlights": True,
        },
    }

    if "category" in input_data:
        payload["category"] = input_data["category"]
    if "include_domains" in input_data:
        payload["includeDomains"] = input_data["include_domains"]
    if "start_published_date" in input_data:
        payload["startPublishedDate"] = input_data["start_published_date"]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://api.exa.ai/search",
            json=payload,
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()

    return {
        "query": query,
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
