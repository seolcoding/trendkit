"""Type definitions for google-trends-api."""

from typing import Literal, TypedDict

# Output format for token optimization
Format = Literal["minimal", "standard", "full"]

# Time periods
Hours = Literal[4, 24, 48, 168]
Days = Literal[1, 7, 30, 90, 365]

# Geo codes
Geo = str  # e.g., "KR", "US", "JP"


class TrendMinimal(TypedDict):
    """Minimal trend data (~10 tokens per item)."""
    keyword: str


class TrendStandard(TypedDict):
    """Standard trend data (~30 tokens per item)."""
    keyword: str
    traffic: str  # e.g., "5000+"


class TrendFull(TypedDict):
    """Full trend data (~100+ tokens per item)."""
    keyword: str
    traffic: str
    published: str
    explore_link: str
    news: list[dict]


class InterestData(TypedDict):
    """Interest over time data."""
    dates: list[str]
    values: dict[str, list[int]]


class CompareResult(TypedDict):
    """Keyword comparison result."""
    averages: dict[str, float]
    period: str
