"""
Google Trends API - Lightweight wrapper optimized for LLM tool calls.

Quick Start:
    >>> from google_trends_api import trending, related, compare
    >>> trending(limit=5)
    ['환율', '신한카드', '국민신문고', ...]

    >>> related("아이폰", limit=5)
    ['아이폰 17', '아이폰 디시', ...]

    >>> compare(["삼성", "애플"])
    {"삼성": 45.6, "애플": 14.4}
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

__version__ = "0.1.0"

__all__ = [
    # Functions
    "trending",
    "trending_bulk",
    "interest",
    "related",
    "compare",
    "supported_geos",
    # Types
    "Format",
]
