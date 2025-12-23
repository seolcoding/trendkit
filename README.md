# trendkit

Multi-platform trend aggregator optimized for LLM tool calls.

## Supported Platforms

| Platform | Status | Method |
|----------|--------|--------|
| Google Trends | ✅ v0.1 | RSS + pytrends |
| Naver Trends | 🔜 Planned | DataLab API |
| YouTube Trends | 🔜 Planned | Data API v3 |

## Features

- **Token-optimized**: Minimal output format for LLM function calling
- **Direct scraping**: No external API dependency
- **Multiple interfaces**: Python API, MCP server, CLI

## Installation

```bash
# Basic
pip install trendkit

# With CLI
pip install trendkit[cli]

# With MCP server
pip install trendkit[mcp]

# All features
pip install trendkit[all]
```

## Quick Start

```python
from trendkit import trending, related, compare, interest

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
trendkit trend --limit 5
trendkit trend --geo US --format standard

# Related queries
trendkit rel 아이폰 --limit 5

# Compare keywords
trendkit cmp 삼성 애플 --days 90

# Interest history
trendkit hist BTS --days 7
```

## MCP Server

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "trendkit": {
      "command": "trendkit-mcp"
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

Get realtime trending keywords.

**Returns:**
- `minimal`: `["keyword1", "keyword2", ...]`
- `standard`: `[{"keyword": "...", "traffic": "..."}]`
- `full`: `[{"keyword": "...", "traffic": "...", "news": [...]}]`

### `related(keyword, geo="KR", limit=10)`

Get related search queries for a keyword.

### `compare(keywords, geo="KR", days=90)`

Compare keywords by average search interest.

### `interest(keywords, geo="KR", days=7)`

Get interest over time for keywords.

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
│       ├── google/          # Google Trends backends
│       ├── naver/           # Naver Trends (planned)
│       └── youtube/         # YouTube Trends (planned)
└── tests/
```

## Roadmap

- [x] v0.1 - Google Trends
- [ ] v0.2 - Naver Trends
- [ ] v0.3 - YouTube Trends

## License

MIT
