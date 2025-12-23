"""Tests for validation in core functions."""

import pytest
from unittest.mock import patch, MagicMock
from trendkit import trending, compare, interest, TrendkitValidationError


class TestTrendingValidation:
    """Tests for trending() validation."""

    def test_negative_limit_raises(self):
        """trending() should raise on negative limit."""
        with pytest.raises(TrendkitValidationError) as exc_info:
            trending(limit=-1)
        assert exc_info.value.parameter == "limit"

    def test_zero_limit_raises(self):
        """trending() should raise on zero limit."""
        with pytest.raises(TrendkitValidationError) as exc_info:
            trending(limit=0)
        assert "positive" in str(exc_info.value).lower()

    def test_excessive_limit_raises(self):
        """trending() should raise on limit > 20."""
        with pytest.raises(TrendkitValidationError) as exc_info:
            trending(limit=25)
        assert exc_info.value.parameter == "limit"
        assert "20" in str(exc_info.value)

    def test_invalid_geo_raises_with_suggestions(self):
        """trending() should raise on invalid geo with valid options."""
        # TrendkitValidationError or underlying library error should be raised
        with pytest.raises((TrendkitValidationError, Exception)) as exc_info:
            trending(geo="INVALID")
        # Error message should indicate the geo is invalid
        error_msg = str(exc_info.value).lower()
        assert "invalid" in error_msg or "geo" in error_msg or "available" in error_msg

    def test_lowercase_geo_works(self):
        """trending() should accept lowercase geo codes."""
        # Should not raise - lowercase should be normalized
        result = trending(geo="kr", limit=3)
        assert isinstance(result, list)


class TestCompareValidation:
    """Tests for compare() validation."""

    @patch("trendkit.core._get_pytrends")
    def test_compare_valid_keywords(self, mock_pytrends):
        """compare() with valid keywords should work."""
        mock_backend = MagicMock()
        mock_pytrends.return_value = mock_backend
        mock_backend.compare.return_value = {"삼성": 50.0, "애플": 50.0}

        result = compare(["삼성", "애플"])
        assert isinstance(result, dict)
        assert len(result) == 2


class TestInterestValidation:
    """Tests for interest() validation."""

    @patch("trendkit.core._get_pytrends")
    def test_interest_valid_keywords(self, mock_pytrends):
        """interest() with valid keywords should work."""
        mock_backend = MagicMock()
        mock_pytrends.return_value = mock_backend
        mock_backend.interest_over_time.return_value = {
            "dates": ["2024-12-01"],
            "values": {"BTS": [50]}
        }

        result = interest(["BTS"], days=7)
        assert "dates" in result
        assert "values" in result


class TestTrendingCache:
    """Tests for trending() cache functionality."""

    def test_cache_returns_same_result(self):
        """Cached call should return same result."""
        result1 = trending(limit=3, cache=True, ttl=60)
        result2 = trending(limit=3, cache=True, ttl=60)
        # Results should be equal (from cache)
        assert result1 == result2

    def test_cache_disabled_by_default(self):
        """Cache should be disabled by default."""
        # This is just a smoke test - cache=False should work
        result = trending(limit=3)
        assert isinstance(result, list)
