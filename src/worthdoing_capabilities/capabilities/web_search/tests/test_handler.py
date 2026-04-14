"""Tests for the web_search capability handler."""

import pytest

from worthdoing_capabilities.capabilities.web_search.handler import execute


@pytest.mark.asyncio
async def test_execute_returns_results():
    result = await execute({"query": "python asyncio"})
    assert result["query"] == "python asyncio"
    assert isinstance(result["results"], list)
    assert len(result["results"]) >= 1
    assert result["total"] >= 1


@pytest.mark.asyncio
async def test_execute_result_structure():
    result = await execute({"query": "test", "max_results": 3})
    assert "query" in result
    assert "results" in result
    assert "total" in result
    first = result["results"][0]
    assert "title" in first
    assert "url" in first
    assert "snippet" in first
