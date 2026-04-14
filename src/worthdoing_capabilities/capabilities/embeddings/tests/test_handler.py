"""Tests for the embeddings capability handler."""

import pytest

from worthdoing_capabilities.capabilities.embeddings.handler import execute


@pytest.mark.asyncio
async def test_execute_returns_vector():
    result = await execute({"text": "hello world"})
    assert result["text"] == "hello world"
    assert result["model"] == "placeholder-v1"
    assert result["dimensions"] == 128
    assert isinstance(result["vector"], list)
    assert len(result["vector"]) == 128


@pytest.mark.asyncio
async def test_execute_vector_values_in_range():
    result = await execute({"text": "test embedding"})
    for val in result["vector"]:
        assert -1.0 <= val <= 1.0


@pytest.mark.asyncio
async def test_execute_deterministic():
    result1 = await execute({"text": "deterministic"})
    result2 = await execute({"text": "deterministic"})
    assert result1["vector"] == result2["vector"]


@pytest.mark.asyncio
async def test_execute_different_texts_produce_different_vectors():
    result1 = await execute({"text": "hello"})
    result2 = await execute({"text": "goodbye"})
    assert result1["vector"] != result2["vector"]
