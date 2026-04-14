import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from worthdoing_capabilities.capabilities.tavily_search.handler import execute


@pytest.fixture
def mock_tavily_search_response():
    return {
        "query": "latest AI news",
        "answer": "Recent AI developments include...",
        "results": [
            {
                "title": "AI Breakthrough 2026",
                "url": "https://example.com/ai-news",
                "content": "A major AI breakthrough was announced today...",
                "score": 0.95,
            },
            {
                "title": "Machine Learning Trends",
                "url": "https://example.com/ml-trends",
                "content": "The latest trends in machine learning...",
                "score": 0.88,
            },
        ],
        "response_time": 1.23,
    }


@pytest.mark.asyncio
async def test_execute_basic_search(mock_tavily_search_response):
    mock_response = MagicMock()
    mock_response.json.return_value = mock_tavily_search_response
    mock_response.raise_for_status = MagicMock()

    with patch("worthdoing_capabilities.capabilities.tavily_search.handler.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch.dict("os.environ", {"TAVILY_API_KEY": "tvly-test-key"}):
            result = await execute({"query": "latest AI news"})

    assert result["query"] == "latest AI news"
    assert result["answer"] == "Recent AI developments include..."
    assert len(result["results"]) == 2
    assert result["results"][0]["title"] == "AI Breakthrough 2026"
    assert result["results"][0]["url"] == "https://example.com/ai-news"
    assert result["results"][0]["score"] == 0.95
    assert result["response_time"] == 1.23
    assert result["total"] == 2


@pytest.mark.asyncio
async def test_execute_with_optional_params(mock_tavily_search_response):
    mock_response = MagicMock()
    mock_response.json.return_value = mock_tavily_search_response
    mock_response.raise_for_status = MagicMock()

    with patch("worthdoing_capabilities.capabilities.tavily_search.handler.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch.dict("os.environ", {"TAVILY_API_KEY": "tvly-test-key"}):
            result = await execute({
                "query": "finance news",
                "search_depth": "advanced",
                "topic": "finance",
                "max_results": 10,
                "include_answer": True,
                "time_range": "week",
                "include_domains": ["reuters.com", "bloomberg.com"],
                "exclude_domains": ["example.com"],
            })

        call_args = mock_client.post.call_args
        payload = call_args.kwargs.get("json") or call_args[1].get("json")

        assert payload["query"] == "finance news"
        assert payload["search_depth"] == "advanced"
        assert payload["topic"] == "finance"
        assert payload["max_results"] == 10
        assert payload["include_answer"] is True
        assert payload["time_range"] == "week"
        assert payload["include_domains"] == ["reuters.com", "bloomberg.com"]
        assert payload["exclude_domains"] == ["example.com"]


@pytest.mark.asyncio
async def test_execute_default_params():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "query": "test",
        "results": [],
        "response_time": 0.5,
    }
    mock_response.raise_for_status = MagicMock()

    with patch("worthdoing_capabilities.capabilities.tavily_search.handler.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch.dict("os.environ", {"TAVILY_API_KEY": "tvly-test-key"}):
            result = await execute({"query": "test"})

        call_args = mock_client.post.call_args
        payload = call_args.kwargs.get("json") or call_args[1].get("json")

        assert payload["search_depth"] == "basic"
        assert payload["topic"] == "general"
        assert payload["max_results"] == 5
        assert payload["include_answer"] is True
        assert "time_range" not in payload
        assert "include_domains" not in payload
        assert "exclude_domains" not in payload

    assert result["total"] == 0
    assert result["results"] == []
    assert result["answer"] is None


@pytest.mark.asyncio
async def test_execute_sends_bearer_auth():
    mock_response = MagicMock()
    mock_response.json.return_value = {"query": "test", "results": [], "response_time": 0.1}
    mock_response.raise_for_status = MagicMock()

    with patch("worthdoing_capabilities.capabilities.tavily_search.handler.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch.dict("os.environ", {"TAVILY_API_KEY": "tvly-my-secret"}):
            await execute({"query": "test"})

        call_args = mock_client.post.call_args
        headers = call_args.kwargs.get("headers") or call_args[1].get("headers")
        assert headers["Authorization"] == "Bearer tvly-my-secret"
        assert headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_execute_raises_on_http_error():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized", request=MagicMock(), response=MagicMock()
    )

    with patch("worthdoing_capabilities.capabilities.tavily_search.handler.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch.dict("os.environ", {"TAVILY_API_KEY": "bad-key"}):
            with pytest.raises(httpx.HTTPStatusError):
                await execute({"query": "test"})


import httpx
