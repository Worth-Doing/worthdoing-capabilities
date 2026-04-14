"""Tests for the openalex.authors capability handler."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.openalex_authors.handler import execute

MOCK_AUTHOR = {
    "id": "https://openalex.org/A1234567890",
    "display_name": "Jane Smith",
    "orcid": "https://orcid.org/0000-0001-2345-6789",
    "works_count": 85,
    "cited_by_count": 4200,
    "summary_stats": {
        "h_index": 32,
        "i10_index": 55,
    },
    "last_known_institution": {
        "display_name": "MIT",
    },
    "topics": [
        {"display_name": "Machine Learning"},
        {"display_name": "Natural Language Processing"},
        {"display_name": "Computer Vision"},
        {"display_name": "Deep Learning"},
        {"display_name": "Reinforcement Learning"},
        {"display_name": "Robotics"},
    ],
}

MOCK_SEARCH_RESPONSE = {
    "meta": {
        "count": 15,
        "page": 1,
        "per_page": 10,
    },
    "results": [MOCK_AUTHOR],
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
@patch("worthdoing_capabilities.capabilities.openalex_authors.handler.httpx.AsyncClient")
async def test_search_returns_formatted_authors(mock_client_cls):
    mock_client = _build_mock_client(MOCK_SEARCH_RESPONSE)
    mock_client_cls.return_value = mock_client

    result = await execute({"search": "Jane Smith"})

    assert result["total_count"] == 15
    assert len(result["authors"]) == 1

    author = result["authors"][0]
    assert author["id"] == "https://openalex.org/A1234567890"
    assert author["display_name"] == "Jane Smith"
    assert author["orcid"] == "https://orcid.org/0000-0001-2345-6789"
    assert author["works_count"] == 85
    assert author["cited_by_count"] == 4200
    assert author["h_index"] == 32
    assert author["i10_index"] == 55
    assert author["last_institution"] == "MIT"
    assert len(author["topics"]) == 5
    assert author["topics"][0] == "Machine Learning"
    assert "Robotics" not in author["topics"]  # Only top 5


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openalex_authors.handler.httpx.AsyncClient")
async def test_orcid_lookup(mock_client_cls):
    mock_client = _build_mock_client(MOCK_AUTHOR)
    mock_client_cls.return_value = mock_client

    result = await execute({"orcid": "https://orcid.org/0000-0001-2345-6789"})

    assert result["total_count"] == 1
    assert len(result["authors"]) == 1
    assert result["authors"][0]["display_name"] == "Jane Smith"

    # Verify the ORCID was normalized in the URL
    call_args = mock_client.get.call_args
    url = call_args[0][0]
    assert url == "https://api.openalex.org/authors/orcid:0000-0001-2345-6789"


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openalex_authors.handler.httpx.AsyncClient")
async def test_search_with_filter(mock_client_cls):
    mock_client = _build_mock_client({"meta": {"count": 0, "page": 1, "per_page": 10}, "results": []})
    mock_client_cls.return_value = mock_client

    result = await execute({
        "search": "deep learning",
        "filter": "has_orcid:true",
        "per_page": 5,
        "page": 2,
    })

    assert result["total_count"] == 0
    assert result["authors"] == []

    call_kwargs = mock_client.get.call_args
    params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
    assert params["search"] == "deep learning"
    assert params["filter"] == "has_orcid:true"
    assert params["per_page"] == 5
    assert params["page"] == 2


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openalex_authors.handler.httpx.AsyncClient")
async def test_author_without_optional_fields(mock_client_cls):
    minimal_author = {
        "id": "https://openalex.org/A999",
        "display_name": "Unknown Researcher",
        "works_count": 1,
        "cited_by_count": 0,
    }
    mock_client = _build_mock_client({
        "meta": {"count": 1, "page": 1, "per_page": 10},
        "results": [minimal_author],
    })
    mock_client_cls.return_value = mock_client

    result = await execute({"search": "unknown"})

    author = result["authors"][0]
    assert author["display_name"] == "Unknown Researcher"
    assert author["orcid"] is None
    assert author["h_index"] == 0
    assert author["i10_index"] == 0
    assert author["last_institution"] is None
    assert author["topics"] == []
