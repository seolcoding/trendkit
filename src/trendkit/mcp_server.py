"""
MCP Server for trendkit.

Run with: trendkit-mcp
Or configure in Claude Desktop settings.
"""

from typing import Literal

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise ImportError("MCP not installed. Run: pip install trendkit[mcp]")

from . import trending, related, compare, interest
from .backends.pytrends_backend import Platform

# Create FastMCP server
mcp = FastMCP(
    "trendkit",
    instructions="Google Trends data aggregator optimized for LLM tool calls. "
    "Provides realtime trending keywords, related queries, keyword comparison, "
    "and interest over time data.",
)


@mcp.tool()
def trends_trending(
    geo: str = "KR",
    limit: int = 10,
    format: Literal["minimal", "standard", "full"] = "minimal",
) -> list[str] | list[dict]:
    """
    Get realtime trending keywords from Google Trends.

    Args:
        geo: Country code (KR, US, JP, GB, DE, FR, etc.)
        limit: Number of results to return (max 20)
        format: Output detail level
            - minimal: ["keyword1", "keyword2", ...] (~5 tokens/item)
            - standard: [{"keyword": "...", "traffic": "..."}] (~15 tokens/item)
            - full: [{"keyword": "...", "traffic": "...", "news": [...]}] (~100 tokens/item)

    Returns:
        List of trending keywords or detailed dicts based on format.

    Example:
        trends_trending(geo="KR", limit=5)
        → ["환율", "날씨", "뉴스", "주식", "로또"]
    """
    return trending(geo=geo, limit=limit, format=format)


@mcp.tool()
def trends_related(
    keyword: str,
    geo: str = "KR",
    limit: int = 10,
) -> list[str]:
    """
    Get related search queries for a keyword.

    Args:
        keyword: Target keyword to find related queries for
        geo: Country code (KR, US, JP, etc.)
        limit: Number of results to return

    Returns:
        List of related search queries.

    Example:
        trends_related(keyword="아이폰", limit=5)
        → ["아이폰 16", "아이폰 17", "아이폰 케이스", ...]
    """
    return related(keyword=keyword, geo=geo, limit=limit)


@mcp.tool()
def trends_compare(
    keywords: list[str],
    geo: str = "KR",
    days: int = 90,
    platform: Platform = "web",
) -> dict[str, float]:
    """
    Compare keywords by average search interest.

    Args:
        keywords: Keywords to compare (max 5)
        geo: Country code (KR, US, JP, etc.)
        days: Time period in days (7, 30, 90, 365)
        platform: Search platform - "web", "youtube", "images", "news"

    Returns:
        Dictionary mapping keywords to their average interest scores (0-100).

    Example:
        trends_compare(keywords=["삼성", "애플"], days=90)
        → {"삼성": 45.6, "애플": 32.1}
    """
    return compare(keywords=keywords, geo=geo, days=days, platform=platform)


@mcp.tool()
def trends_interest(
    keywords: list[str],
    geo: str = "KR",
    days: int = 7,
    platform: Platform = "web",
) -> dict:
    """
    Get interest over time for keywords (time series data).

    Args:
        keywords: Keywords to analyze (max 5)
        geo: Country code (KR, US, JP, etc.)
        days: Time period in days (1, 7, 30, 90, 365)
        platform: Search platform - "web", "youtube", "images", "news"

    Returns:
        Dictionary with dates and values for each keyword.
        {
            "dates": ["2024-12-01", "2024-12-02", ...],
            "values": {"keyword1": [42, 45, ...], "keyword2": [...]}
        }

    Example:
        trends_interest(keywords=["BTS"], days=7)
        → {"dates": [...], "values": {"BTS": [42, 45, 38, ...]}}
    """
    return interest(keywords=keywords, geo=geo, days=days, platform=platform)


def main():
    """Entry point for MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
