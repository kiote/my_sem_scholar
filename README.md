# Semantic Scholar MCP Server

A FastMCP server that provides access to the Semantic Scholar academic search API through Claude Code CLI.

## Installation

Add the MCP server using the Claude CLI:

```bash
claude mcp add --transport stdio semantic-scholar -- uvx --from git+https://github.com/kiote/my_sem_scholar.git fastmcp run server.py
```

That's it! The server will be automatically installed and configured.

### Optional: API Key Setup

For better rate limits, get a free API key from [Semantic Scholar](https://www.semanticscholar.org/product/api):

```bash
# Add with API key
claude mcp add --transport stdio semantic-scholar --env SEMANTIC_SCHOLAR_API_KEY=your_key_here -- uvx --from git+https://github.com/kiote/my_sem_scholar.git fastmcp run server.py
```

## Development

If you want to contribute or run tests:

```bash
# Clone the repository
git clone https://github.com/kiote/my_sem_scholar.git
cd my_sem_scholar

# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest -v
```

## Features

- **search_papers**: Search for academic papers by query
- **get_paper_details**: Get detailed information about a specific paper
- **get_paper_citations**: Get papers that cite a specific paper
- **get_paper_references**: Get papers referenced by a specific paper
- **get_author_papers**: Get papers by a specific author
- **Rate limiting**: Automatic 1 req/sec limit
- **API key support**: Optional authentication for better limits

## Documentation

- [Semantic Scholar API](https://api.semanticscholar.org/)
- [FastMCP](https://github.com/jlowin/fastmcp)
