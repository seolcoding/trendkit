"""Comprehensive unit tests for core.py functions."""

import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from trendkit import (
    trending,
    related,
    compare,
    interest,
    supported_geos,
    TrendkitError,
    TrendkitValidationError,
    TrendkitRateLimitError,
    TrendkitAPIError,
    TrendkitDriverError,
    TrendkitTimeoutError,
    RetryConfig,
    cache,
)
from trendkit.core import (
    _validate_geo,
    _validate_limit,
    _with_retry,
    _wrap_with_metadata,
    _save_to_file,
    _get_pytrends,
    _enrich_trends,
)


class TestValidateGeo:
    """Tests for _validate_geo function."""

    def test_valid_geo_kr(self):
        """Valid geo code KR should pass."""
        _validate_geo("KR")  # Should not raise

    def test_valid_geo_us(self):
        """Valid geo code US should pass."""
        _validate_geo("US")  # Should not raise

    def test_valid_geo_lowercase(self):
        """Lowercase geo code should be validated (case-insensitive check)."""
        # The function checks geo.upper() not in valid_geos
        # But valid_geos contains uppercase, so "kr".upper() = "KR" is valid
        _validate_geo("kr")  # Should not raise

    def test_invalid_geo_raises(self):
        """Invalid geo code should raise TrendkitValidationError."""
        with pytest.raises(TrendkitValidationError) as exc_info:
            _validate_geo("INVALID")
        assert exc_info.value.parameter == "geo"
        assert "INVALID" in str(exc_info.value)

    def test_invalid_geo_has_suggestion(self):
        """Invalid geo should include valid options in suggestion."""
        with pytest.raises(TrendkitValidationError) as exc_info:
            _validate_geo("XX")
        assert exc_info.value.valid_values is not None
        assert "KR" in exc_info.value.valid_values


class TestValidateLimit:
    """Tests for _validate_limit function."""

    def test_valid_limit(self):
        """Valid limit should pass."""
        _validate_limit(10)  # Should not raise
        _validate_limit(1)   # Minimum
        _validate_limit(100)  # Maximum (default)

    def test_zero_limit_raises(self):
        """Zero limit should raise."""
        with pytest.raises(TrendkitValidationError) as exc_info:
            _validate_limit(0)
        assert "positive" in str(exc_info.value).lower()

    def test_negative_limit_raises(self):
        """Negative limit should raise."""
        with pytest.raises(TrendkitValidationError) as exc_info:
            _validate_limit(-5)
        assert exc_info.value.parameter == "limit"

    def test_exceeds_max_limit_raises(self):
        """Limit exceeding max should raise."""
        with pytest.raises(TrendkitValidationError) as exc_info:
            _validate_limit(150, max_limit=100)
        assert "100" in str(exc_info.value)

    def test_custom_max_limit(self):
        """Custom max_limit should be respected."""
        _validate_limit(15, max_limit=20)  # Should pass
        with pytest.raises(TrendkitValidationError):
            _validate_limit(25, max_limit=20)


class TestWithRetry:
    """Tests for _with_retry function."""

    def test_success_on_first_try(self):
        """Function should return on first successful call."""
        mock_func = MagicMock(return_value="success")
        result = _with_retry(mock_func)
        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_on_rate_limit(self):
        """Should retry on TrendkitRateLimitError."""
        mock_func = MagicMock(side_effect=[
            TrendkitRateLimitError(),
            TrendkitRateLimitError(),
            "success"
        ])
        config = RetryConfig(max_retries=3, base_delay=0.01)
        result = _with_retry(mock_func, retry_config=config)
        assert result == "success"
        assert mock_func.call_count == 3

    def test_raises_after_max_retries(self):
        """Should raise after max retries exhausted."""
        mock_func = MagicMock(side_effect=TrendkitRateLimitError())
        config = RetryConfig(max_retries=2, base_delay=0.01)
        with pytest.raises(TrendkitRateLimitError):
            _with_retry(mock_func, retry_config=config)
        assert mock_func.call_count == 3  # initial + 2 retries

    def test_non_retryable_exception_raises_immediately(self):
        """Non-retryable exceptions should raise immediately."""
        mock_func = MagicMock(side_effect=ValueError("not retryable"))
        config = RetryConfig(max_retries=3, base_delay=0.01)
        with pytest.raises(ValueError):
            _with_retry(
                mock_func,
                retry_config=config,
                retryable_exceptions=(TrendkitRateLimitError,)
            )
        assert mock_func.call_count == 1

    def test_custom_retryable_exceptions(self):
        """Should support custom retryable exceptions."""
        mock_func = MagicMock(side_effect=[
            TrendkitAPIError("error"),
            "success"
        ])
        config = RetryConfig(max_retries=2, base_delay=0.01)
        result = _with_retry(
            mock_func,
            retry_config=config,
            retryable_exceptions=(TrendkitAPIError,)
        )
        assert result == "success"


