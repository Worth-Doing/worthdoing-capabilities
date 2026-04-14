"""Tests for the openrouter.chat capability handler."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from worthdoing_capabilities.capabilities.openrouter_chat.handler import execute

MOCK_CHAT_RESPONSE = {
    "id": "gen-abc123",
    "model": "openai/gpt-4",
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you today?",
            },
            "finish_reason": "stop",
        }
    ],
    "usage": {
        "prompt_tokens": 12,
        "completion_tokens": 8,
        "total_tokens": 20,
        "cost": 0.0012,
    },
}

MOCK_TOOL_CALLS_RESPONSE = {
    "id": "gen-tool456",
    "model": "openai/gpt-4",
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_001",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": '{"city": "Paris"}',
                        },
                    }
                ],
            },
            "finish_reason": "tool_calls",
        }
    ],
    "usage": {
        "prompt_tokens": 20,
        "completion_tokens": 15,
        "total_tokens": 35,
    },
}


def _build_mock_client(response_data, method="post"):
    mock_response = MagicMock()
    mock_response.json.return_value = response_data
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    setattr(mock_client, method, AsyncMock(return_value=mock_response))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openrouter_chat.handler.httpx.AsyncClient")
async def test_execute_returns_proper_structure(mock_client_cls):
    """Test that a basic chat completion returns the expected output structure."""
    mock_client = _build_mock_client(MOCK_CHAT_RESPONSE)
    mock_client_cls.return_value = mock_client

    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-or-test-key"}):
        result = await execute({
            "model": "openai/gpt-4",
            "messages": [{"role": "user", "content": "Hello"}],
        })

    assert result["id"] == "gen-abc123"
    assert result["model"] == "openai/gpt-4"
    assert result["content"] == "Hello! How can I help you today?"
    assert result["finish_reason"] == "stop"
    assert result["usage"]["prompt_tokens"] == 12
    assert result["usage"]["completion_tokens"] == 8
    assert result["usage"]["total_tokens"] == 20
    assert result["usage"]["cost"] == 0.0012
    assert "tool_calls" not in result


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openrouter_chat.handler.httpx.AsyncClient")
async def test_execute_sends_correct_payload_and_headers(mock_client_cls):
    """Test that the handler sends the right payload, headers, and optional params."""
    mock_client = _build_mock_client(MOCK_CHAT_RESPONSE)
    mock_client_cls.return_value = mock_client

    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-or-secret"}):
        await execute({
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 256,
            "temperature": 0.7,
            "top_p": 0.9,
        })

    call_args = mock_client.post.call_args
    payload = call_args.kwargs.get("json") or call_args[1].get("json")
    headers = call_args.kwargs.get("headers") or call_args[1].get("headers")

    # Verify payload
    assert payload["model"] == "anthropic/claude-3.5-sonnet"
    assert payload["messages"] == [{"role": "user", "content": "Hi"}]
    assert payload["max_tokens"] == 256
    assert payload["temperature"] == 0.7
    assert payload["top_p"] == 0.9

    # Verify headers
    assert headers["Authorization"] == "Bearer sk-or-secret"
    assert headers["Content-Type"] == "application/json"
    assert headers["HTTP-Referer"] == "https://worthdoing.ai"
    assert headers["X-OpenRouter-Title"] == "WorthDoing Capabilities"

    # Verify URL
    url = call_args.args[0] if call_args.args else call_args.kwargs.get("url", "")
    assert url == "https://openrouter.ai/api/v1/chat/completions"


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openrouter_chat.handler.httpx.AsyncClient")
async def test_execute_handles_tool_calls(mock_client_cls):
    """Test that tool_calls in the response are correctly mapped."""
    mock_client = _build_mock_client(MOCK_TOOL_CALLS_RESPONSE)
    mock_client_cls.return_value = mock_client

    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-or-test"}):
        result = await execute({
            "model": "openai/gpt-4",
            "messages": [{"role": "user", "content": "What is the weather in Paris?"}],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}},
                    },
                }
            ],
        })

    assert result["finish_reason"] == "tool_calls"
    assert "tool_calls" in result
    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["id"] == "call_001"
    assert result["tool_calls"][0]["function_name"] == "get_weather"
    assert result["tool_calls"][0]["arguments"] == '{"city": "Paris"}'


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openrouter_chat.handler.httpx.AsyncClient")
async def test_execute_raises_on_api_error(mock_client_cls):
    """Test that an OpenRouter error in the response body raises RuntimeError."""
    error_response = {
        "error": {
            "message": "Model not found",
            "code": 404,
        }
    }
    # The error response still has choices absent, so we need the handler
    # to check for errors before accessing choices.
    mock_client = _build_mock_client(error_response)
    mock_client_cls.return_value = mock_client

    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-or-test"}):
        with pytest.raises(RuntimeError, match="Model not found"):
            await execute({
                "model": "nonexistent/model",
                "messages": [{"role": "user", "content": "test"}],
            })


@pytest.mark.asyncio
@patch("worthdoing_capabilities.capabilities.openrouter_chat.handler.httpx.AsyncClient")
async def test_execute_omits_unset_optional_params(mock_client_cls):
    """Test that optional parameters not provided are not sent in the payload."""
    mock_client = _build_mock_client(MOCK_CHAT_RESPONSE)
    mock_client_cls.return_value = mock_client

    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-or-test"}):
        await execute({
            "model": "openai/gpt-4",
            "messages": [{"role": "user", "content": "Hi"}],
        })

    call_args = mock_client.post.call_args
    payload = call_args.kwargs.get("json") or call_args[1].get("json")

    assert "max_tokens" not in payload
    assert "temperature" not in payload
    assert "top_p" not in payload
    assert "tools" not in payload
    assert "response_format" not in payload
    assert "seed" not in payload
    assert payload["model"] == "openai/gpt-4"
    assert payload["messages"] == [{"role": "user", "content": "Hi"}]
