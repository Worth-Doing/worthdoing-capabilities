"""URL fetch capability handler."""

import httpx


async def execute(input_data: dict) -> dict:
    url = input_data["url"]

    async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
        response = await client.get(url)

    content = response.text
    return {
        "url": str(response.url),
        "status_code": response.status_code,
        "content_type": response.headers.get("content-type", "unknown"),
        "content": content,
        "length": len(content),
    }