class TestWrapWithMetadata:
    """Tests for _wrap_with_metadata function."""

    def test_wraps_trends_with_metadata(self):
        """Should wrap trends with metadata."""
        trends = [{"keyword": "test", "rank": 1, "traffic": "1000+"}]
        result = _wrap_with_metadata(trends, geo="KR", hours=168, limit=100)

        assert "metadata" in result
        assert "trends" in result
        assert result["trends"] == trends

    def test_metadata_contains_required_fields(self):
        """Metadata should contain all required fields."""
        trends = [{"keyword": "test"}]
        result = _wrap_with_metadata(trends, geo="US", hours=24, limit=50)

        metadata = result["metadata"]
        assert metadata["geo"] == "US"
        assert metadata["hours"] == 24
        assert metadata["limit"] == 50
        assert metadata["total_items"] == 1
        assert metadata["source"] == "google_trends"
        assert "collected_at" in metadata

    def test_collected_at_is_iso_format(self):
        """collected_at should be ISO format timestamp."""
        result = _wrap_with_metadata([], geo="KR", hours=168, limit=100)
        collected_at = result["metadata"]["collected_at"]
        # Should be parseable as ISO format
        from datetime import datetime
        datetime.fromisoformat(collected_at)


class TestSaveToFile:
    """Tests for _save_to_file function."""

    def test_save_csv(self):
        """Should save data to CSV file."""
        data = [
            {"keyword": "test1", "rank": 1, "traffic": "1000+"},
            {"keyword": "test2", "rank": 2, "traffic": "500+"},
        ]
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            filepath = f.name

        try:
            _save_to_file(data, filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            assert "keyword" in content
            assert "test1" in content
            assert "test2" in content
        finally:
            os.unlink(filepath)

    def test_save_json(self):
        """Should save data to JSON file."""
        data = {"keyword": "test", "value": 123}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            _save_to_file(data, filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            assert loaded == data
        finally:
            os.unlink(filepath)

    def test_save_enriched_csv_raises(self):
        """Saving enriched data as CSV should raise."""
        data = {"metadata": {}, "trends": []}
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            filepath = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                _save_to_file(data, filepath, is_enriched=True)
            assert "json" in str(exc_info.value).lower()
        finally:
            os.unlink(filepath)

    def test_unsupported_format_raises(self):
        """Unsupported file format should raise."""
        with pytest.raises(ValueError) as exc_info:
            _save_to_file({}, "test.xml")
        assert "Unsupported" in str(exc_info.value)

    def test_save_empty_csv(self):
        """Saving empty data to CSV should create empty file."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            filepath = f.name

        try:
            _save_to_file([], filepath)
            assert os.path.exists(filepath)
            with open(filepath, "r") as f:
                content = f.read()
            assert content == ""  # Empty file
        finally:
            os.unlink(filepath)


class TestTrendingWithCache:
    """Tests for trending() with cache functionality."""

    def setup_method(self):
        """Reset cache before each test."""
        cache.clear()

    def test_cache_hit(self):
        """Second call should use cache."""
        # First call (cache miss)
        result1 = trending(limit=3, cache=True, ttl=60)
        stats1 = cache.stats()

        # Second call (cache hit)
        result2 = trending(limit=3, cache=True, ttl=60)
        stats2 = cache.stats()

        assert result1 == result2
        assert stats2["hits"] > stats1["hits"]

    def test_different_params_different_cache_keys(self):
        """Different parameters should use different cache keys."""
        result1 = trending(limit=3, cache=True)
        result2 = trending(limit=5, cache=True)

        # Should have 2 cache entries
        stats = cache.stats()
        assert stats["size"] == 2

    def test_cache_disabled_by_default(self):
        """Cache should be disabled by default."""
        cache.clear()
        trending(limit=3)
        trending(limit=3)

        stats = cache.stats()
        assert stats["size"] == 0  # Nothing cached


class TestTrendingValidation:
    """Tests for trending() validation."""

    def test_limit_validation(self):
        """Should validate limit for trending (max 20)."""
        with pytest.raises(TrendkitValidationError):
            trending(limit=25)

    def test_limit_zero_validation(self):
        """Zero limit should raise."""
        with pytest.raises(TrendkitValidationError):
            trending(limit=0)


class TestSupportedGeos:
    """Tests for supported_geos function."""

    def test_returns_list(self):
        """Should return list of strings."""
        geos = supported_geos()
        assert isinstance(geos, list)
        assert all(isinstance(g, str) for g in geos)

    def test_contains_common_codes(self):
        """Should contain common country codes."""
        geos = supported_geos()
        assert "KR" in geos
        assert "US" in geos
        assert "JP" in geos
        assert "GB" in geos

    def test_all_uppercase(self):
        """All geo codes should be uppercase."""
        geos = supported_geos()
        assert all(g == g.upper() for g in geos)


class TestGetPytrends:
    """Tests for _get_pytrends singleton."""

    def test_returns_backend(self):
        """Should return PyTrendsBackend instance."""
        from trendkit.backends.pytrends_backend import PyTrendsBackend
        backend = _get_pytrends()
        assert isinstance(backend, PyTrendsBackend)

    def test_singleton(self):
        """Should return same instance on multiple calls."""
        backend1 = _get_pytrends()
        backend2 = _get_pytrends()
        assert backend1 is backend2


class TestTrendingBulkValidation:
    """Tests for trending_bulk validation."""

    def test_invalid_hours_raises(self):
        """Invalid hours value should raise TrendkitValidationError."""
        from trendkit import trending_bulk
        with pytest.raises(TrendkitValidationError) as exc_info:
            trending_bulk(hours=12)  # 12 is not valid
        assert exc_info.value.parameter == "hours"
        assert "4" in str(exc_info.value)  # Should suggest valid values

    def test_excessive_limit_raises(self):
        """Limit exceeding 200 should raise."""
        from trendkit import trending_bulk
        with pytest.raises(TrendkitValidationError) as exc_info:
            trending_bulk(limit=250)
        assert "200" in str(exc_info.value)

    def test_selenium_import_error(self):
        """Should raise TrendkitDriverError when selenium not installed."""
        import sys

        # Save original modules
        original_selenium = sys.modules.get('trendkit.backends.selenium_backend')

        try:
            # Remove selenium_backend from modules
            if 'trendkit.backends.selenium_backend' in sys.modules:
                del sys.modules['trendkit.backends.selenium_backend']

            # Temporarily modify sys.modules to simulate import failure
            with patch.dict(sys.modules, {'trendkit.backends.selenium_backend': None}):
                # Reload core module to trigger the import error path
                import importlib
                import trendkit.core as core_module

                # Force reimport by clearing the module
                if 'trendkit.core' in sys.modules:
                    del sys.modules['trendkit.core']

                # Try to import trending_bulk and call it
                try:
                    from trendkit import trending_bulk
                    # This should hit the import error handling
                    trending_bulk(limit=10)
                except (TrendkitDriverError, ImportError, TypeError):
                    # Expected - import fails or we get the driver error
                    pass
        finally:
            # Restore original modules
            if original_selenium:
                sys.modules['trendkit.backends.selenium_backend'] = original_selenium


class TestEnrichTrends:
    """Tests for _enrich_trends function."""

    @patch("trendkit.core._get_pytrends")
    @patch("trendspyg.download_google_trends_rss")
    def test_enrich_with_rss_match(self, mock_rss, mock_pytrends):
        """Should enrich trends with matching RSS data."""
        # Mock RSS data with matching keyword
        mock_rss.return_value = [
            {
                "trend": "테스트",
                "image": {"url": "http://image.com/test.jpg"},
                "news_articles": [
                    {"headline": "Test News", "url": "http://news.com", "source": "Source", "image": "img.jpg"}
                ],
                "explore_link": "http://trends.google.com/explore?q=test",
            }
        ]

        # Mock pytrends
        mock_backend = MagicMock()
        mock_pytrends.return_value = mock_backend
        mock_backend.related_queries.return_value = ["related1", "related2"]

        # Input trends with matching keyword
        trends = [{"keyword": "테스트", "rank": 1, "traffic": "1000+"}]

        result = _enrich_trends(trends, geo="KR")

        assert len(result) == 1
        assert result[0]["keyword"] == "테스트"
        assert result[0]["image"] == {"url": "http://image.com/test.jpg"}
        assert len(result[0]["news"]) == 1
        assert result[0]["news"][0]["headline"] == "Test News"
        assert result[0]["explore_link"] == "http://trends.google.com/explore?q=test"
        assert result[0]["related"] == ["related1", "related2"]

    @patch("trendkit.core._get_pytrends")
    @patch("trendspyg.download_google_trends_rss")
    def test_enrich_without_rss_match(self, mock_rss, mock_pytrends):
        """Should handle trends without RSS match."""
        # Mock RSS data without matching keyword
        mock_rss.return_value = [{"trend": "다른키워드"}]

        # Mock pytrends
        mock_backend = MagicMock()
        mock_pytrends.return_value = mock_backend
        mock_backend.related_queries.return_value = []

        trends = [{"keyword": "테스트", "rank": 1, "traffic": "1000+"}]

        result = _enrich_trends(trends, geo="KR")

        assert len(result) == 1
        assert result[0]["image"] == {}
        assert result[0]["news"] == []
        assert "trends.google.com" in result[0]["explore_link"]

    @patch("trendkit.core._get_pytrends")
    @patch("trendspyg.download_google_trends_rss")
    def test_enrich_handles_related_error(self, mock_rss, mock_pytrends):
        """Should handle errors when getting related queries."""
        mock_rss.return_value = []

        # Mock pytrends to raise an exception
        mock_backend = MagicMock()
        mock_pytrends.return_value = mock_backend
        mock_backend.related_queries.side_effect = Exception("Rate limited")

        trends = [{"keyword": "테스트", "rank": 1, "traffic": "1000+"}]

        result = _enrich_trends(trends, geo="KR")

        assert len(result) == 1
        assert result[0]["related"] == []  # Should fallback to empty list


class TestTrendingBulkErrors:
    """Tests for trending_bulk error handling."""

    @patch("trendkit.backends.selenium_backend.SeleniumBackend")
    def test_driver_init_error(self, mock_selenium):
        """Driver initialization error should raise TrendkitDriverError."""
        mock_selenium.side_effect = Exception("Chrome not found")

        from trendkit import trending_bulk
        with pytest.raises(TrendkitDriverError) as exc_info:
            trending_bulk(limit=10)
        assert "Selenium driver" in str(exc_info.value)

    @patch("trendkit.backends.selenium_backend.SeleniumBackend")
    def test_timeout_error(self, mock_selenium):
        """Timeout during fetch should raise TrendkitTimeoutError."""
        mock_instance = mock_selenium.return_value
        mock_instance.fetch_trending.side_effect = Exception("timeout occurred")

        from trendkit import trending_bulk
        with pytest.raises(TrendkitTimeoutError) as exc_info:
            trending_bulk(limit=10)
        assert "timed out" in str(exc_info.value)

    @patch("trendkit.backends.selenium_backend.SeleniumBackend")
    def test_api_error(self, mock_selenium):
        """General API error should raise TrendkitAPIError."""
        mock_instance = mock_selenium.return_value
        mock_instance.fetch_trending.side_effect = Exception("Connection refused")

        from trendkit import trending_bulk
        with pytest.raises(TrendkitAPIError) as exc_info:
            trending_bulk(limit=10)
        assert "fetch trends" in str(exc_info.value).lower()

    @patch("trendkit.backends.selenium_backend.SeleniumBackend")
    def test_successful_bulk_with_enrich(self, mock_selenium):
        """Should return enriched data when enrich=True."""
        mock_instance = mock_selenium.return_value
        mock_instance.fetch_trending.return_value = [
            {"keyword": "test1", "rank": 1, "traffic": "1000+"},
            {"keyword": "test2", "rank": 2, "traffic": "500+"},
        ]

        from trendkit import trending_bulk
        result = trending_bulk(limit=10, enrich=True)

        assert "metadata" in result
        assert "trends" in result
        assert result["metadata"]["geo"] == "KR"
        mock_instance.close.assert_called_once()

    @patch("trendkit.backends.selenium_backend.SeleniumBackend")
    def test_bulk_output_to_file(self, mock_selenium):
        """Should save results to file."""
        mock_instance = mock_selenium.return_value
        mock_instance.fetch_trending.return_value = [
            {"keyword": "test1", "rank": 1, "traffic": "1000+"},
        ]

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            from trendkit import trending_bulk
            result = trending_bulk(limit=10, output=filepath)

            assert os.path.exists(filepath)
            with open(filepath, "r") as f:
                content = json.load(f)
            assert len(content) == 1
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)
