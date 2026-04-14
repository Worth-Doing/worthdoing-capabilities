import os

import httpx


async def execute(input_data: dict) -> dict:
    api_key = os.environ.get("TAVILY_API_KEY", "")

    payload = {
        "query": input_data["query"],
        "search_depth": input_data.get("search_depth", "basic"),
        "topic": input_data.get("topic", "general"),
        "max_results": input_data.get("max_results", 5),
        "include_answer": input_data.get("include_answer", True),
    }

    if "time_range" in input_data:
        payload["time_range"] = input_data["time_range"]
    if "include_domains" in input_data:
        payload["include_domains"] = input_data["include_domains"]
    if "exclude_domains" in input_data:
        payload["exclude_domains"] = input_data["exclude_domains"]

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            "https://api.tavily.com/search",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    return {
        "query": data.get("query", input_data["query"]),
        "answer": data.get("answer"),
        "results": [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
                "score": r.get("score"),
            }
            for r in data.get("results", [])
        ],
        "response_time": data.get("response_time"),
        "total": len(data.get("results", [])),
    }
