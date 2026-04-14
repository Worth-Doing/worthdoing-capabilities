"""Firecrawl scrape capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    api_key = os.environ.get("FIRECRAWL_API_KEY", "")
    payload = {
        "url": input_data["url"],
        "formats": input_data.get("formats", ["markdown"]),
        "onlyMainContent": input_data.get("only_main_content", True),
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://api.firecrawl.dev/v2/scrape",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    result_data = data.get("data", {})
    return {
        "success": data.get("success", False),
        "markdown": result_data.get("markdown", ""),
        "html": result_data.get("html"),
        "links": result_data.get("links", []),
        "metadata": result_data.get("metadata", {}),
    }
