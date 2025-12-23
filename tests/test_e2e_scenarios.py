"""End-to-end user scenario tests.

These tests simulate real user workflows and integration scenarios.
They test the complete flow from API call to result.
"""

import json
import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from trendkit import (
    trending,
    related,
    compare,
    interest,
    supported_geos,
    cache,
    TrendkitError,
    TrendkitValidationError,
)


class TestNewsBotScenario:
    """Scenario: AI News Bot that fetches trending topics and expands them."""

    @patch("trendkit.core._get_pytrends")
    def test_fetch_trending_and_expand(self, mock_get_pytrends):
        """News bot fetches trends and gets related queries."""
        # Mock related queries
        mock_backend = MagicMock()
        mock_get_pytrends.return_value = mock_backend
        mock_backend.related_queries.return_value = ["related1", "related2"]

        # Step 1: Get trending topics (minimal for token efficiency)
        topics = trending(limit=3, format="minimal")
        assert isinstance(topics, list)
        assert len(topics) <= 3

        # Step 2: For each topic, get related queries to expand coverage
        all_related = {}
        for topic in topics[:2]:  # Limit to 2 to avoid rate limits
            related_queries = related(topic, limit=3)
            all_related[topic] = related_queries

        # Verify we got related queries
        assert len(all_related) > 0

    def test_cache_reduces_api_calls(self):
        """Cache should reduce redundant API calls."""
        cache.clear()

        # First call - cache miss
        result1 = trending(limit=3, cache=True, ttl=60)
        stats1 = cache.stats()

        # Second call - should hit cache
        result2 = trending(limit=3, cache=True, ttl=60)
        stats2 = cache.stats()

        # Results should be identical
        assert result1 == result2

        # Cache hit count should increase
        assert stats2["hits"] > stats1["hits"]


class TestContentRecommendationScenario:
    """Scenario: Content recommendation system comparing topic popularity."""

    @patch("trendkit.core._get_pytrends")
    def test_compare_topics_for_recommendation(self, mock_get_pytrends):
        """Compare topics to recommend the most popular one."""
        mock_backend = MagicMock()
        mock_get_pytrends.return_value = mock_backend
        mock_backend.compare.return_value = {"삼성": 45.0, "애플": 55.0}

        # Compare related topics
        topics = ["삼성", "애플"]
        scores = compare(topics)

        assert isinstance(scores, dict)
        assert all(topic in scores for topic in topics)
        assert all(isinstance(v, float) for v in scores.values())

        # Find most popular
        most_popular = max(scores, key=scores.get)
        assert most_popular in topics

    @patch("trendkit.core._get_pytrends")
    def test_youtube_vs_web_interest(self, mock_get_pytrends):
        """Compare interest across platforms."""
        mock_backend = MagicMock()
        mock_get_pytrends.return_value = mock_backend
        mock_backend.interest_over_time.return_value = {
            "dates": ["2024-12-01", "2024-12-02"],
            "values": {"BTS": [42, 45]}
        }

        keyword = "BTS"

        # Web interest
        web_data = interest([keyword], days=7, platform="web")
        assert "values" in web_data
        assert keyword in web_data["values"]

        # YouTube interest
        youtube_data = interest([keyword], days=7, platform="youtube")
        assert "values" in youtube_data
        assert keyword in youtube_data["values"]


class TestMarketingAnalysisScenario:
    """Scenario: Marketing team analyzing trend data."""

    @patch("trendkit.core._get_pytrends")
    def test_analyze_interest_over_time(self, mock_get_pytrends):
        """Analyze how interest changes over time."""
        mock_backend = MagicMock()
        mock_get_pytrends.return_value = mock_backend
        mock_backend.interest_over_time.return_value = {
            "dates": ["2024-12-01", "2024-12-02", "2024-12-03"],
            "values": {"BTS": [30, 50, 40]}
        }

        keywords = ["BTS"]
        data = interest(keywords, days=7)

        assert "dates" in data
        assert "values" in data
        assert len(data["dates"]) > 0

        # Calculate simple metrics
        for kw in keywords:
            values = data["values"].get(kw, [])
            if values:
                avg = sum(values) / len(values)
                max_val = max(values)
                min_val = min(values)
                assert max_val >= avg >= min_val

    def test_multi_geo_comparison(self):
        """Compare trends across different regions."""
        geos = supported_geos()
        assert "KR" in geos
        assert "US" in geos

        # Compare same keyword in different regions
        kr_result = trending(geo="KR", limit=3, format="minimal")
        us_result = trending(geo="US", limit=3, format="minimal")

        # Both should return results
        assert isinstance(kr_result, list)
        assert isinstance(us_result, list)


