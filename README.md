# trendkit

Google Trends aggregator optimized for LLM tool calls.

## Features

- **Token-optimized**: Minimal output format for LLM function calling
- **Multiple backends**: RSS (fast), Selenium (bulk), pytrends (analysis)
- **Enriched export**: News, images, related queries with metadata
- **Multiple interfaces**: Python API, CLI, MCP server

## Installation

```bash
# Basic
pip install trendkit

# With Selenium (bulk collection)
pip install trendkit[selenium]

# With CLI
pip install trendkit[cli]

# With MCP server
pip install trendkit[mcp]

# All features
pip install trendkit[all]
```

## Quick Start

```python
from trendkit import trending, trending_bulk, related, compare, interest

# Realtime trending (minimal tokens)
keywords = trending(limit=5)
# ['환율', '신한카드', '국민신문고', ...]

# Bulk collection (~100 items)
data = trending_bulk(limit=100, output="trends.csv")

# Enriched bulk export (with news, related queries, images)
data = trending_bulk(limit=10, enrich=True, output="trends.json")

# Related queries
related_kw = related("아이폰", limit=5)
# ['아이폰 17', '아이폰 디시', ...]

# Compare keywords
scores = compare(["삼성", "애플"])
# {"삼성": 45.6, "애플": 14.4}

# Interest over time
data = interest(["BTS"], days=7)
# {"dates": [...], "values": {"BTS": [42, 45, ...]}}

# YouTube search interest (via Google Trends)
data = interest(["BTS"], platform="youtube")
```

## CLI Usage

```bash
# Trending keywords
trendkit trend --limit 5
trendkit trend --geo US --format standard

# Bulk collection
trendkit bulk --limit 100 --output trends.csv
trendkit bulk --limit 10 --enrich --output trends.json

# Related queries
trendkit rel 아이폰 --limit 5

# Compare keywords
trendkit cmp 삼성 애플 --days 90

# Interest history
trendkit hist BTS --days 7
```

## Bulk Export

### Basic (CSV)
```python
trending_bulk(limit=100, output="trends.csv")
```
```csv
keyword,rank,traffic
내일 날씨,2,20만+
이노스페이스,3,5천+
```

### Enriched (JSON)
```python
trending_bulk(limit=10, enrich=True, output="trends.json")
```
```json
{
  "metadata": {
    "geo": "KR",
    "hours": 168,
    "collected_at": "2025-12-23T23:01:17",
    "total_items": 10,
    "source": "google_trends"
  },
  "trends": [
    {
      "keyword": "내일 날씨",
      "rank": 2,
      "traffic": "20만+",
      "image": {"url": "...", "source": "Daum"},
      "news": [
        {"headline": "...", "url": "...", "source": "..."}
      ],
      "related": ["내일 서울 날씨", "대구 내일 날씨", ...],
      "explore_link": "https://trends.google.com/..."
    }
  ]
}
```

## MCP Server

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

**From source (current)**
```json
{
  "mcpServers": {
    "trendkit": {
      "command": "uv",
      "args": ["--directory", "/ABSOLUTE/PATH/TO/trendkit", "run", "trendkit-mcp"]
    }
  }
}
```

**After PyPI release**
```json
{
  "mcpServers": {
    "trendkit": {
      "command": "uvx",
      "args": ["--from", "trendkit[mcp]", "trendkit-mcp"]
    }
  }
}
```

### Available Tools

| Tool | Description |
|------|-------------|
| `trends_trending` | Get realtime trending keywords |
| `trends_related` | Get related search queries |
| `trends_compare` | Compare keywords by interest |
| `trends_interest` | Get interest over time |

## API Reference

### `trending(geo="KR", limit=10, format="minimal")`

Get realtime trending keywords (via RSS, fast).

**Returns:**
- `minimal`: `["keyword1", "keyword2", ...]`
- `standard`: `[{"keyword": "...", "traffic": "..."}]`
- `full`: `[{"keyword": "...", "traffic": "...", "news": [...]}]`

### `trending_bulk(geo="KR", hours=168, limit=100, enrich=False, output=None)`

Get bulk trending data (via Selenium, ~100 items).

**Parameters:**
- `hours`: Time period (4, 24, 48, 168)
- `enrich`: Add news, images, related queries
- `output`: Save to file (.csv or .json)

### `related(keyword, geo="KR", limit=10)`

Get related search queries for a keyword.

### `compare(keywords, geo="KR", days=90, platform="web")`

Compare keywords by average search interest.

### `interest(keywords, geo="KR", days=7, platform="web")`

Get interest over time for keywords.

**Platform options:** `"web"`, `"youtube"`, `"images"`, `"news"`

## Token Optimization

| Format | Tokens/Item | Use Case |
|--------|-------------|----------|
| `minimal` | ~5 | List keywords only |
| `standard` | ~15 | Keywords + traffic |
| `full` | ~100 | Full data with news |

## Architecture

```
trendkit/
├── src/trendkit/
│   ├── core.py              # Main API functions
│   ├── types.py             # Type definitions
│   ├── cli.py               # CLI (trendkit command)
│   ├── mcp_server.py        # MCP server
│   └── backends/
│       ├── rss.py           # RSS backend (fast, ~20 items)
│       ├── pytrends_backend.py  # Analysis features
│       └── selenium_backend.py  # Bulk collection (~100 items)
└── tests/
```

## License

MIT
