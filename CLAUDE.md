# trendkit - Project Context

## Overview

Multi-platform trend aggregator optimized for LLM tool calls.
- Google Trends (v0.1) ✅
- Naver Trends (planned)
- YouTube Trends (planned)

## Tech Stack

- **Runtime**: Python 3.12+
- **Package Manager**: uv
- **Dependencies**: trendspyg, pytrends, pandas
- **Optional**: selenium, mcp, typer, rich

## Project Structure

```
src/trendkit/
├── core.py           # Public API (trending, related, compare, interest)
├── types.py          # Type definitions (Format, TypedDicts)
├── cli.py            # CLI entry point (trendkit command)
├── mcp_server.py     # MCP server (trendkit-mcp command)
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

### Backend Strategy (Google)

| Backend | Library | Purpose |
|---------|---------|---------|
| RSS | trendspyg | Realtime trending (fast, 10-20 items) |
| Selenium | selenium | Bulk collection (100+ items) |
| pytrends | pytrends | Analysis (interest, related, compare) |

## Commands

```bash
# Development
cd /Users/sdh/Dev/02_production/trendkit
source .venv/bin/activate
uv run python -c "from trendkit import trending; print(trending(limit=5))"

# CLI (after pip install)
trendkit trend --limit 5
trendkit rel 아이폰 --limit 5
trendkit cmp 삼성 애플

# MCP Server (after pip install)
trendkit-mcp

# Tests
uv run pytest tests/ -v
```

## API Quick Reference

```python
from trendkit import trending, related, compare, interest

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

## Roadmap

- [x] v0.1 - Google Trends
- [ ] v0.2 - Naver Trends (DataLab API)
- [ ] v0.3 - YouTube Trends (Data API v3)
