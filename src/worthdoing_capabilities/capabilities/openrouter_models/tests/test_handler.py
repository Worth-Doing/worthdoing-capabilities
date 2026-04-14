"""Tests for the openrouter.models capability handler."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.openrouter_models.handler import execute

MOCK_MODELS_RESPONSE = {
    "data": [
        {
            "id": "openai/gpt-4",
            "name": "GPT-4",
            "description": "OpenAI's most capable model for complex tasks.",
            "context_length": 8192,
            "pricing": {
                "prompt": "0.00003",
                "completion": "0.00006",
            },
            "architecture": {
                "input_modalities": ["text"],
                "output_modalities": ["text"],
            },
        },
        {
            "id": "anthropic/claude-3.5-sonnet",
            "name": "Claude 3.5 Sonnet",
            "description": "Anthropic's balanced model for intelligence and speed.",
            "context_length": 200000,
            "pricing": {
                "prompt": "0.000003",
                "completion": "0.000015",
            },
            "architecture": {
                "input_modalities": ["text", "image"],
                "output_modalities": ["text"],
            },
        },
        {
            "id": "meta-llama/llama-3-70b",
            "name": "Llama 3 70B",
            "description": "Meta's open-source large language model.",
            "context_length": 8192,
            "pricing": {
                "prompt": "0.0000008",
                "completion": "0.0000008",
            },
            "architecture": {
                "input_modalities": ["text"],
                "output_modalities": ["text"],
            },
        },
    ]
}


def _build_mock_client(response_data):
    mock_response = MagicMock()
    mock_response.json.return_value = response_data
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openrouter_models.handler.httpx.AsyncClient")
async def test_execute_returns_all_models(mock_client_cls):
    """Test that all models are returned when no filter is applied."""
    mock_client = _build_mock_client(MOCK_MODELS_RESPONSE)
    mock_client_cls.return_value = mock_client

    result = await execute({})

    assert result["total"] == 3
    assert len(result["models"]) == 3

    gpt4 = result["models"][0]
    assert gpt4["id"] == "openai/gpt-4"
    assert gpt4["name"] == "GPT-4"
    assert gpt4["context_length"] == 8192
    assert gpt4["pricing_prompt"] == "0.00003"
    assert gpt4["pricing_completion"] == "0.00006"
    assert gpt4["input_modalities"] == ["text"]
    assert gpt4["output_modalities"] == ["text"]

    claude = result["models"][1]
    assert claude["id"] == "anthropic/claude-3.5-sonnet"
    assert claude["input_modalities"] == ["text", "image"]


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openrouter_models.handler.httpx.AsyncClient")
async def test_execute_filters_by_query(mock_client_cls):
    """Test that the query parameter correctly filters models by name, id, or description."""
    mock_client = _build_mock_client(MOCK_MODELS_RESPONSE)
    mock_client_cls.return_value = mock_client

    # Filter by "claude" - should match anthropic/claude-3.5-sonnet
    result = await execute({"query": "claude"})

    assert result["total"] == 1
    assert result["models"][0]["id"] == "anthropic/claude-3.5-sonnet"
    assert result["models"][0]["name"] == "Claude 3.5 Sonnet"


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openrouter_models.handler.httpx.AsyncClient")
async def test_execute_filters_by_query_description(mock_client_cls):
    """Test that query filtering also matches against model descriptions."""
    mock_client = _build_mock_client(MOCK_MODELS_RESPONSE)
    mock_client_cls.return_value = mock_client

    # "open-source" appears in the Llama description
    result = await execute({"query": "open-source"})

    assert result["total"] == 1
    assert result["models"][0]["id"] == "meta-llama/llama-3-70b"


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openrouter_models.handler.httpx.AsyncClient")
async def test_execute_passes_category_param(mock_client_cls):
    """Test that the category parameter is forwarded as a query param to the API."""
    mock_client = _build_mock_client({"data": []})
    mock_client_cls.return_value = mock_client

    result = await execute({"category": "programming"})

    call_args = mock_client.get.call_args
    params = call_args.kwargs.get("params") or call_args[1].get("params")
    assert params["category"] == "programming"
    assert result["total"] == 0
    assert result["models"] == []


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openrouter_models.handler.httpx.AsyncClient")
async def test_execute_handles_empty_response(mock_client_cls):
    """Test that an empty model list is handled gracefully."""
    mock_client = _build_mock_client({"data": []})
    mock_client_cls.return_value = mock_client

    result = await execute({})

    assert result["total"] == 0
    assert result["models"] == []


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openrouter_models.handler.httpx.AsyncClient")
async def test_execute_truncates_long_descriptions(mock_client_cls):
    """Test that model descriptions are truncated to 200 characters."""
    long_desc = "A" * 500
    mock_client = _build_mock_client({
        "data": [
            {
                "id": "test/model",
                "name": "Test Model",
                "description": long_desc,
                "context_length": 4096,
                "pricing": {"prompt": "0.001", "completion": "0.002"},
                "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]},
            }
        ]
    })
    mock_client_cls.return_value = mock_client

    result = await execute({})

    assert len(result["models"][0]["description"]) == 200
    assert result["models"][0]["description"] == "A" * 200
