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
]
