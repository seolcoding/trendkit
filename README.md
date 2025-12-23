# Google Trends API

Lightweight Google Trends wrapper optimized for LLM tool calls.

## Features

- **Token-optimized**: Minimal output format for LLM function calling
- **Multiple backends**: RSS (fast), pytrends (analysis), Selenium (bulk)
- **Multiple interfaces**: Python API, MCP server, CLI

## Installation

```bash
# Basic
pip install google-trends-api

# With CLI
pip install google-trends-api[cli]

# With MCP server
pip install google-trends-api[mcp]

# With Selenium for bulk collection
pip install google-trends-api[selenium]

# All features
pip install google-trends-api[all]
```

## Quick Start

```python
from google_trends_api import trending, related, compare, interest

# Realtime trending (minimal tokens)
keywords = trending(limit=5)
# ['환율', '신한카드', '국민신문고', ...]

# Related queries
related_kw = related("아이폰", limit=5)
# ['아이폰 17', '아이폰 디시', ...]

# Compare keywords
scores = compare(["삼성", "애플"])
# {"삼성": 45.6, "애플": 14.4}

# Interest over time
data = interest(["BTS"], days=7)
# {"dates": [...], "values": {"BTS": [42, 45, ...]}}
```

## CLI Usage

```bash
# Trending keywords
gtrends trend --limit 5
gtrends trend --geo US --format standard

# Related queries
gtrends rel 아이폰 --limit 5

# Compare keywords
gtrends cmp 삼성 애플 --days 90

# Interest history
gtrends hist BTS --days 7
```

## MCP Server

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "google-trends": {
      "command": "google-trends-mcp"
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

Get realtime trending keywords via RSS (fast).

**Parameters:**
- `geo`: Country code (KR, US, JP, etc.)
- `limit`: Number of results (max 20)
- `format`: Output detail level

**Returns:**
- `minimal`: `["keyword1", "keyword2", ...]`
- `standard`: `[{"keyword": "...", "traffic": "..."}]`
- `full`: `[{"keyword": "...", "traffic": "...", "news": [...]}]`

### `trending_bulk(geo="KR", hours=168, limit=100)`

Get bulk trending data via Selenium (slower, more data).

**Parameters:**
- `geo`: Country code
- `hours`: Time period (4, 24, 48, 168)
- `limit`: Number of results (up to ~100)

**Requires:** `pip install google-trends-api[selenium]`

### `related(keyword, geo="KR", limit=10)`

Get related search queries for a keyword.

**Returns:** `["related1", "related2", ...]`

### `compare(keywords, geo="KR", days=90)`

Compare keywords by average search interest.

**Parameters:**
- `keywords`: List of keywords (max 5)
- `days`: Time period (1, 7, 30, 90, 365)

**Returns:** `{"keyword1": 45.6, "keyword2": 14.4}`

### `interest(keywords, geo="KR", days=7)`

Get interest over time for keywords.

**Returns:**
```python
{
    "dates": ["2024-12-16", "2024-12-17", ...],
    "values": {"BTS": [42, 45, ...]}
}
```

### `supported_geos()`

Get list of commonly supported country codes.

**Returns:** `["KR", "US", "JP", "GB", ...]`

## Token Optimization

| Format | Tokens/Item | Use Case |
|--------|-------------|----------|
| `minimal` | ~5 | List keywords only |
| `standard` | ~15 | Keywords + traffic |
| `full` | ~100 | Full data with news |

## Architecture

```
google-trends-api/
├── src/google_trends_api/
│   ├── core.py              # Main API functions
│   ├── types.py             # Type definitions
│   ├── cli.py               # CLI (gtrends command)
│   ├── mcp_server.py        # MCP server
│   └── backends/
│       ├── rss.py           # trendspyg RSS (fast)
│       ├── pytrends_backend.py  # Analysis features
│       └── selenium_backend.py  # Bulk collection
└── tests/                   # Test files
```

### Backend Selection

| Backend | Speed | Data Volume | Use Case |
|---------|-------|-------------|----------|
| RSS (trendspyg) | Fast | 10-20 items | Realtime trending |
| Selenium | Slow | 100+ items | Bulk collection |
| pytrends | Medium | N/A | Analysis (interest, related, compare) |

## Supported Countries

KR, US, JP, GB, DE, FR, CA, AU, IN, BR, MX, ES, IT, NL, SE, CH, TW, HK, SG, TH, VN, ID, MY, PH

## License

MIT
