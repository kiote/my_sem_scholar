"""
Semantic Scholar MCP Server

A FastMCP server providing tools to search and retrieve academic papers from Semantic Scholar API.
Implements rate limiting of 1 request per second to respect API limits.
Supports optional API key authentication via .env file.
"""

import asyncio
import os
import time
from typing import Optional
from pathlib import Path
import httpx
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize FastMCP server
mcp = FastMCP("Semantic Scholar")

# Semantic Scholar API base URL
BASE_URL = "https://api.semanticscholar.org/graph/v1"

# API Key (optional - improves rate limits)
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

# Rate limiting: 1 request per second
RATE_LIMIT_SECONDS = 1.0
_last_request_time = 0.0
_rate_limit_lock = asyncio.Lock()


def _get_headers() -> dict:
    """Get HTTP headers including API key if available."""
    headers = {}
    if API_KEY:
        headers["x-api-key"] = API_KEY
    return headers


async def _wait_for_rate_limit():
    """Wait to respect rate limit of 1 request per second."""
    global _last_request_time

    async with _rate_limit_lock:
        current_time = time.time()
        time_since_last = current_time - _last_request_time

        if time_since_last < RATE_LIMIT_SECONDS:
            wait_time = RATE_LIMIT_SECONDS - time_since_last
            await asyncio.sleep(wait_time)

        _last_request_time = time.time()


@mcp.tool()
async def search_papers(
    query: str,
    limit: int = 10,
    fields: str = "title,authors,year,abstract,citationCount,url"
) -> dict:
    """
    Search for academic papers on Semantic Scholar.

    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 10, max: 100)
        fields: Comma-separated list of fields to return

    Returns:
        Dictionary containing search results with paper metadata
    """
    await _wait_for_rate_limit()

    async with httpx.AsyncClient() as client:
        params = {
            "query": query,
            "limit": min(limit, 100),
            "fields": fields
        }

        response = await client.get(
            f"{BASE_URL}/paper/search",
            params=params,
            headers=_get_headers(),
            timeout=30.0
        )
        response.raise_for_status()

        return response.json()


@mcp.tool()
async def get_paper_details(
    paper_id: str,
    fields: str = "title,authors,year,abstract,citationCount,url,venue,publicationDate,referenceCount,influentialCitationCount"
) -> dict:
    """
    Get detailed information about a specific paper by its Semantic Scholar ID.

    Args:
        paper_id: Semantic Scholar paper ID (e.g., "649def34f8be52c8b66281af98ae884c09aef38b")
        fields: Comma-separated list of fields to return

    Returns:
        Dictionary containing detailed paper information
    """
    await _wait_for_rate_limit()

    async with httpx.AsyncClient() as client:
        params = {"fields": fields}

        response = await client.get(
            f"{BASE_URL}/paper/{paper_id}",
            params=params,
            headers=_get_headers(),
            timeout=30.0
        )
        response.raise_for_status()

        return response.json()


@mcp.tool()
async def get_paper_citations(
    paper_id: str,
    limit: int = 10,
    fields: str = "title,authors,year,citationCount"
) -> dict:
    """
    Get papers that cite a specific paper.

    Args:
        paper_id: Semantic Scholar paper ID
        limit: Maximum number of citations to return (default: 10, max: 1000)
        fields: Comma-separated list of fields to return for each citation

    Returns:
        Dictionary containing citing papers
    """
    await _wait_for_rate_limit()

    async with httpx.AsyncClient() as client:
        params = {
            "limit": min(limit, 1000),
            "fields": fields
        }

        response = await client.get(
            f"{BASE_URL}/paper/{paper_id}/citations",
            params=params,
            headers=_get_headers(),
            timeout=30.0
        )
        response.raise_for_status()

        return response.json()


@mcp.tool()
async def get_paper_references(
    paper_id: str,
    limit: int = 10,
    fields: str = "title,authors,year,citationCount"
) -> dict:
    """
    Get papers referenced by a specific paper.

    Args:
        paper_id: Semantic Scholar paper ID
        limit: Maximum number of references to return (default: 10, max: 1000)
        fields: Comma-separated list of fields to return for each reference

    Returns:
        Dictionary containing referenced papers
    """
    await _wait_for_rate_limit()

    async with httpx.AsyncClient() as client:
        params = {
            "limit": min(limit, 1000),
            "fields": fields
        }

        response = await client.get(
            f"{BASE_URL}/paper/{paper_id}/references",
            params=params,
            headers=_get_headers(),
            timeout=30.0
        )
        response.raise_for_status()

        return response.json()


@mcp.tool()
async def get_author_papers(
    author_id: str,
    limit: int = 10,
    fields: str = "title,year,citationCount,url"
) -> dict:
    """
    Get papers by a specific author.

    Args:
        author_id: Semantic Scholar author ID
        limit: Maximum number of papers to return (default: 10, max: 1000)
        fields: Comma-separated list of fields to return for each paper

    Returns:
        Dictionary containing author's papers
    """
    await _wait_for_rate_limit()

    async with httpx.AsyncClient() as client:
        params = {
            "limit": min(limit, 1000),
            "fields": fields
        }

        response = await client.get(
            f"{BASE_URL}/author/{author_id}/papers",
            params=params,
            headers=_get_headers(),
            timeout=30.0
        )
        response.raise_for_status()

        return response.json()
