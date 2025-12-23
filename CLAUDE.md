# Google Trends API - Project Context

## Overview

LLM-optimized Google Trends wrapper with token-efficient output formats.

## Tech Stack

- **Runtime**: Python 3.12+
- **Package Manager**: uv
- **Dependencies**: trendspyg, pytrends, pandas
- **Optional**: selenium, mcp, typer, rich

## Project Structure

```
src/google_trends_api/
├── core.py           # Public API (trending, related, compare, interest)
├── types.py          # Type definitions (Format, TypedDicts)
├── cli.py            # CLI entry point (gtrends command)
├── mcp_server.py     # MCP server (google-trends-mcp command)
└── backends/
    ├── rss.py        # trendspyg RSS backend (fast)
    ├── pytrends_backend.py  # Analysis features
    └── selenium_backend.py  # Bulk collection

tests/
└── test_api.py       # API tests
```

## Key Design Decisions

### Token Optimization

Three output formats to minimize LLM token usage:
- `minimal`: List of strings only (~5 tokens/item)
- `standard`: Dict with keyword + traffic (~15 tokens/item)
- `full`: Complete data with news (~100 tokens/item)

### Backend Strategy

| Backend | Library | Purpose |
|---------|---------|---------|
| RSS | trendspyg | Realtime trending (fast, 10-20 items) |
| Selenium | selenium | Bulk collection (100+ items) |
| pytrends | pytrends | Analysis (interest, related, compare) |

Note: pytrends `trending_searches()` returns 404 - use trendspyg RSS instead.

## Commands

```bash
# Development
source .venv/bin/activate
uv run python -c "from google_trends_api import trending; print(trending(limit=5))"

# CLI (after pip install)
gtrends trend --limit 5
gtrends rel 아이폰 --limit 5
gtrends cmp 삼성 애플

# MCP Server (after pip install)
google-trends-mcp

# Tests
uv run pytest tests/ -v
```

## API Quick Reference

```python
from google_trends_api import trending, related, compare, interest

trending(geo="KR", limit=10, format="minimal")  # List[str]
related("keyword", geo="KR", limit=10)          # List[str]
compare(["kw1", "kw2"], geo="KR", days=90)      # Dict[str, float]
interest(["kw1"], geo="KR", days=7)             # Dict with dates/values
```

## MCP Tools

- `trends_trending`: Realtime trending keywords
- `trends_related`: Related search queries
- `trends_compare`: Compare keyword interest
- `trends_interest`: Interest over time

## Content Creation

This package does NOT handle content creation. It provides data only.
Content generation is the responsibility of downstream consumers.
