"""Tests for validation in core functions."""

import pytest
from trendkit import trending, TrendkitValidationError


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
