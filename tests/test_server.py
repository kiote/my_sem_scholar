"""
Unit tests for Semantic Scholar MCP Server
"""

import asyncio
import time
from unittest.mock import AsyncMock, Mock, patch
import pytest
import httpx
import respx
import server
from server import (
    _wait_for_rate_limit,
    _get_headers,
    BASE_URL,
)

# Access the actual functions from the mcp tool wrappers
search_papers = server.search_papers.fn
get_paper_details = server.get_paper_details.fn
get_paper_citations = server.get_paper_citations.fn
get_paper_references = server.get_paper_references.fn
get_author_papers = server.get_author_papers.fn


@pytest.fixture
def reset_rate_limit():
    """Reset rate limit state before each test."""
    import server
    server._last_request_time = 0.0
    yield
    server._last_request_time = 0.0


@pytest.fixture
def mock_api_key():
    """Mock API key environment variable."""
    with patch("server.API_KEY", "test_api_key_123"):
        yield


@pytest.fixture
def no_api_key():
    """Mock no API key."""
    with patch("server.API_KEY", None):
        yield


class TestRateLimiting:
    """Tests for rate limiting functionality."""

    @pytest.mark.asyncio
    async def test_rate_limit_waits_for_second_request(self, reset_rate_limit):
        """Test that second rapid request is delayed."""
        start_time = time.time()

        # First request should be immediate
        await _wait_for_rate_limit()
        first_elapsed = time.time() - start_time
        assert first_elapsed < 0.1  # Should be nearly instant

        # Second request should wait
        await _wait_for_rate_limit()
        second_elapsed = time.time() - start_time
        assert second_elapsed >= 1.0  # Should wait at least 1 second

    @pytest.mark.asyncio
    async def test_rate_limit_allows_after_delay(self, reset_rate_limit):
        """Test that requests after delay don't wait."""
        # First request
        await _wait_for_rate_limit()

        # Wait more than 1 second
        await asyncio.sleep(1.1)

        # Second request should be immediate
        start_time = time.time()
        await _wait_for_rate_limit()
        elapsed = time.time() - start_time
        assert elapsed < 0.1  # Should be nearly instant

    @pytest.mark.asyncio
    async def test_rate_limit_concurrent_requests(self, reset_rate_limit):
        """Test that concurrent requests are properly serialized."""
        start_time = time.time()

        # Launch 3 concurrent requests
        tasks = [_wait_for_rate_limit() for _ in range(3)]
        await asyncio.gather(*tasks)

        elapsed = time.time() - start_time
        # Should take at least 2 seconds (0, 1, 2 second marks)
        assert elapsed >= 2.0


class TestAPIKeyHandling:
    """Tests for API key functionality."""

    def test_headers_with_api_key(self, mock_api_key):
        """Test that headers include API key when present."""
        headers = _get_headers()
        assert "x-api-key" in headers
        assert headers["x-api-key"] == "test_api_key_123"

    def test_headers_without_api_key(self, no_api_key):
        """Test that headers are empty when no API key."""
        headers = _get_headers()
        assert "x-api-key" not in headers
        assert headers == {}


class TestSearchPapers:
    """Tests for search_papers function."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_papers_success(self, reset_rate_limit, no_api_key):
        """Test successful paper search."""
        mock_response = {
            "total": 1,
            "data": [{
                "paperId": "test123",
                "title": "Test Paper",
                "year": 2023,
                "citationCount": 10
            }]
        }

        respx.get(f"{BASE_URL}/paper/search").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        result = await search_papers("test query", limit=10)
        assert result == mock_response
        assert result["total"] == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_papers_with_api_key(self, reset_rate_limit, mock_api_key):
        """Test that API key is included in request."""
        mock_response = {"total": 0, "data": []}

        route = respx.get(f"{BASE_URL}/paper/search").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        await search_papers("test query")

        # Verify the request was made with the API key header
        assert route.called
        request = route.calls.last.request
        assert request.headers.get("x-api-key") == "test_api_key_123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_papers_respects_limit(self, reset_rate_limit, no_api_key):
        """Test that limit parameter is respected."""
        mock_response = {"total": 0, "data": []}

        route = respx.get(f"{BASE_URL}/paper/search").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        await search_papers("test query", limit=5)

        request = route.calls.last.request
        assert "limit=5" in str(request.url)


class TestGetPaperDetails:
    """Tests for get_paper_details function."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_paper_details_success(self, reset_rate_limit, no_api_key):
        """Test successful paper details retrieval."""
        paper_id = "test123"
        mock_response = {
            "paperId": paper_id,
            "title": "Test Paper",
            "year": 2023,
            "abstract": "Test abstract"
        }

        respx.get(f"{BASE_URL}/paper/{paper_id}").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        result = await get_paper_details(paper_id)
        assert result == mock_response
        assert result["paperId"] == paper_id

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_paper_details_with_custom_fields(self, reset_rate_limit, no_api_key):
        """Test custom fields parameter."""
        paper_id = "test123"
        mock_response = {"paperId": paper_id, "title": "Test"}

        route = respx.get(f"{BASE_URL}/paper/{paper_id}").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        await get_paper_details(paper_id, fields="title,year")

        request = route.calls.last.request
        assert "fields=title%2Cyear" in str(request.url)


class TestGetPaperCitations:
    """Tests for get_paper_citations function."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_paper_citations_success(self, reset_rate_limit, no_api_key):
        """Test successful citations retrieval."""
        paper_id = "test123"
        mock_response = {
            "data": [{
                "citingPaper": {
                    "paperId": "citing1",
                    "title": "Citing Paper"
                }
            }]
        }

        respx.get(f"{BASE_URL}/paper/{paper_id}/citations").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        result = await get_paper_citations(paper_id)
        assert result == mock_response


class TestGetPaperReferences:
    """Tests for get_paper_references function."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_paper_references_success(self, reset_rate_limit, no_api_key):
        """Test successful references retrieval."""
        paper_id = "test123"
        mock_response = {
            "data": [{
                "citedPaper": {
                    "paperId": "ref1",
                    "title": "Referenced Paper"
                }
            }]
        }

        respx.get(f"{BASE_URL}/paper/{paper_id}/references").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        result = await get_paper_references(paper_id)
        assert result == mock_response


class TestGetAuthorPapers:
    """Tests for get_author_papers function."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_author_papers_success(self, reset_rate_limit, no_api_key):
        """Test successful author papers retrieval."""
        author_id = "author123"
        mock_response = {
            "data": [{
                "paperId": "paper1",
                "title": "Author Paper"
            }]
        }

        respx.get(f"{BASE_URL}/author/{author_id}/papers").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        result = await get_author_papers(author_id)
        assert result == mock_response


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_handles_404_error(self, reset_rate_limit, no_api_key):
        """Test handling of 404 error."""
        paper_id = "nonexistent"

        respx.get(f"{BASE_URL}/paper/{paper_id}").mock(
            return_value=httpx.Response(404, json={"error": "Not found"})
        )

        with pytest.raises(httpx.HTTPStatusError):
            await get_paper_details(paper_id)

    @pytest.mark.asyncio
    @respx.mock
    async def test_handles_rate_limit_error(self, reset_rate_limit, no_api_key):
        """Test handling of 429 rate limit error."""
        respx.get(f"{BASE_URL}/paper/search").mock(
            return_value=httpx.Response(429, json={"error": "Rate limited"})
        )

        with pytest.raises(httpx.HTTPStatusError):
            await search_papers("test query")
