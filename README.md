# Semantic Scholar MCP Server

A FastMCP server that provides access to the Semantic Scholar academic search API through Claude Desktop.

## Installation

1. Clone or download this repository to your local machine

2. Navigate to the project directory:
```bash
cd path/to/my_sem_scholar
```

3. (Optional) Set up your API key for increased rate limits:
```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your API key
# Get your free API key from: https://www.semanticscholar.org/product/api
```

4. Install dependencies:
```bash
uv pip install -e .

# For development (includes testing tools)
uv pip install -e ".[dev]"
```

## Connecting to Claude Desktop

Add this to your Claude Desktop config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "semantic-scholar": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/my_sem_scholar",
        "run",
        "fastmcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

**Important**: Replace `/absolute/path/to/my_sem_scholar` with the actual absolute path to your installation directory.

Then restart Claude Desktop:
- **macOS/Linux**: Quit completely (Cmd+Q / Ctrl+Q) and reopen
- **Windows**: Close and reopen the application

## Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/test_server.py::TestRateLimiting
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
