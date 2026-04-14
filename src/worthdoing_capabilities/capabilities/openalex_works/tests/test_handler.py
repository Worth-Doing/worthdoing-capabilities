"""Tests for the openalex.works capability handler."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.openalex_works.handler import (
    _reconstruct_abstract,
    execute,
)

MOCK_WORK = {
    "id": "https://openalex.org/W2741809807",
    "doi": "https://doi.org/10.1038/s41586-020-2649-2",
    "title": "A Study on Machine Learning",
    "display_name": "A Study on Machine Learning",
    "publication_year": 2020,
    "publication_date": "2020-08-26",
    "type": "article",
    "authorships": [
        {
            "author": {
                "display_name": "Jane Smith",
                "orcid": "https://orcid.org/0000-0001-2345-6789",
            },
            "institutions": [
                {"display_name": "MIT"},
            ],
        },
        {
            "author": {
                "display_name": "John Doe",
                "orcid": None,
            },
            "institutions": [],
        },
    ],
    "abstract_inverted_index": {
        "This": [0],
        "is": [1],
        "a": [2],
        "test": [3],
        "abstract.": [4],
    },
    "cited_by_count": 150,
    "open_access": {
        "is_oa": True,
        "oa_url": "https://example.com/paper.pdf",
    },
    "primary_location": {
        "source": {"display_name": "Nature"},
        "landing_page_url": "https://nature.com/articles/s41586-020-2649-2",
    },
}

MOCK_SEARCH_RESPONSE = {
    "meta": {
        "count": 42,
        "page": 1,
        "per_page": 10,
    },
    "results": [MOCK_WORK],
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


def test_reconstruct_abstract_basic():
    inverted_index = {
        "Hello": [0],
        "world": [1],
        "of": [2],
        "science": [3],
    }
    result = _reconstruct_abstract(inverted_index)
    assert result == "Hello world of science"


def test_reconstruct_abstract_with_repeated_words():
    inverted_index = {
        "the": [0, 3],
        "cat": [1],
        "and": [2],
        "dog": [4],
    }
    result = _reconstruct_abstract(inverted_index)
    assert result == "the cat and the dog"


def test_reconstruct_abstract_none():
    assert _reconstruct_abstract(None) is None


def test_reconstruct_abstract_empty():
    assert _reconstruct_abstract({}) is None


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openalex_works.handler.httpx.AsyncClient")
async def test_search_returns_formatted_works(mock_client_cls):
    mock_client = _build_mock_client(MOCK_SEARCH_RESPONSE)
    mock_client_cls.return_value = mock_client

    result = await execute({"search": "machine learning"})

    assert result["total_count"] == 42
    assert result["page"] == 1
    assert result["per_page"] == 10
    assert len(result["works"]) == 1

    work = result["works"][0]
    assert work["id"] == "https://openalex.org/W2741809807"
    assert work["doi"] == "https://doi.org/10.1038/s41586-020-2649-2"
    assert work["title"] == "A Study on Machine Learning"
    assert work["publication_year"] == 2020
    assert work["cited_by_count"] == 150
    assert work["is_oa"] is True
    assert work["source_name"] == "Nature"
    assert work["abstract"] == "This is a test abstract."
    assert len(work["authors"]) == 2
    assert work["authors"][0]["name"] == "Jane Smith"
    assert work["authors"][0]["institution"] == "MIT"
    assert work["authors"][1]["institution"] is None


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openalex_works.handler.httpx.AsyncClient")
async def test_doi_lookup(mock_client_cls):
    mock_client = _build_mock_client(MOCK_WORK)
    mock_client_cls.return_value = mock_client

    result = await execute({"doi": "https://doi.org/10.1038/s41586-020-2649-2"})

    assert result["total_count"] == 1
    assert result["page"] == 1
    assert len(result["works"]) == 1
    assert result["works"][0]["title"] == "A Study on Machine Learning"

    # Verify the DOI was normalized in the URL
    call_args = mock_client.get.call_args
    url = call_args[0][0]
    assert url == "https://api.openalex.org/works/doi:10.1038/s41586-020-2649-2"


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openalex_works.handler.httpx.AsyncClient")
async def test_search_with_filter_and_sort(mock_client_cls):
    mock_client = _build_mock_client({"meta": {"count": 0, "page": 1, "per_page": 5}, "results": []})
    mock_client_cls.return_value = mock_client

    result = await execute({
        "search": "climate change",
        "filter": "publication_year:2024,is_oa:true",
        "sort": "cited_by_count:desc",
        "per_page": 5,
        "page": 2,
    })

    assert result["total_count"] == 0
    assert result["works"] == []

    call_kwargs = mock_client.get.call_args
    params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
    assert params["search"] == "climate change"
    assert params["filter"] == "publication_year:2024,is_oa:true"
    assert params["sort"] == "cited_by_count:desc"
    assert params["per_page"] == 5
    assert params["page"] == 2


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openalex_works.handler.httpx.AsyncClient")
async def test_work_without_optional_fields(mock_client_cls):
    minimal_work = {
        "id": "https://openalex.org/W123",
        "title": "Minimal Work",
        "authorships": [],
        "cited_by_count": 0,
    }
    mock_client = _build_mock_client({
        "meta": {"count": 1, "page": 1, "per_page": 10},
        "results": [minimal_work],
    })
    mock_client_cls.return_value = mock_client

    result = await execute({"search": "test"})

    work = result["works"][0]
    assert work["title"] == "Minimal Work"
    assert work["authors"] == []
    assert work["abstract"] is None
    assert work["doi"] is None
    assert work["is_oa"] is False
    assert work["source_name"] is None
