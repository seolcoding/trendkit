"""RSS backend using trendspyg for fast realtime trends."""

from typing import Any
from trendspyg import download_google_trends_rss

from ..types import Format


class RSSBackend:
    """Fast realtime trends via Google Trends RSS feed."""

    @staticmethod
    def fetch_trending(
        geo: str = "KR",
        limit: int = 10,
        format: Format = "minimal",
    ) -> list[str] | list[dict]:
        """
        Fetch realtime trending keywords.

        Args:
            geo: Country code (KR, US, JP, etc.)
            limit: Maximum number of results (max 20 from RSS)
            format: Output format for token optimization
                - minimal: ["keyword1", "keyword2", ...]
                - standard: [{"keyword": "...", "traffic": "..."}, ...]
                - full: [{"keyword": "...", "traffic": "...", "news": [...], ...}]

        Returns:
            List of trending keywords or dicts based on format.
        """
        raw_data = download_google_trends_rss(
            geo=geo,
            output_format="dict",
            include_images=format == "full",
            include_articles=format in ("standard", "full"),
            max_articles_per_trend=3 if format == "full" else 0,
        )

        if not raw_data:
            return []

        # Apply limit
        raw_data = raw_data[:limit]

        # Format output based on token optimization level
        if format == "minimal":
            return [item["trend"] for item in raw_data]

        elif format == "standard":
            return [
                {
                    "keyword": item["trend"],
                    "traffic": item.get("traffic", "N/A"),
                }
                for item in raw_data
            ]

        else:  # full
            return [
                {
                    "keyword": item["trend"],
                    "traffic": item.get("traffic", "N/A"),
                    "published": item.get("published", "").isoformat() if item.get("published") else None,
                    "explore_link": item.get("explore_link", ""),
                    "news": [
                        {
                            "headline": article.get("headline", ""),
                            "source": article.get("source", ""),
                            "url": article.get("url", ""),
                        }
                        for article in item.get("news_articles", [])[:3]
                    ],
                }
                for item in raw_data
            ]
