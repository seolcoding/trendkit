"""
Core API functions for trendkit.

Multi-platform trend aggregator optimized for LLM tool calls.
Supports: Google Trends
"""

from __future__ import annotations

import logging
import time
from typing import Optional, overload

from .types import Format
from .backends.rss import RSSBackend
from .backends.pytrends_backend import PyTrendsBackend, Platform
from .cache import get_cache, LRUCache
from .exceptions import (
    TrendkitError,
    TrendkitAPIError,
    TrendkitRateLimitError,
    TrendkitTimeoutError,
    TrendkitServiceError,
    TrendkitDriverError,
    TrendkitValidationError,
    RetryConfig,
)

# Logger
logger = logging.getLogger(__name__)

# Lazy-loaded backends
_pytrends_backend: Optional[PyTrendsBackend] = None


def _get_pytrends() -> PyTrendsBackend:
    """Get or create PyTrends backend (singleton)."""
    global _pytrends_backend
    if _pytrends_backend is None:
        _pytrends_backend = PyTrendsBackend()
    return _pytrends_backend


def _validate_geo(geo: str) -> None:
    """Validate geo code."""
    valid_geos = supported_geos()
    if geo.upper() not in valid_geos:
        raise TrendkitValidationError(
            message=f"Invalid geo code: '{geo}'",
            parameter="geo",
            valid_values=valid_geos[:10],  # Show first 10
            suggestion=f"Use one of: {', '.join(valid_geos[:10])}..."
        )


def _validate_limit(limit: int, max_limit: int = 100) -> None:
    """Validate limit parameter."""
    if limit < 1:
        raise TrendkitValidationError(
            message=f"limit must be positive, got {limit}",
            parameter="limit"
        )
    if limit > max_limit:
        raise TrendkitValidationError(
            message=f"limit exceeds maximum ({max_limit}), got {limit}",
            parameter="limit",
            suggestion=f"Use limit <= {max_limit}"
        )


def _with_retry(
    func,
    retry_config: Optional[RetryConfig] = None,
    retryable_exceptions: tuple = (TrendkitRateLimitError,)
):
    """Execute function with exponential backoff retry.

    Args:
        func: Function to execute
        retry_config: Retry configuration
        retryable_exceptions: Exceptions that trigger retry

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    config = retry_config or RetryConfig()
    last_exception = None

    for attempt in range(config.max_retries + 1):
        try:
            return func()
        except retryable_exceptions as e:
            last_exception = e
            if attempt < config.max_retries:
                delay = config.get_delay(attempt)
                logger.warning(
                    f"Attempt {attempt + 1}/{config.max_retries + 1} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f"All {config.max_retries + 1} attempts failed")

    raise last_exception


# ============================================
# Realtime Trending
# ============================================

def trending(
    geo: str = "KR",
    limit: int = 10,
    format: Format = "minimal",
    cache: bool = False,
    ttl: int = 300,
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
        cache: Enable caching (default: False)
        ttl: Cache time-to-live in seconds (default: 300)

    Returns:
        List of trending keywords or dicts.

    Raises:
        TrendkitValidationError: If geo or limit is invalid
        TrendkitAPIError: If API call fails

    Example:
        >>> trending(limit=5)
        ['환율', '신한카드', '국민신문고', '국가장학금', '흑백요리사2']

        >>> trending(limit=5, cache=True, ttl=60)  # Cache for 60 seconds
    """
    _validate_limit(limit, max_limit=20)

    if cache:
        cache_instance = get_cache()
        cache_key = cache_instance._make_key("trending", (geo, limit, format), {})
        cached_result = cache_instance.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for trending({geo}, {limit}, {format})")
            return cached_result

    result = RSSBackend.fetch_trending(geo=geo, limit=limit, format=format)

    if cache:
        cache_instance.set(cache_key, result, ttl)
        logger.debug(f"Cached trending({geo}, {limit}, {format}) for {ttl}s")

    return result


def trending_bulk(
    geo: str = "KR",
    hours: int = 168,
    limit: int = 100,
    enrich: bool = False,
    output: Optional[str] = None,
    timeout: float = 60.0,
    headless: bool = True,
) -> dict | list[dict]:
    """
    Get bulk trending data with Playwright stealth browser (slower, more data).

    Uses playwright-stealth for anti-detection:
    - Bypasses bot detection on Google Trends
    - Faster than Selenium with async I/O
    - Spoofs browser fingerprints

    Args:
        geo: Country code
        hours: Time period (4, 24, 48, 168)
        limit: Number of results (max ~100)
        enrich: If True, fetch additional data (news, images, related queries)
        output: Optional file path to save results (.json only if enrich=True)
        timeout: Maximum time in seconds for browser operations (default: 60)
        headless: Run browser in headless mode (default: True)

    Returns:
        If enrich=False: [{"keyword": "...", "rank": 1, "traffic": "..."}]
        If enrich=True: {
            "metadata": {"geo": "KR", "hours": 168, ...},
            "trends": [{"keyword": "...", "news": [...], "related": [...]}]
        }

    Raises:
        TrendkitDriverError: If Playwright/browser fails
        TrendkitTimeoutError: If operation times out
        TrendkitValidationError: If parameters are invalid

    Note:
        Requires playwright extra: pip install trendkit[playwright]
        Then run: playwright install chromium

    Example:
        >>> trending_bulk(limit=10, enrich=True, output="trends.json")
    """
    _validate_limit(limit, max_limit=200)

    valid_hours = [4, 24, 48, 168]
    if hours not in valid_hours:
        raise TrendkitValidationError(
            message=f"Invalid hours value: {hours}",
            parameter="hours",
            valid_values=valid_hours
        )

    try:
        from .backends.playwright_backend import PlaywrightBackend
    except ImportError as e:
        raise TrendkitDriverError(
            message="Playwright is not installed",
            suggestion="Install with: pip install trendkit[playwright] && playwright install chromium"
        ) from e

    try:
        backend = PlaywrightBackend(headless=headless)
    except Exception as e:
        raise TrendkitDriverError(
            message=f"Failed to initialize Playwright browser: {e}",
            suggestion="Run: playwright install chromium"
        ) from e

    try:
        data = backend.fetch_trending(geo=geo, hours=hours, limit=limit)
    except Exception as e:
        if "timeout" in str(e).lower():
            raise TrendkitTimeoutError(
                message=f"Browser operation timed out after {timeout}s",
                timeout=timeout
            ) from e
        raise TrendkitAPIError(
            message=f"Failed to fetch trends: {e}",
            suggestion="Check your internet connection and try again"
        ) from e
    finally:
        backend.close()

    if enrich and data:
        data = _enrich_trends(data, geo)
        result = _wrap_with_metadata(data, geo=geo, hours=hours, limit=limit)
    else:
        result = data

    if output and result:
        _save_to_file(result, output, is_enriched=enrich)

    return result


