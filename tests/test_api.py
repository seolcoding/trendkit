"""Basic tests for google-trends-api."""

import pytest
from google_trends_api import trending, related, compare, interest, supported_geos


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
    """Tests for related function."""

    def test_related_returns_list(self):
        """related() should return list of strings."""
        result = related("아이폰", limit=5)
        assert isinstance(result, list)
        assert all(isinstance(kw, str) for kw in result)

    def test_related_respects_limit(self):
        """related() should respect limit parameter."""
        result = related("아이폰", limit=3)
        assert len(result) <= 3


class TestCompare:
    """Tests for compare function."""

    def test_compare_returns_dict(self):
        """compare() should return dict with float values."""
        result = compare(["삼성", "애플"])
        assert isinstance(result, dict)
        assert "삼성" in result
        assert "애플" in result
        assert all(isinstance(v, float) for v in result.values())


class TestInterest:
    """Tests for interest function."""

    def test_interest_returns_dict_with_dates_and_values(self):
        """interest() should return dict with dates and values."""
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