class TestErrorHandlingScenario:
    """Scenario: Graceful error handling in production."""

    def test_validation_error_is_helpful(self):
        """Validation errors should provide helpful suggestions."""
        with pytest.raises(TrendkitValidationError) as exc_info:
            trending(limit=-1)

        error = exc_info.value
        assert error.suggestion is not None or error.parameter is not None

    def test_invalid_limit_provides_guidance(self):
        """Invalid limit should explain the maximum."""
        with pytest.raises(TrendkitValidationError) as exc_info:
            trending(limit=100)  # Max is 20 for trending

        assert "20" in str(exc_info.value)

    def test_all_errors_inherit_from_base(self):
        """All errors should be catchable with base exception."""
        try:
            trending(limit=-1)
        except TrendkitError as e:
            assert isinstance(e, TrendkitValidationError)


class TestTokenOptimizationScenario:
    """Scenario: Verify token optimization across formats."""

    def test_minimal_format_is_smallest(self):
        """Minimal format should produce smallest output."""
        minimal = trending(limit=5, format="minimal")
        standard = trending(limit=5, format="standard")

        # Minimal is list of strings
        assert all(isinstance(item, str) for item in minimal)

        # Standard is list of dicts
        assert all(isinstance(item, dict) for item in standard)

        # Minimal should have less data
        minimal_size = len(json.dumps(minimal))
        standard_size = len(json.dumps(standard))
        assert minimal_size < standard_size

    def test_format_comparison(self):
        """Compare all three formats."""
        minimal = trending(limit=3, format="minimal")
        standard = trending(limit=3, format="standard")
        full = trending(limit=3, format="full")

        # Minimal: list of strings
        assert isinstance(minimal[0], str) if minimal else True

        # Standard: dict with keyword and traffic
        if standard:
            assert "keyword" in standard[0]
            assert "traffic" in standard[0]

        # Full: dict with additional fields
        if full:
            assert "keyword" in full[0]
            # Full should have more fields than standard
            assert len(full[0].keys()) >= len(standard[0].keys()) if standard else True


class TestDataExportScenario:
    """Scenario: Exporting trend data for analysis."""

    @patch("trendkit.backends.playwright_backend.PlaywrightBackend")
    def test_csv_export_workflow(self, mock_playwright):
        """Export trends to CSV file."""
        # Mock the playwright backend
        mock_instance = mock_playwright.return_value
        mock_instance.fetch_trending.return_value = [
            {"keyword": "test1", "rank": 1, "traffic": "1000+"},
            {"keyword": "test2", "rank": 2, "traffic": "500+"},
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            filepath = f.name

        try:
            from trendkit import trending_bulk
            result = trending_bulk(limit=10, output=filepath)

            # File should exist
            assert os.path.exists(filepath)

            # Read and verify content
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            assert "keyword" in content
            assert "test1" in content
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestCacheWorkflowScenario:
    """Scenario: Using cache effectively in repeated queries."""

    def setup_method(self):
        """Reset cache before each test."""
        cache.clear()

    def test_cache_workflow(self):
        """Complete cache workflow: configure, use, stats, clear."""
        # Configure cache
        cache.configure(max_size=100, default_ttl=60)

        # Make cached requests
        trending(limit=3, cache=True)
        trending(limit=3, cache=True)  # Should hit cache
        trending(limit=5, cache=True)  # Different params, new entry

        # Check stats
        stats = cache.stats()
        assert stats["hits"] >= 1
        assert stats["size"] >= 1

        # Clear cache
        cleared = cache.clear()
        assert cleared >= 1

        # Verify cleared
        stats_after = cache.stats()
        assert stats_after["size"] == 0

    def test_cache_ttl_expiration(self):
        """Cache entries should expire after TTL."""
        import time

        # Use very short TTL
        trending(limit=3, cache=True, ttl=1)

        stats1 = cache.stats()
        assert stats1["size"] == 1

        # Wait for TTL to expire
        time.sleep(1.5)

        # Cleanup expired entries
        expired = cache.cleanup()
        assert expired >= 1


class TestSupportedGeosScenario:
    """Scenario: Working with different geographic regions."""

    def test_all_geos_are_valid(self):
        """All returned geos should work with trending."""
        geos = supported_geos()

        # Test a few geos
        for geo in geos[:3]:
            result = trending(geo=geo, limit=2, format="minimal")
            assert isinstance(result, list)

    def test_geo_variety(self):
        """Should support diverse geographic regions."""
        geos = supported_geos()

        # Check for regional diversity
        asia = ["KR", "JP", "TW", "HK", "SG"]
        europe = ["GB", "DE", "FR", "ES", "IT"]
        americas = ["US", "CA", "BR", "MX"]

        for region in [asia, europe, americas]:
            assert any(g in geos for g in region), f"Missing coverage for {region}"
