"""Tests for the openalex.institutions capability handler."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.openalex_institutions.handler import execute

MOCK_INSTITUTION = {
    "id": "https://openalex.org/I27837315",
    "display_name": "Massachusetts Institute of Technology",
    "ror": "https://ror.org/042nb2s44",
    "country_code": "US",
    "type": "education",
    "homepage_url": "http://web.mit.edu/",
    "works_count": 250000,
    "cited_by_count": 15000000,
    "summary_stats": {
        "h_index": 950,
    },
}

MOCK_SEARCH_RESPONSE = {
    "meta": {
        "count": 5,
        "page": 1,
        "per_page": 10,
    },
    "results": [MOCK_INSTITUTION],
}


def _build_mock_client(response_data):
    mock_response = MagicMock()
    mock_response.json.return_value = response_data
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = False
    return mock_client


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openalex_institutions.handler.httpx.AsyncClient")
async def test_search_returns_formatted_institutions(mock_client_cls):
    mock_client = _build_mock_client(MOCK_SEARCH_RESPONSE)
    mock_client_cls.return_value = mock_client

    result = await execute({"search": "MIT"})

    assert result["total_count"] == 5
    assert len(result["institutions"]) == 1

    inst = result["institutions"][0]
    assert inst["id"] == "https://openalex.org/I27837315"
    assert inst["display_name"] == "Massachusetts Institute of Technology"
    assert inst["ror"] == "https://ror.org/042nb2s44"
    assert inst["country_code"] == "US"
    assert inst["type"] == "education"
    assert inst["homepage_url"] == "http://web.mit.edu/"
    assert inst["works_count"] == 250000
    assert inst["cited_by_count"] == 15000000
    assert inst["h_index"] == 950


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openalex_institutions.handler.httpx.AsyncClient")
async def test_search_with_filter(mock_client_cls):
    mock_client = _build_mock_client({"meta": {"count": 0, "page": 1, "per_page": 10}, "results": []})
    mock_client_cls.return_value = mock_client

    result = await execute({
        "search": "university",
        "filter": "country_code:US,type:education",
        "per_page": 20,
        "page": 3,
    })

    assert result["total_count"] == 0
    assert result["institutions"] == []

    call_kwargs = mock_client.get.call_args
    params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
    assert params["search"] == "university"
    assert params["filter"] == "country_code:US,type:education"
    assert params["per_page"] == 20
    assert params["page"] == 3


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openalex_institutions.handler.httpx.AsyncClient")
async def test_search_hits_correct_endpoint(mock_client_cls):
    mock_client = _build_mock_client({"meta": {"count": 1, "page": 1, "per_page": 10}, "results": [MOCK_INSTITUTION]})
    mock_client_cls.return_value = mock_client

    await execute({"search": "Harvard"})

    call_args = mock_client.get.call_args
    url = call_args[0][0]
    assert url == "https://api.openalex.org/institutions"


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openalex_institutions.handler.httpx.AsyncClient")
async def test_institution_without_optional_fields(mock_client_cls):
    minimal_inst = {
        "id": "https://openalex.org/I999",
        "display_name": "Unknown University",
        "works_count": 10,
        "cited_by_count": 50,
    }
    mock_client = _build_mock_client({
        "meta": {"count": 1, "page": 1, "per_page": 10},
        "results": [minimal_inst],
    })
    mock_client_cls.return_value = mock_client

    result = await execute({"search": "unknown"})

    inst = result["institutions"][0]
    assert inst["display_name"] == "Unknown University"
    assert inst["ror"] is None
    assert inst["country_code"] is None
    assert inst["type"] is None
    assert inst["homepage_url"] is None
    assert inst["h_index"] == 0
