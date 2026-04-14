"""OpenAlex works search capability handler."""

import os

import httpx


def _reconstruct_abstract(inverted_index: dict | None) -> str | None:
    """Reconstruct abstract text from OpenAlex inverted index format."""
    if not inverted_index:
        return None
    positions = []
    for word, idxs in inverted_index.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)


async def execute(input_data: dict) -> dict:
    """Search scholarly works via the OpenAlex API."""
    api_key = os.environ.get("OPENALEX_API_KEY", "")

    # If DOI is provided, fetch single work
    doi = input_data.get("doi")
    if doi:
        # Normalize DOI
        doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"https://api.openalex.org/works/doi:{doi}",
                params={"api_key": api_key} if api_key else {},
            )
            resp.raise_for_status()
            work = resp.json()

        return {
            "works": [_format_work(work)],
            "total_count": 1,
            "page": 1,
            "per_page": 1,
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
    if "sort" in input_data:
        params["sort"] = input_data["sort"]

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            "https://api.openalex.org/works",
            params=params,
        )
        resp.raise_for_status()
        data = resp.json()

    meta = data.get("meta", {})
    results = data.get("results", [])

    return {
        "works": [_format_work(w) for w in results],
        "total_count": meta.get("count", 0),
        "page": meta.get("page", 1),
        "per_page": meta.get("per_page", 10),
    }


def _format_work(w: dict) -> dict:
    """Format a raw OpenAlex work object into a clean response dict."""
    # Extract authors
    authors = []
    for authorship in w.get("authorships", []):
        author = authorship.get("author", {})
        institutions = authorship.get("institutions", [])
        authors.append({
            "name": author.get("display_name", ""),
            "orcid": author.get("orcid"),
            "institution": institutions[0].get("display_name", "") if institutions else None,
        })

    # Get source name
    primary_loc = w.get("primary_location") or {}
    source = primary_loc.get("source") or {}

    # Get OA info
    oa = w.get("open_access", {})

    return {
        "id": w.get("id", ""),
        "doi": w.get("doi"),
        "title": w.get("title", w.get("display_name", "")),
        "publication_year": w.get("publication_year"),
        "publication_date": w.get("publication_date"),
        "type": w.get("type"),
        "authors": authors,
        "abstract": _reconstruct_abstract(w.get("abstract_inverted_index")),
        "cited_by_count": w.get("cited_by_count", 0),
        "is_oa": oa.get("is_oa", False),
        "oa_url": oa.get("oa_url"),
        "source_name": source.get("display_name"),
        "url": primary_loc.get("landing_page_url"),
    }
