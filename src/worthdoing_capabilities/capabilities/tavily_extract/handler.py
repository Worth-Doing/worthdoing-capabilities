import os

import httpx


async def execute(input_data: dict) -> dict:
    api_key = os.environ.get("TAVILY_API_KEY", "")

    payload = {
        "urls": input_data["urls"],
        "extract_depth": input_data.get("extract_depth", "basic"),
        "format": "markdown",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.tavily.com/extract",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    return {
        "results": [
            {
                "url": r.get("url", ""),
                "raw_content": r.get("raw_content", ""),
            }
            for r in data.get("results", [])
        ],
        "failed_results": [
            {
                "url": r.get("url", ""),
                "error": r.get("error", "Unknown error"),
            }
            for r in data.get("failed_results", [])
        ],
    }
