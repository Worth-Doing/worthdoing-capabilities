"""Exa answer capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    """Get a direct AI-generated answer with citations using the Exa API."""
    api_key = os.environ.get("EXA_API_KEY", "")
    query = input_data["query"]

    payload: dict = {
        "query": query,
        "text": True,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.exa.ai/answer",
            json=payload,
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()

    citations = [
        {
            "title": c.get("title", ""),
            "url": c.get("url", ""),
            "published_date": c.get("publishedDate"),
            "text": c.get("text", ""),
        }
        for c in data.get("citations", [])
    ]

    return {
        "query": query,
        "answer": data.get("answer", ""),
        "citations": citations,
    }
