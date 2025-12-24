# trendkit

**Token-Optimized Trends for AI**

[![PyPI version](https://badge.fury.io/py/trendkit.svg)](https://badge.fury.io/py/trendkit)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

Google Trends aggregator designed for LLM tool calls with minimal token usage.

---

## Why trendkit?

> *"Claude에게 트렌드를 물었더니 5,000 토큰을 썼다. 그래서 5토큰으로 줄였다."*

| Problem | Before | After (trendkit) |
|---------|--------|------------------|
| Token waste | ~500 tokens/item | **~5 tokens/item** |
| Complex setup | API keys, auth | `pip install` and go |
| No MCP support | Build your own | **Built-in MCP server** |
| Limited bulk | ~20 items max | **100+ items** |

### Comparison with Alternatives

| Feature | trendkit | pytrends | SerpAPI | Tavily |
|---------|----------|----------|---------|--------|
| Price | **Free** | Free | $50/mo | $20/mo |
| Token Optimized | **Yes** | No | No | No |
| MCP Native | **Yes** | No | No | Partial |
| Bulk Collection | **100+** | ~20 | 100+ | No |
| Setup Complexity | **Easy** | Easy | Medium | Easy |

---

## Features

- **Token-optimized**: Minimal output format for LLM function calling (~5 tokens/item)
- **Multiple backends**: RSS (fast), Playwright with stealth (bulk), pytrends (analysis)
- **Anti-detection**: playwright-stealth bypasses bot detection
- **Enriched export**: News, images, related queries with metadata
- **Multiple interfaces**: Python API, CLI, MCP server

---

## Installation

```bash
# Basic
pip install trendkit

# With Playwright (bulk collection with anti-detection)
pip install trendkit[playwright]
playwright install chromium

# With CLI
pip install trendkit[cli]

# With MCP server
pip install trendkit[mcp]

# All features
pip install trendkit[all]
playwright install chromium
```

---

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

---

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

---

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

---

## Token Optimization

The key design principle of trendkit is **minimal token usage** for LLM integrations.

| Format | Tokens/Item | Example Output |
|--------|-------------|----------------|
| `minimal` | **~5** | `["키워드1", "키워드2"]` |
| `standard` | ~15 | `[{"keyword": "키워드1", "traffic": "10만+"}]` |
| `full` | ~100 | Full data with news, images, related |

### Real-world Impact

```python
# Traditional approach: ~5,000 tokens for 10 items
# trendkit minimal: ~50 tokens for 10 items
# = 99% token reduction
```

---

## Use Cases

### AI News Bot
```python
from trendkit import trending, related

# Get trending topics
topics = trending(limit=5, format="minimal")

# Expand with related queries
for topic in topics:
    queries = related(topic, limit=3)
    # Generate news summary for each...
```

### Content Recommendation
```python
from trendkit import compare

# Find which topic is more popular
scores = compare(["React", "Vue", "Svelte"])
# {"React": 67.2, "Vue": 24.1, "Svelte": 8.7}
```

### Marketing Trend Analysis
```python
from trendkit import trending_bulk

# Collect comprehensive trend data
data = trending_bulk(
    limit=100,
    enrich=True,
    output="weekly_trends.json"
)
```

---

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
      "related": ["내일 서울 날씨", "대구 내일 날씨"],
      "explore_link": "https://trends.google.com/..."
    }
  ]
}
```

---

## API Reference

### `trending(geo="KR", limit=10, format="minimal")`

Get realtime trending keywords (via RSS, fast).

**Returns:**
- `minimal`: `["keyword1", "keyword2", ...]`
- `standard`: `[{"keyword": "...", "traffic": "..."}]`
- `full`: `[{"keyword": "...", "traffic": "...", "news": [...]}]`

### `trending_bulk(geo="KR", hours=168, limit=100, enrich=False, output=None, headless=True)`

Get bulk trending data (via Playwright with stealth, ~100 items).

**Parameters:**
- `hours`: Time period (4, 24, 48, 168)
- `enrich`: Add news, images, related queries
- `output`: Save to file (.csv or .json)
- `headless`: Run browser in headless mode (default: True, set False for debugging)

### `related(keyword, geo="KR", limit=10)`

Get related search queries for a keyword.

### `compare(keywords, geo="KR", days=90, platform="web")`

Compare keywords by average search interest.

### `interest(keywords, geo="KR", days=7, platform="web")`

Get interest over time for keywords.

**Platform options:** `"web"`, `"youtube"`, `"images"`, `"news"`

---

## Architecture

```
trendkit/
├── src/trendkit/
│   ├── core.py              # Main API functions
│   ├── types.py             # Type definitions
│   ├── cli.py               # CLI (trendkit command)
│   ├── mcp_server.py        # MCP server
│   └── backends/
│       ├── rss.py               # RSS backend (fast, ~20 items)
│       ├── pytrends_backend.py  # Analysis features
│       └── playwright_backend.py # Bulk collection with stealth (~100 items)
└── tests/                   # 206 tests (86% coverage)
```

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/seolcoding/trendkit.git
cd trendkit
uv sync --all-extras
uv run pytest
```

---

## Roadmap

See [ROADMAP.md](docs/ROADMAP.md) for planned features.

**Implemented:**
- ✅ Cache layer for reduced API calls
- ✅ Playwright with stealth mode for anti-detection
- ✅ Comprehensive error handling with helpful suggestions

**Coming Soon:**
- LangChain Tool integration
- Multi-geo support expansion

---

## License

MIT
