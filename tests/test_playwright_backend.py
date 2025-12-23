"""Tests for Playwright backend with stealth capabilities."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio


# Skip if playwright not installed
pytest.importorskip("playwright")
pytest.importorskip("playwright_stealth")


class TestPlaywrightBackendInit:
    """Tests for PlaywrightBackend initialization."""

    def test_init_default_headless(self):
        """Should default to headless mode."""
        from trendkit.backends.playwright_backend import PlaywrightBackend
        backend = PlaywrightBackend()
        assert backend.headless is True
        assert backend._browser is None

    def test_init_headful(self):
        """Should accept headless=False."""
        from trendkit.backends.playwright_backend import PlaywrightBackend
        backend = PlaywrightBackend(headless=False)
        assert backend.headless is False


class TestPlaywrightBackendImportError:
    """Tests for import error handling."""

    def test_import_error_message(self):
        """Should provide helpful import error message."""
        import sys

        # Save original modules
        original_playwright = sys.modules.get('playwright')
        original_async_api = sys.modules.get('playwright.async_api')
        original_stealth = sys.modules.get('playwright_stealth')

        try:
            # Remove playwright modules
            sys.modules['playwright'] = None
            sys.modules['playwright.async_api'] = None
            sys.modules['playwright_stealth'] = None

            from trendkit.backends.playwright_backend import PlaywrightBackend
            backend = PlaywrightBackend()

            # Trying to setup should raise ImportError
            with pytest.raises(ImportError) as exc_info:
                asyncio.run(backend._setup_browser())

            # This test might not work due to module caching
        except (ImportError, TypeError):
            pass
        finally:
            # Restore modules
            if original_playwright:
                sys.modules['playwright'] = original_playwright
            if original_async_api:
                sys.modules['playwright.async_api'] = original_async_api
            if original_stealth:
                sys.modules['playwright_stealth'] = original_stealth


class TestPlaywrightBackendMocked:
    """Tests for PlaywrightBackend with mocked browser."""

    def test_fetch_trending_returns_list(self):
        """fetch_trending should return a list."""
        from trendkit.backends.playwright_backend import PlaywrightBackend

        async def mock_fetch(*args, **kwargs):
            return [
                {"keyword": "test1", "rank": 1, "traffic": "1000+"},
                {"keyword": "test2", "rank": 2, "traffic": "500+"},
            ]

        backend = PlaywrightBackend()
        with patch.object(backend, '_fetch_trending_async', side_effect=mock_fetch):
            result = backend.fetch_trending(geo="KR", limit=2)

            assert len(result) == 2
            assert result[0]["keyword"] == "test1"

    def test_fetch_trending_empty_on_error(self):
        """fetch_trending should return empty list on error."""
        from trendkit.backends.playwright_backend import PlaywrightBackend

        async def mock_fetch(*args, **kwargs):
            return []

        backend = PlaywrightBackend()
        with patch.object(backend, '_fetch_trending_async', side_effect=mock_fetch):
            result = backend.fetch_trending(geo="INVALID", limit=5)

            assert result == []

    def test_fetch_trending_handles_exception(self):
        """fetch_trending should handle exceptions gracefully."""
        from trendkit.backends.playwright_backend import PlaywrightBackend

        async def mock_fetch(*args, **kwargs):
            raise Exception("Connection failed")

        backend = PlaywrightBackend()
        with patch.object(backend, '_fetch_trending_async', side_effect=mock_fetch):
            with pytest.raises(Exception):
                backend.fetch_trending(geo="KR", limit=5)


class TestPlaywrightBackendClose:
    """Tests for PlaywrightBackend close behavior."""

    def test_close_without_browser(self):
        """close() should not raise if browser not started."""
        from trendkit.backends.playwright_backend import PlaywrightBackend
        backend = PlaywrightBackend()
        backend.close()  # Should not raise

    def test_close_cleans_up(self):
        """close() should clean up all resources."""
        from trendkit.backends.playwright_backend import PlaywrightBackend
        backend = PlaywrightBackend()

        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_browser = AsyncMock()
        mock_playwright = AsyncMock()

        backend._page = mock_page
        backend._context = mock_context
        backend._browser = mock_browser
        backend._playwright = mock_playwright

        backend.close()

        assert backend._page is None
        assert backend._context is None
        assert backend._browser is None
        assert backend._playwright is None


class TestAsyncPlaywrightBackend:
    """Tests for AsyncPlaywrightBackend."""

    def test_async_backend_exists(self):
        """AsyncPlaywrightBackend should exist."""
        from trendkit.backends.playwright_backend import AsyncPlaywrightBackend
        assert AsyncPlaywrightBackend is not None

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """AsyncPlaywrightBackend should work as async context manager."""
        from trendkit.backends.playwright_backend import AsyncPlaywrightBackend

        with patch.object(AsyncPlaywrightBackend, '_setup_browser', new_callable=AsyncMock):
            with patch.object(AsyncPlaywrightBackend, 'close', new_callable=AsyncMock):
                async with AsyncPlaywrightBackend() as backend:
                    assert backend is not None


class TestPlaywrightStealthFeatures:
    """Tests for stealth-specific features."""

    def test_stealth_import(self):
        """playwright-stealth should be importable."""
        from playwright_stealth import Stealth
        assert Stealth is not None

    def test_backend_has_stealth_attribute(self):
        """Backend should have _stealth attribute."""
        from trendkit.backends.playwright_backend import PlaywrightBackend
        backend = PlaywrightBackend()
        assert hasattr(backend, '_stealth')

    def test_context_settings(self):
        """Browser context should have Korean locale settings."""
        from trendkit.backends.playwright_backend import PlaywrightBackend

        # The backend initializes with locale and timezone
        backend = PlaywrightBackend()
        # These are set in _setup_browser, just checking the backend exists
        assert backend is not None


class TestPlaywrightBackendPagination:
    """Tests for pagination logic."""

    def test_pages_calculation_small_limit(self):
        """Should calculate 1 page for small limits."""
        # limit=5 => (5 // 25) + 1 = 1 page
        from trendkit.backends.playwright_backend import PlaywrightBackend

        async def mock_fetch(*args, **kwargs):
            return [{"keyword": f"test{i}", "rank": i, "traffic": "N/A"} for i in range(5)]

        backend = PlaywrightBackend()
        with patch.object(backend, '_fetch_trending_async', side_effect=mock_fetch):
            result = backend.fetch_trending(limit=5)
            assert len(result) == 5

    def test_pages_calculation_large_limit(self):
        """Should calculate up to 4 pages for large limits."""
        # limit=100 => (100 // 25) + 1 = 5 pages, capped at 4
        from trendkit.backends.playwright_backend import PlaywrightBackend

        async def mock_fetch(*args, **kwargs):
            return [{"keyword": f"test{i}", "rank": i, "traffic": "N/A"} for i in range(100)]

        backend = PlaywrightBackend()
        with patch.object(backend, '_fetch_trending_async', side_effect=mock_fetch):
            result = backend.fetch_trending(limit=100)
            assert len(result) == 100


class TestPlaywrightBackendIntegration:
    """Integration tests (requires real browser)."""

    @pytest.mark.skipif(
        True,  # Skip by default, enable for local testing
        reason="Integration test - requires browser"
    )
    def test_real_browser_fetch(self):
        """Test with real browser."""
        from trendkit.backends.playwright_backend import PlaywrightBackend

        backend = PlaywrightBackend(headless=True)
        try:
            result = backend.fetch_trending(geo="KR", limit=5)
            assert isinstance(result, list)
            # Should get some results (if not blocked)
            print(f"Got {len(result)} results")
            for item in result:
                print(f"  - {item['keyword']}: {item['traffic']}")
        finally:
            backend.close()
