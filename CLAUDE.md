# trendkit - Project Context

## Overview

Google Trends aggregator optimized for LLM tool calls.
- Token-optimized output formats
- Multiple collection methods (RSS, Selenium, pytrends)
- Enriched bulk export with metadata

## Tech Stack

- **Runtime**: Python 3.12+
- **Package Manager**: uv
- **Dependencies**: trendspyg, pytrends, pandas
- **Optional**: selenium, mcp, typer, rich

## Project Structure

```
src/trendkit/
├── core.py           # Public API (trending, trending_bulk, related, compare, interest)
├── types.py          # Type definitions (Format, Platform)
├── cli.py            # CLI entry point (trendkit command)
├── mcp_server.py     # MCP server (trendkit-mcp command)
└── backends/
    ├── rss.py              # trendspyg RSS backend (fast, ~20 items)
    ├── pytrends_backend.py # Analysis features (interest, related, compare)
    └── selenium_backend.py # Bulk collection (~100 items)

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

| Backend | Library | Purpose | Limit |
|---------|---------|---------|-------|
| RSS | trendspyg | Realtime trending (fast) | ~20 |
| Selenium | selenium | Bulk collection | ~100 |
| pytrends | pytrends | Analysis (interest, related, compare) | - |

### Bulk Export

`trending_bulk()` supports enriched export with:
- Metadata (geo, hours, limit, collected_at, source)
- News articles (headline, url, source, image)
- Related queries (up to 10)
- Images (url, source)
- Explore links

## Commands

```bash
# Development
uv run python -c "from trendkit import trending; print(trending(limit=5))"

# CLI
trendkit trend --limit 5
trendkit bulk --limit 100 --output trends.csv
trendkit bulk --limit 10 --enrich --output trends.json
trendkit rel 아이폰 --limit 5
trendkit cmp 삼성 애플

# Tests
uv run pytest tests/ -v
```

## API Quick Reference

```python
from trendkit import trending, trending_bulk, related, compare, interest

# Realtime trending (RSS, fast)
trending(geo="KR", limit=10, format="minimal")  # List[str]

# Bulk trending (Selenium, ~100 items)
trending_bulk(geo="KR", hours=168, limit=100)                    # List[dict]
trending_bulk(limit=100, output="trends.csv")                     # Save to CSV
trending_bulk(limit=10, enrich=True, output="trends.json")       # Enriched JSON

# Analysis
related("keyword", geo="KR", limit=10)          # List[str]
compare(["kw1", "kw2"], geo="KR", days=90)      # Dict[str, float]
interest(["kw1"], geo="KR", days=7)             # Dict with dates/values
interest(["kw1"], platform="youtube")           # YouTube search interest
```

## MCP Tools

- `trends_trending`: Realtime trending keywords
- `trends_related`: Related search queries
- `trends_compare`: Compare keyword interest
- `trends_interest`: Interest over time