def _enrich_trends(trends: list[dict], geo: str) -> list[dict]:
    """Enrich trend data with news, images, and related queries."""
    from trendspyg import download_google_trends_rss
    import logging

    logger = logging.getLogger(__name__)

    # Get RSS data for news/images (cached lookup)
    rss_data = download_google_trends_rss(
        geo=geo,
        output_format="dict",
        include_images=True,
        include_articles=True,
        max_articles_per_trend=5,
    )

    # Build lookup by keyword
    rss_lookup = {item["trend"]: item for item in (rss_data or [])}

    # Get pytrends backend for related queries
    pytrends = _get_pytrends()

    enriched = []
    for i, trend in enumerate(trends):
        keyword = trend["keyword"]
        logger.info(f"Enriching {i+1}/{len(trends)}: {keyword}")

        # Base data
        item = {
            "keyword": keyword,
            "rank": trend["rank"],
            "traffic": trend["traffic"],
        }

        # Add RSS data (news, images) if available
        if keyword in rss_lookup:
            rss = rss_lookup[keyword]
            item["image"] = rss.get("image", {})
            item["news"] = [
                {
                    "headline": a.get("headline", ""),
                    "url": a.get("url", ""),
                    "source": a.get("source", ""),
                    "image": a.get("image", ""),
                }
                for a in rss.get("news_articles", [])[:5]
            ]
            item["explore_link"] = rss.get("explore_link", "")
        else:
            item["image"] = {}
            item["news"] = []
            item["explore_link"] = f"https://trends.google.com/trends/explore?q={keyword}&geo={geo}"

        # Get related queries (with rate limiting)
        try:
            item["related"] = pytrends.related_queries(keyword, geo=geo, limit=10)
        except Exception as e:
            logger.warning(f"Failed to get related queries for {keyword}: {e}")
            item["related"] = []

        enriched.append(item)

    return enriched


def _wrap_with_metadata(
    trends: list[dict],
    geo: str,
    hours: int,
    limit: int,
) -> dict:
    """Wrap trends data with metadata."""
    from datetime import datetime

    return {
        "metadata": {
            "geo": geo,
            "hours": hours,
            "limit": limit,
            "collected_at": datetime.now().isoformat(),
            "total_items": len(trends),
            "source": "google_trends",
        },
        "trends": trends,
    }


def _save_to_file(data, filepath: str, is_enriched: bool = False) -> None:
    """Save data to CSV or JSON file."""
    import csv
    import json
    from pathlib import Path

    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        if is_enriched:
            # For enriched data, flatten or save as JSON instead
            raise ValueError("Enriched data must be saved as .json (use output='file.json')")
        with open(path, "w", newline="", encoding="utf-8") as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
    elif suffix == ".json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .csv or .json")


# ============================================
# Analysis Functions (via pytrends)
# ============================================

def interest(
    keywords: list[str],
    geo: str = "KR",
    days: int = 7,
    platform: Platform = "web",
) -> dict:
    """
    Get interest over time for keywords.

    Args:
        keywords: Keywords to analyze (max 5)
        geo: Country code
        days: Time period (1, 7, 30, 90, 365)
        platform: Search platform - "web", "youtube", "images", "news", "froogle"

    Returns:
        {
            "dates": ["2024-12-16", "2024-12-17", ...],
            "values": {"BTS": [42, 45, ...]}
        }

    Example:
        >>> interest(["BTS"], days=7)
        {"dates": [...], "values": {"BTS": [42, 45, 38, ...]}}

        >>> interest(["BTS"], days=7, platform="youtube")
        {"dates": [...], "values": {"BTS": [60, 69, ...]}}
    """
    return _get_pytrends().interest_over_time(keywords, geo, days, platform)


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
    platform: Platform = "web",
) -> dict[str, float]:
    """
    Compare keywords by average interest.

    Args:
        keywords: Keywords to compare (max 5)
        geo: Country code
        days: Time period
        platform: Search platform - "web", "youtube", "images", "news", "froogle"

    Returns:
        {"keyword1": 45.6, "keyword2": 14.4}

    Example:
        >>> compare(["삼성", "애플"])
        {"삼성": 45.6, "애플": 14.4}

        >>> compare(["BTS", "BLACKPINK"], platform="youtube")
        {"BTS": 65.2, "BLACKPINK": 48.7}
    """
    return _get_pytrends().compare(keywords, geo, days, platform)


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
