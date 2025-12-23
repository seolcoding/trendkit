"""Tests for backend modules with mocking."""

from unittest.mock import patch, MagicMock
import pytest

from trendkit.backends.rss import RSSBackend
from trendkit.backends.pytrends_backend import PyTrendsBackend


class TestRSSBackend:
    """Tests for RSSBackend."""

    @patch("trendkit.backends.rss.download_google_trends_rss")
    def test_fetch_trending_minimal(self, mock_download):
        """Should return list of keywords for minimal format."""
        mock_download.return_value = [
            {"trend": "keyword1", "traffic": "1000+"},
            {"trend": "keyword2", "traffic": "500+"},
        ]

        result = RSSBackend.fetch_trending(geo="KR", limit=10, format="minimal")

        assert result == ["keyword1", "keyword2"]
        mock_download.assert_called_once()

    @patch("trendkit.backends.rss.download_google_trends_rss")
    def test_fetch_trending_standard(self, mock_download):
        """Should return list of dicts for standard format."""
        mock_download.return_value = [
            {"trend": "keyword1", "traffic": "1000+"},
            {"trend": "keyword2", "traffic": "500+"},
        ]

        result = RSSBackend.fetch_trending(geo="KR", limit=10, format="standard")

        assert len(result) == 2
        assert result[0]["keyword"] == "keyword1"
        assert result[0]["traffic"] == "1000+"

    @patch("trendkit.backends.rss.download_google_trends_rss")
    def test_fetch_trending_full(self, mock_download):
        """Should return full data for full format."""
        from datetime import datetime
        mock_download.return_value = [
            {
                "trend": "keyword1",
                "traffic": "1000+",
                "published": datetime.now(),
                "explore_link": "https://trends.google.com/...",
                "news_articles": [
                    {"headline": "News 1", "source": "Source", "url": "http://..."}
                ],
            },
        ]

        result = RSSBackend.fetch_trending(geo="KR", limit=10, format="full")

        assert len(result) == 1
        assert result[0]["keyword"] == "keyword1"
        assert "news" in result[0]
        assert "explore_link" in result[0]

    @patch("trendkit.backends.rss.download_google_trends_rss")
    def test_fetch_trending_empty(self, mock_download):
        """Should return empty list when no data."""
        mock_download.return_value = None

        result = RSSBackend.fetch_trending(geo="KR", limit=10, format="minimal")

        assert result == []

    @patch("trendkit.backends.rss.download_google_trends_rss")
    def test_fetch_trending_respects_limit(self, mock_download):
        """Should respect limit parameter."""
        mock_download.return_value = [
            {"trend": f"keyword{i}", "traffic": "100+"} for i in range(20)
        ]

        result = RSSBackend.fetch_trending(geo="KR", limit=5, format="minimal")

        assert len(result) == 5

    @patch("trendkit.backends.rss.download_google_trends_rss")
    def test_fetch_trending_passes_geo(self, mock_download):
        """Should pass geo to download function."""
        mock_download.return_value = []

        RSSBackend.fetch_trending(geo="US", limit=10, format="minimal")

        mock_download.assert_called_with(
            geo="US",
            output_format="dict",
            include_images=False,
            include_articles=False,
            max_articles_per_trend=0,
        )

    @patch("trendkit.backends.rss.download_google_trends_rss")
    def test_fetch_trending_includes_images_for_full(self, mock_download):
        """Should include images for full format."""
        mock_download.return_value = []

        RSSBackend.fetch_trending(geo="KR", limit=10, format="full")

        mock_download.assert_called_with(
            geo="KR",
            output_format="dict",
            include_images=True,
            include_articles=True,
            max_articles_per_trend=3,
        )


class TestPyTrendsBackend:
    """Tests for PyTrendsBackend."""

    def test_init(self):
        """Should initialize with default values."""
        backend = PyTrendsBackend()
        assert backend._client is not None

    def test_init_custom_values(self):
        """Should accept custom hl and tz."""
        backend = PyTrendsBackend(hl="en", tz=0)
        assert backend._client is not None

    def test_days_to_timeframe_1_day(self):
        """Should return correct timeframe for 1 day."""
        result = PyTrendsBackend._days_to_timeframe(1)
        assert result == "now 1-d"

    def test_days_to_timeframe_7_days(self):
        """Should return correct timeframe for 7 days."""
        result = PyTrendsBackend._days_to_timeframe(7)
        assert result == "now 7-d"

    def test_days_to_timeframe_30_days(self):
        """Should return correct timeframe for 30 days."""
        result = PyTrendsBackend._days_to_timeframe(30)
        assert result == "today 1-m"

    def test_days_to_timeframe_90_days(self):
        """Should return correct timeframe for 90 days."""
        result = PyTrendsBackend._days_to_timeframe(90)
        assert result == "today 3-m"

    def test_days_to_timeframe_365_days(self):
        """Should return correct timeframe for 365 days."""
        result = PyTrendsBackend._days_to_timeframe(365)
        assert result == "today 12-m"


