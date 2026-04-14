"""OpenAlex institutions search capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    """Search academic institutions via the OpenAlex API."""
    api_key = os.environ.get("OPENALEX_API_KEY", "")

    params: dict = {
        "per_page": input_data.get("per_page", 10),
        "page": input_data.get("page", 1),
    }
    if api_key:
        params["api_key"] = api_key
    if "search" in input_data:
        params["search"] = input_data["search"]
    if "filter" in input_data:
        params["filter"] = input_data["filter"]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://api.openalex.org/institutions",
            params=params,
        )
        resp.raise_for_status()
        data = resp.json()

    meta = data.get("meta", {})
    results = data.get("results", [])

    return {
        "institutions": [_format_institution(inst) for inst in results],
        "total_count": meta.get("count", 0),
    }


def _format_institution(inst: dict) -> dict:
    """Format a raw OpenAlex institution object into a clean response dict."""
    # Get summary stats
    summary = inst.get("summary_stats", {})

    return {
        "id": inst.get("id", ""),
        "display_name": inst.get("display_name", ""),
        "ror": inst.get("ror"),
        "country_code": inst.get("country_code"),
        "type": inst.get("type"),
        "homepage_url": inst.get("homepage_url"),
        "works_count": inst.get("works_count", 0),
        "cited_by_count": inst.get("cited_by_count", 0),
        "h_index": summary.get("h_index", 0),
    }
