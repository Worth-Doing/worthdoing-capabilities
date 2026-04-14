import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from worthdoing_capabilities.capabilities.tavily_extract.handler import execute


@pytest.fixture
def mock_tavily_extract_response():
    return {
        "results": [
            {
                "url": "https://example.com/article",
                "raw_content": "# Article Title\n\nThis is the article content in markdown.",
            },
            {
                "url": "https://example.com/docs",
                "raw_content": "# Documentation\n\nAPI reference and guides.",
            },
        ],
        "failed_results": [],
    }


@pytest.fixture
def mock_tavily_extract_partial_failure():
    return {
        "results": [
            {
                "url": "https://example.com/article",
                "raw_content": "# Article Content",
            },
        ],
        "failed_results": [
            {
                "url": "https://example.com/broken",
                "error": "Failed to fetch URL",
            },
        ],
    }


@pytest.mark.asyncio
async def test_execute_basic_extract(mock_tavily_extract_response):
    mock_response = MagicMock()
    mock_response.json.return_value = mock_tavily_extract_response
    mock_response.raise_for_status = MagicMock()

    with patch("worthdoing_capabilities.capabilities.tavily_extract.handler.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch.dict("os.environ", {"TAVILY_API_KEY": "tvly-test-key"}):
            result = await execute({
                "urls": ["https://example.com/article", "https://example.com/docs"]
            })

    assert len(result["results"]) == 2
    assert result["results"][0]["url"] == "https://example.com/article"
    assert "Article Title" in result["results"][0]["raw_content"]
    assert result["results"][1]["url"] == "https://example.com/docs"
    assert len(result["failed_results"]) == 0


@pytest.mark.asyncio
async def test_execute_with_extract_depth(mock_tavily_extract_response):
    mock_response = MagicMock()
    mock_response.json.return_value = mock_tavily_extract_response
    mock_response.raise_for_status = MagicMock()

    with patch("worthdoing_capabilities.capabilities.tavily_extract.handler.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch.dict("os.environ", {"TAVILY_API_KEY": "tvly-test-key"}):
            await execute({
                "urls": ["https://example.com/article"],
                "extract_depth": "advanced",
            })

        call_args = mock_client.post.call_args
        payload = call_args.kwargs.get("json") or call_args[1].get("json")

        assert payload["urls"] == ["https://example.com/article"]
        assert payload["extract_depth"] == "advanced"
        assert payload["format"] == "markdown"


@pytest.mark.asyncio
async def test_execute_default_extract_depth():
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": [], "failed_results": []}
    mock_response.raise_for_status = MagicMock()

    with patch("worthdoing_capabilities.capabilities.tavily_extract.handler.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch.dict("os.environ", {"TAVILY_API_KEY": "tvly-test-key"}):
            await execute({"urls": ["https://example.com"]})

        call_args = mock_client.post.call_args
        payload = call_args.kwargs.get("json") or call_args[1].get("json")

        assert payload["extract_depth"] == "basic"


@pytest.mark.asyncio
async def test_execute_partial_failure(mock_tavily_extract_partial_failure):
    mock_response = MagicMock()
    mock_response.json.return_value = mock_tavily_extract_partial_failure
    mock_response.raise_for_status = MagicMock()

    with patch("worthdoing_capabilities.capabilities.tavily_extract.handler.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch.dict("os.environ", {"TAVILY_API_KEY": "tvly-test-key"}):
            result = await execute({
                "urls": ["https://example.com/article", "https://example.com/broken"]
            })

    assert len(result["results"]) == 1
    assert result["results"][0]["url"] == "https://example.com/article"
    assert len(result["failed_results"]) == 1
    assert result["failed_results"][0]["url"] == "https://example.com/broken"
    assert result["failed_results"][0]["error"] == "Failed to fetch URL"


@pytest.mark.asyncio
async def test_execute_sends_bearer_auth():
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": [], "failed_results": []}
    mock_response.raise_for_status = MagicMock()

    with patch("worthdoing_capabilities.capabilities.tavily_extract.handler.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch.dict("os.environ", {"TAVILY_API_KEY": "tvly-my-secret"}):
            await execute({"urls": ["https://example.com"]})

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

    with patch("worthdoing_capabilities.capabilities.tavily_extract.handler.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with patch.dict("os.environ", {"TAVILY_API_KEY": "bad-key"}):
            with pytest.raises(httpx.HTTPStatusError):
                await execute({"urls": ["https://example.com"]})


import httpx
