"""Tests for the exa.answer capability handler."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.exa_answer.handler import execute

MOCK_RESPONSE = {
    "answer": "Python is a high-level programming language created by Guido van Rossum.",
    "citations": [
        {
            "title": "Python (programming language) - Wikipedia",
            "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "publishedDate": "2025-01-01",
            "text": "Python is a high-level, general-purpose programming language.",
        },
        {
            "title": "About Python - python.org",
            "url": "https://www.python.org/about/",
            "publishedDate": "2024-12-01",
            "text": "Python was created by Guido van Rossum.",
        },
    ],
}


def _build_mock_client(response_data):
    mock_response = MagicMock()
    mock_response.json.return_value = response_data
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = False
    return mock_client


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.exa_answer.handler.httpx.AsyncClient")
async def test_execute_returns_proper_structure(mock_client_cls):
    mock_client = _build_mock_client(MOCK_RESPONSE)
    mock_client_cls.return_value = mock_client

    result = await execute({"query": "What is Python?"})

    assert result["query"] == "What is Python?"
    assert "Python" in result["answer"]
    assert isinstance(result["citations"], list)
    assert len(result["citations"]) == 2

    first_citation = result["citations"][0]
    assert first_citation["title"] == "Python (programming language) - Wikipedia"
    assert first_citation["url"] == "https://en.wikipedia.org/wiki/Python_(programming_language)"
    assert first_citation["published_date"] == "2025-01-01"
    assert "high-level" in first_citation["text"]


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.exa_answer.handler.httpx.AsyncClient")
async def test_execute_sends_correct_payload(mock_client_cls):
    mock_client = _build_mock_client({"answer": "", "citations": []})
    mock_client_cls.return_value = mock_client

    await execute({"query": "test question"})

    call_kwargs = mock_client.post.call_args
    payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
    assert payload["query"] == "test question"
    assert payload["text"] is True

    url = call_kwargs.args[0] if call_kwargs.args else call_kwargs.kwargs.get("url", "")
    assert url == "https://api.exa.ai/answer"


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.exa_answer.handler.httpx.AsyncClient")
async def test_execute_handles_empty_answer(mock_client_cls):
    mock_client = _build_mock_client({"answer": "", "citations": []})
    mock_client_cls.return_value = mock_client

    result = await execute({"query": "unanswerable question"})

    assert result["answer"] == ""
    assert result["citations"] == []
    assert result["query"] == "unanswerable question"
