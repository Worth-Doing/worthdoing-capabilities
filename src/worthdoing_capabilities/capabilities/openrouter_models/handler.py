"""OpenRouter models listing capability handler."""

import httpx


async def execute(input_data: dict) -> dict:
    params = {}
    if "category" in input_data:
        params["category"] = input_data["category"]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://openrouter.ai/api/v1/models",
            params=params,
        )
        resp.raise_for_status()
        data = resp.json()

    models = data.get("data", [])

    # Filter by query if provided
    query = input_data.get("query", "").lower()
    if query:
        models = [
            m
            for m in models
            if query in m.get("id", "").lower()
            or query in m.get("name", "").lower()
            or query in (m.get("description") or "").lower()
        ]

    return {
        "models": [
            {
                "id": m.get("id", ""),
                "name": m.get("name", ""),
                "description": (m.get("description") or "")[:200],
                "context_length": m.get("context_length", 0),
                "pricing_prompt": m.get("pricing", {}).get("prompt", "0"),
                "pricing_completion": m.get("pricing", {}).get("completion", "0"),
                "input_modalities": m.get("architecture", {}).get(
                    "input_modalities", []
                ),
                "output_modalities": m.get("architecture", {}).get(
                    "output_modalities", []
                ),
            }
            for m in models
        ],
        "total": len(models),
    }
