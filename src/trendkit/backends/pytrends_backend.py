"""PyTrends backend for analysis features."""

from typing import Literal, Optional
from pytrends.request import TrendReq

# Platform type for gprop parameter
Platform = Literal["web", "youtube", "images", "news", "froogle"]


class PyTrendsBackend:
    """Analysis features via pytrends (interest, related queries, compare)."""

    def __init__(self, hl: str = "ko", tz: int = 540):
        """
        Initialize PyTrends backend.

        Args:
            hl: Host language (ko, en, ja, etc.)
            tz: Timezone offset in minutes (540 = KST)
        """
        self._client = TrendReq(hl=hl, tz=tz)

    def interest_over_time(
        self,
        keywords: list[str],
        geo: str = "KR",
        days: int = 7,
        platform: Platform = "web",
    ) -> dict:
        """
        Get interest over time for keywords.

        Args:
            keywords: List of keywords to analyze (max 5)
            geo: Country code
            days: Number of days (1, 7, 30, 90, 365)
            platform: Search platform - "web", "youtube", "images", "news", "froogle"

        Returns:
            {
                "dates": ["2024-12-16", "2024-12-17", ...],
                "values": {"keyword1": [42, 45, ...], "keyword2": [...]}
            }
        """
        timeframe = self._days_to_timeframe(days)
        gprop = "" if platform == "web" else platform
        self._client.build_payload(keywords[:5], timeframe=timeframe, geo=geo, gprop=gprop)

        df = self._client.interest_over_time()

        if df.empty:
            return {"dates": [], "values": {kw: [] for kw in keywords}}

        # Drop isPartial column if exists
        if "isPartial" in df.columns:
            df = df.drop(columns=["isPartial"])

        return {
            "dates": [d.strftime("%Y-%m-%d") for d in df.index],
            "values": {col: df[col].tolist() for col in df.columns},
        }

    def related_queries(
        self,
        keyword: str,
        geo: str = "KR",
        days: int = 90,
        limit: int = 10,
    ) -> list[str]:
        """
        Get related queries for a keyword.

        Args:
            keyword: Keyword to find related queries for
            geo: Country code
            days: Number of days
            limit: Maximum number of results

        Returns:
            ["related1", "related2", ...]
        """
        timeframe = self._days_to_timeframe(days)
        self._client.build_payload([keyword], timeframe=timeframe, geo=geo)

        result = self._client.related_queries()

        if not result or keyword not in result:
            return []

        top_queries = result[keyword].get("top")
        if top_queries is None or top_queries.empty:
            return []

        return top_queries["query"].tolist()[:limit]

    def compare(
        self,
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
            days: Number of days
            platform: Search platform - "web", "youtube", "images", "news", "froogle"

        Returns:
            {"keyword1": 45.6, "keyword2": 14.4}
        """
        timeframe = self._days_to_timeframe(days)
        gprop = "" if platform == "web" else platform
        self._client.build_payload(keywords[:5], timeframe=timeframe, geo=geo, gprop=gprop)

        df = self._client.interest_over_time()

        if df.empty:
            return {kw: 0.0 for kw in keywords}

        # Drop isPartial column if exists
        if "isPartial" in df.columns:
            df = df.drop(columns=["isPartial"])

        return {col: round(float(df[col].mean()), 1) for col in df.columns}

    @staticmethod
    def _days_to_timeframe(days: int) -> str:
        """Convert days to pytrends timeframe string."""
        if days <= 1:
            return "now 1-d"
        elif days <= 7:
            return "now 7-d"
        elif days <= 30:
            return "today 1-m"
        elif days <= 90:
            return "today 3-m"
        else:
            return "today 12-m"
