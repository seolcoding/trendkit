"""Basic tests for trendkit."""

from unittest.mock import patch, MagicMock
import pandas as pd
import pytest
from trendkit import trending, related, compare, interest, supported_geos


class TestTrending:
    """Tests for trending function."""

    def test_trending_minimal_returns_list(self):
        """trending() should return list of strings."""
        result = trending(limit=3, format="minimal")
        assert isinstance(result, list)
        assert len(result) <= 3
        assert all(isinstance(kw, str) for kw in result)

    def test_trending_standard_returns_dicts(self):
        """trending(format='standard') should return list of dicts."""
        result = trending(limit=3, format="standard")
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)
        assert all("keyword" in item for item in result)

    def test_trending_respects_limit(self):
        """trending() should respect limit parameter."""
        result = trending(limit=5, format="minimal")
        assert len(result) <= 5


class TestRelated:
    """Tests for related function (mocked to avoid rate limits)."""

    @patch("trendkit.core._get_pytrends")
    def test_related_returns_list(self, mock_get_pytrends):
        """related() should return list of strings."""
        mock_backend = MagicMock()
        mock_get_pytrends.return_value = mock_backend
        mock_backend.related_queries.return_value = ["query1", "query2", "query3"]

        result = related("아이폰", limit=5)
        assert isinstance(result, list)
        assert all(isinstance(kw, str) for kw in result)
        mock_backend.related_queries.assert_called_once()

    @patch("trendkit.core._get_pytrends")
    def test_related_respects_limit(self, mock_get_pytrends):
        """related() should respect limit parameter."""
        mock_backend = MagicMock()
        mock_get_pytrends.return_value = mock_backend
        mock_backend.related_queries.return_value = ["q1", "q2", "q3"]

        result = related("아이폰", limit=3)
        assert len(result) <= 3


class TestCompare:
    """Tests for compare function (mocked to avoid rate limits)."""

    @patch("trendkit.core._get_pytrends")
    def test_compare_returns_dict(self, mock_get_pytrends):
        """compare() should return dict with float values."""
        mock_backend = MagicMock()
        mock_get_pytrends.return_value = mock_backend
        mock_backend.compare.return_value = {"삼성": 45.0, "애플": 55.0}

        result = compare(["삼성", "애플"])
        assert isinstance(result, dict)
        assert "삼성" in result
        assert "애플" in result
        assert all(isinstance(v, float) for v in result.values())


class TestInterest:
    """Tests for interest function (mocked to avoid rate limits)."""

    @patch("trendkit.core._get_pytrends")
    def test_interest_returns_dict_with_dates_and_values(self, mock_get_pytrends):
        """interest() should return dict with dates and values."""
        mock_backend = MagicMock()
        mock_get_pytrends.return_value = mock_backend
        mock_backend.interest_over_time.return_value = {
            "dates": ["2024-12-01", "2024-12-02"],
            "values": {"BTS": [42, 45]}
        }

        result = interest(["BTS"], days=7)
        assert isinstance(result, dict)
        assert "dates" in result
        assert "values" in result
        assert isinstance(result["dates"], list)
        assert isinstance(result["values"], dict)


class TestSupportedGeos:
    """Tests for supported_geos function."""

    def test_supported_geos_returns_list(self):
        """supported_geos() should return list of country codes."""
        result = supported_geos()
        assert isinstance(result, list)
        assert "KR" in result
        assert "US" in result