class TestPyTrendsBackendMocked:
    """Tests for PyTrendsBackend with mocked TrendReq."""

    @patch("trendkit.backends.pytrends_backend.TrendReq")
    def test_interest_over_time(self, mock_trend_req):
        """Should return interest over time data."""
        import pandas as pd

        # Mock the client
        mock_client = MagicMock()
        mock_trend_req.return_value = mock_client

        # Mock interest_over_time response
        df = pd.DataFrame({
            "keyword1": [42, 45, 38],
            "isPartial": [False, False, True],
        }, index=pd.to_datetime(["2024-12-01", "2024-12-02", "2024-12-03"]))
        mock_client.interest_over_time.return_value = df

        backend = PyTrendsBackend()
        result = backend.interest_over_time(["keyword1"], geo="KR", days=7)

        assert "dates" in result
        assert "values" in result
        assert "keyword1" in result["values"]
        assert len(result["values"]["keyword1"]) == 3

    @patch("trendkit.backends.pytrends_backend.TrendReq")
    def test_interest_over_time_empty(self, mock_trend_req):
        """Should handle empty response."""
        import pandas as pd

        mock_client = MagicMock()
        mock_trend_req.return_value = mock_client
        mock_client.interest_over_time.return_value = pd.DataFrame()

        backend = PyTrendsBackend()
        result = backend.interest_over_time(["keyword1"], geo="KR", days=7)

        assert result["dates"] == []
        assert result["values"]["keyword1"] == []

    @patch("trendkit.backends.pytrends_backend.TrendReq")
    def test_related_queries(self, mock_trend_req):
        """Should return related queries."""
        import pandas as pd

        mock_client = MagicMock()
        mock_trend_req.return_value = mock_client

        # Mock related_queries response
        mock_client.related_queries.return_value = {
            "keyword1": {
                "top": pd.DataFrame({"query": ["related1", "related2", "related3"]}),
                "rising": None,
            }
        }

        backend = PyTrendsBackend()
        result = backend.related_queries("keyword1", geo="KR", limit=2)

        assert result == ["related1", "related2"]

    @patch("trendkit.backends.pytrends_backend.TrendReq")
    def test_related_queries_empty(self, mock_trend_req):
        """Should handle empty related queries."""
        mock_client = MagicMock()
        mock_trend_req.return_value = mock_client
        mock_client.related_queries.return_value = {}

        backend = PyTrendsBackend()
        result = backend.related_queries("keyword1", geo="KR", limit=10)

        assert result == []

    @patch("trendkit.backends.pytrends_backend.TrendReq")
    def test_compare(self, mock_trend_req):
        """Should compare keywords."""
        import pandas as pd

        mock_client = MagicMock()
        mock_trend_req.return_value = mock_client

        df = pd.DataFrame({
            "keyword1": [40, 50, 60],
            "keyword2": [20, 30, 40],
        })
        mock_client.interest_over_time.return_value = df

        backend = PyTrendsBackend()
        result = backend.compare(["keyword1", "keyword2"], geo="KR", days=90)

        assert "keyword1" in result
        assert "keyword2" in result
        assert result["keyword1"] == 50.0  # Mean of 40, 50, 60
        assert result["keyword2"] == 30.0  # Mean of 20, 30, 40

    @patch("trendkit.backends.pytrends_backend.TrendReq")
    def test_compare_empty(self, mock_trend_req):
        """Should handle empty compare response."""
        import pandas as pd

        mock_client = MagicMock()
        mock_trend_req.return_value = mock_client
        mock_client.interest_over_time.return_value = pd.DataFrame()

        backend = PyTrendsBackend()
        result = backend.compare(["keyword1", "keyword2"], geo="KR", days=90)

        assert result == {"keyword1": 0.0, "keyword2": 0.0}

    @patch("trendkit.backends.pytrends_backend.TrendReq")
    def test_platform_parameter(self, mock_trend_req):
        """Should pass platform as gprop."""
        mock_client = MagicMock()
        mock_trend_req.return_value = mock_client

        import pandas as pd
        mock_client.interest_over_time.return_value = pd.DataFrame()

        backend = PyTrendsBackend()
        backend.interest_over_time(["keyword"], geo="KR", days=7, platform="youtube")

        # Check gprop was passed
        call_args = mock_client.build_payload.call_args
        assert call_args[1]["gprop"] == "youtube"
