"""
trendkit - Multi-platform trend aggregator optimized for LLM tool calls.

Supported platforms:
- Google Trends (realtime, analysis)

Quick Start:
    >>> from trendkit import trending, related, compare
    >>> trending(limit=5)
    ['환율', '신한카드', '국민신문고', ...]

    >>> related("아이폰", limit=5)
    ['아이폰 17', '아이폰 디시', ...]

    >>> compare(["삼성", "애플"])
    {"삼성": 45.6, "애플": 14.4}

    # YouTube keyword interest (via Google Trends)
    >>> interest(["BTS"], platform="youtube")
    {"dates": [...], "values": {"BTS": [60, 69, ...]}}

Caching:
    >>> trending(limit=5, cache=True, ttl=60)  # Cache for 60 seconds

    >>> from trendkit import cache
    >>> cache.clear()  # Clear all cached data
    >>> cache.stats()  # Get cache statistics

Error Handling:
    >>> from trendkit import TrendkitError, TrendkitRateLimitError
    >>> try:
    ...     trending(limit=5)
    ... except TrendkitRateLimitError as e:
    ...     print(f"Rate limited. Retry after {e.retry_after}s")
"""

from .core import (
    # Realtime trending
    trending,
    trending_bulk,
    # Analysis
    interest,
    related,
    compare,
    # Utility
    supported_geos,
)

from .types import Format
from .backends.pytrends_backend import Platform

# Cache module
from . import cache

# Exceptions
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

__version__ = "0.1.0"

__all__ = [
    # Google Trends
    "trending",
    "trending_bulk",
    "interest",
    "related",
    "compare",
    # Utility
    "supported_geos",
    # Types
    "Format",
    "Platform",
    # Cache
    "cache",
    # Exceptions
    "TrendkitError",
    "TrendkitAPIError",
    "TrendkitRateLimitError",
    "TrendkitTimeoutError",
    "TrendkitServiceError",
    "TrendkitDriverError",
    "TrendkitValidationError",
    "RetryConfig",
]
