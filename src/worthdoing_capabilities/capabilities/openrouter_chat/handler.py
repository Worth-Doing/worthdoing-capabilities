"""OpenRouter chat completion capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")

    payload = {
        "model": input_data["model"],
        "messages": input_data["messages"],
    }

    # Optional parameters
    for key in [
        "max_tokens",
        "temperature",
        "top_p",
        "stop",
        "tools",
        "tool_choice",
        "response_format",
        "seed",
    ]:
        if key in input_data:
            payload[key] = input_data[key]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://worthdoing.ai",
        "X-OpenRouter-Title": "WorthDoing Capabilities",
    }

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()

    if "error" in data:
        raise RuntimeError(
            f"OpenRouter error: {data['error'].get('message', 'Unknown error')}"
        )

    choice = data["choices"][0]
    message = choice["message"]
    usage = data.get("usage", {})

    result = {
        "id": data.get("id", ""),
        "model": data.get("model", input_data["model"]),
        "content": message.get("content", ""),
        "finish_reason": choice.get("finish_reason", ""),
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "cost": usage.get("cost"),
        },
    }

    if message.get("tool_calls"):
        result["tool_calls"] = [
            {
                "id": tc.get("id", ""),
                "function_name": tc.get("function", {}).get("name", ""),
                "arguments": tc.get("function", {}).get("arguments", ""),
            }
            for tc in message["tool_calls"]
        ]

    return result
