"""OpenAlex authors search capability handler."""

import os

import httpx


async def execute(input_data: dict) -> dict:
    """Search academic authors via the OpenAlex API."""
    api_key = os.environ.get("OPENALEX_API_KEY", "")

    # If ORCID is provided, fetch single author
    orcid = input_data.get("orcid")
    if orcid:
        # Normalize ORCID (remove URL prefix if present)
        orcid = (
            orcid.replace("https://orcid.org/", "")
            .replace("http://orcid.org/", "")
        )
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"https://api.openalex.org/authors/orcid:{orcid}",
                params={"api_key": api_key} if api_key else {},
            )
            resp.raise_for_status()
            author = resp.json()

        return {
            "authors": [_format_author(author)],
            "total_count": 1,
        }

    # Otherwise, search/filter
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
            "https://api.openalex.org/authors",
            params=params,
        )
        resp.raise_for_status()
        data = resp.json()

    meta = data.get("meta", {})
    results = data.get("results", [])

    return {
        "authors": [_format_author(a) for a in results],
        "total_count": meta.get("count", 0),
    }


def _format_author(a: dict) -> dict:
    """Format a raw OpenAlex author object into a clean response dict."""
    # Get summary stats
    summary = a.get("summary_stats", {})

    # Get last known institution
    last_institution = a.get("last_known_institution") or {}
    last_inst_name = last_institution.get("display_name")

    # Get top topics (up to 5)
    topics_raw = a.get("topics", [])
    topics = [
        t.get("display_name", "")
        for t in topics_raw[:5]
        if t.get("display_name")
    ]

    return {
        "id": a.get("id", ""),
        "display_name": a.get("display_name", ""),
        "orcid": a.get("orcid"),
        "works_count": a.get("works_count", 0),
        "cited_by_count": a.get("cited_by_count", 0),
        "h_index": summary.get("h_index", 0),
        "i10_index": summary.get("i10_index", 0),
        "last_institution": last_inst_name,
        "topics": topics,
    }
