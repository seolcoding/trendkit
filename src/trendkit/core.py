"""
Core API functions for Google Trends.

Optimized for LLM tool calls with minimal token usage.
"""

from typing import Literal, Optional
from functools import lru_cache

from .types import Format
from .backends.rss import RSSBackend
from .backends.pytrends_backend import PyTrendsBackend

# Lazy-loaded backends
_pytrends_backend: Optional[PyTrendsBackend] = None


def _get_pytrends() -> PyTrendsBackend:
    """Get or create PyTrends backend (singleton)."""
    global _pytrends_backend
    if _pytrends_backend is None:
        _pytrends_backend = PyTrendsBackend()
    return _pytrends_backend


# ============================================
# Realtime Trending
# ============================================

def trending(
    geo: str = "KR",
    limit: int = 10,
    format: Format = "minimal",
) -> list[str] | list[dict]:
    """
    Get realtime trending keywords (fast, via RSS).

    Args:
        geo: Country code (KR, US, JP, etc.)
        limit: Number of results (max 20)
        format: Output format
            - "minimal": ["keyword1", "keyword2", ...] (~5 tokens/item)
            - "standard": [{"keyword": "...", "traffic": "..."}] (~15 tokens/item)
            - "full": [{"keyword": "...", "news": [...]}] (~100 tokens/item)

    Returns:
        List of trending keywords or dicts.

    Example:
        >>> trending(limit=5)
        ['환율', '신한카드', '국민신문고', '국가장학금', '흑백요리사2']
    """
    return RSSBackend.fetch_trending(geo=geo, limit=limit, format=format)


def trending_bulk(
    geo: str = "KR",
    hours: int = 168,
    limit: int = 100,
) -> list[dict]:
    """
    Get bulk trending data with Selenium (slower, more data).

    Args:
        geo: Country code
        hours: Time period (4, 24, 48, 168)
        limit: Number of results (max ~100)

    Returns:
        [{"keyword": "...", "rank": 1, "traffic": "..."}]

    Note:
        Requires selenium extra: pip install google-trends-api[selenium]
    """
    from .backends.selenium_backend import SeleniumBackend

    backend = SeleniumBackend(headless=True)
    try:
        return backend.fetch_trending(geo=geo, hours=hours, limit=limit)
    finally:
        backend.close()


# ============================================
# Analysis Functions (via pytrends)
# ============================================

def interest(
    keywords: list[str],
    geo: str = "KR",
    days: int = 7,
) -> dict:
    """
    Get interest over time for keywords.

    Args:
        keywords: Keywords to analyze (max 5)
        geo: Country code
        days: Time period (1, 7, 30, 90, 365)

    Returns:
        {
            "dates": ["2024-12-16", "2024-12-17", ...],
            "values": {"BTS": [42, 45, ...]}
        }

    Example:
        >>> interest(["BTS"], days=7)
        {"dates": [...], "values": {"BTS": [42, 45, 38, ...]}}
    """
    return _get_pytrends().interest_over_time(keywords, geo, days)


def related(
    keyword: str,
    geo: str = "KR",
    limit: int = 10,
) -> list[str]:
    """
    Get related queries for a keyword.

    Args:
        keyword: Target keyword
        geo: Country code
        limit: Number of results

    Returns:
        ["related1", "related2", ...]

    Example:
        >>> related("아이폰", limit=5)
        ['아이폰 17', '아이폰 디시', '아이폰 16', ...]
    """
    return _get_pytrends().related_queries(keyword, geo, limit=limit)


def compare(
    keywords: list[str],
    geo: str = "KR",
    days: int = 90,
) -> dict[str, float]:
    """
    Compare keywords by average interest.

    Args:
        keywords: Keywords to compare (max 5)
        geo: Country code
        days: Time period

    Returns:
        {"keyword1": 45.6, "keyword2": 14.4}

    Example:
        >>> compare(["삼성", "애플"])
        {"삼성": 45.6, "애플": 14.4}
    """
    return _get_pytrends().compare(keywords, geo, days)


# ============================================
# Utility Functions
# ============================================

def supported_geos() -> list[str]:
    """
    Get list of commonly supported country codes.

    Returns:
        ["KR", "US", "JP", "GB", ...]
    """
    return [
        "KR", "US", "JP", "GB", "DE", "FR", "CA", "AU",
        "IN", "BR", "MX", "ES", "IT", "NL", "SE", "CH",
        "TW", "HK", "SG", "TH", "VN", "ID", "MY", "PH",
    ]
