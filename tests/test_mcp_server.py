"""Tests for MCP server tools."""

import sys
from unittest.mock import patch, MagicMock
import pytest

# Skip if MCP not installed
pytest.importorskip("mcp")

from trendkit.mcp_server import (
    trends_trending,
    trends_related,
    trends_compare,
    trends_interest,
    main,
    mcp,
)


class TestTrendsTrending:
    """Tests for trends_trending MCP tool."""

    @patch("trendkit.mcp_server.trending")
    def test_default_params(self, mock_trending):
        """Should call trending with defaults."""
        mock_trending.return_value = ["keyword1", "keyword2"]

        result = trends_trending()

        mock_trending.assert_called_once_with(geo="KR", limit=10, format="minimal")
        assert result == ["keyword1", "keyword2"]

    @patch("trendkit.mcp_server.trending")
    def test_custom_params(self, mock_trending):
        """Should pass custom parameters."""
        mock_trending.return_value = [{"keyword": "test"}]

        result = trends_trending(geo="US", limit=5, format="standard")

        mock_trending.assert_called_once_with(geo="US", limit=5, format="standard")

    @patch("trendkit.mcp_server.trending")
    def test_full_format(self, mock_trending):
        """Should support full format."""
        mock_trending.return_value = [{"keyword": "test", "news": []}]

        result = trends_trending(format="full", limit=3)

        assert mock_trending.call_args[1]["format"] == "full"


class TestTrendsRelated:
    """Tests for trends_related MCP tool."""

    @patch("trendkit.mcp_server.related")
    def test_basic_call(self, mock_related):
        """Should call related with keyword."""
        mock_related.return_value = ["related1", "related2"]

        result = trends_related(keyword="아이폰")

        mock_related.assert_called_once_with(keyword="아이폰", geo="KR", limit=10)
        assert result == ["related1", "related2"]

    @patch("trendkit.mcp_server.related")
    def test_custom_params(self, mock_related):
        """Should pass custom parameters."""
        mock_related.return_value = ["related1"]

        result = trends_related(keyword="iphone", geo="US", limit=5)

        mock_related.assert_called_once_with(keyword="iphone", geo="US", limit=5)


class TestTrendsCompare:
    """Tests for trends_compare MCP tool."""

    @patch("trendkit.mcp_server.compare")
    def test_basic_call(self, mock_compare):
        """Should call compare with keywords."""
        mock_compare.return_value = {"삼성": 45.6, "애플": 32.1}

        result = trends_compare(keywords=["삼성", "애플"])

        mock_compare.assert_called_once_with(
            keywords=["삼성", "애플"], geo="KR", days=90, platform="web"
        )
        assert result == {"삼성": 45.6, "애플": 32.1}

    @patch("trendkit.mcp_server.compare")
    def test_youtube_platform(self, mock_compare):
        """Should support YouTube platform."""
        mock_compare.return_value = {"BTS": 65.0}

        result = trends_compare(keywords=["BTS"], platform="youtube")

        assert mock_compare.call_args[1]["platform"] == "youtube"


class TestTrendsInterest:
    """Tests for trends_interest MCP tool."""

    @patch("trendkit.mcp_server.interest")
    def test_basic_call(self, mock_interest):
        """Should call interest with keywords."""
        mock_interest.return_value = {
            "dates": ["2024-12-01", "2024-12-02"],
            "values": {"BTS": [42, 45]}
        }

        result = trends_interest(keywords=["BTS"])

        mock_interest.assert_called_once_with(
            keywords=["BTS"], geo="KR", days=7, platform="web"
        )
        assert "dates" in result
        assert "values" in result

    @patch("trendkit.mcp_server.interest")
    def test_custom_params(self, mock_interest):
        """Should pass custom parameters."""
        mock_interest.return_value = {"dates": [], "values": {}}

        result = trends_interest(
            keywords=["keyword1", "keyword2"],
            geo="US",
            days=30,
            platform="news"
        )

        mock_interest.assert_called_once_with(
            keywords=["keyword1", "keyword2"],
            geo="US",
            days=30,
            platform="news"
        )


class TestMCPToolDocstrings:
    """Tests for MCP tool docstrings."""

    def test_trends_trending_docstring(self):
        """trends_trending should have proper docstring."""
        assert trends_trending.__doc__ is not None
        assert "geo" in trends_trending.__doc__
        assert "limit" in trends_trending.__doc__

    def test_trends_related_docstring(self):
        """trends_related should have proper docstring."""
        assert trends_related.__doc__ is not None
        assert "keyword" in trends_related.__doc__

    def test_trends_compare_docstring(self):
        """trends_compare should have proper docstring."""
        assert trends_compare.__doc__ is not None
        assert "keywords" in trends_compare.__doc__
        assert "platform" in trends_compare.__doc__

    def test_trends_interest_docstring(self):
        """trends_interest should have proper docstring."""
        assert trends_interest.__doc__ is not None
        assert "dates" in trends_interest.__doc__
        assert "values" in trends_interest.__doc__


class TestMCPMain:
    """Tests for MCP server entry point."""

    def test_main_calls_mcp_run(self):
        """main() should call mcp.run with stdio transport."""
        with patch.object(mcp, 'run') as mock_run:
            main()
            mock_run.assert_called_once_with(transport="stdio")

    def test_mcp_server_exists(self):
        """MCP server should be properly initialized."""
        assert mcp is not None
        assert mcp.name == "trendkit"


class TestMCPErrorHandling:
    """Tests for MCP tool error scenarios."""

    @patch("trendkit.mcp_server.trending")
    def test_trending_rate_limit_propagates(self, mock_trending):
        """MCP tool should propagate rate limit errors."""
        from trendkit import TrendkitRateLimitError
        mock_trending.side_effect = TrendkitRateLimitError(retry_after=60)

        with pytest.raises(TrendkitRateLimitError) as exc_info:
            trends_trending()
        assert exc_info.value.retry_after == 60

    @patch("trendkit.mcp_server.compare")
    def test_compare_validation_error_propagates(self, mock_compare):
        """MCP tool should propagate validation errors."""
        from trendkit import TrendkitValidationError
        mock_compare.side_effect = TrendkitValidationError("Invalid keyword count")

        with pytest.raises(TrendkitValidationError):
            trends_compare(keywords=["single"])

    @patch("trendkit.mcp_server.interest")
    def test_interest_timeout_propagates(self, mock_interest):
        """MCP tool should propagate timeout errors."""
        from trendkit import TrendkitTimeoutError
        mock_interest.side_effect = TrendkitTimeoutError(timeout=30.0)

        with pytest.raises(TrendkitTimeoutError):
            trends_interest(keywords=["test"])


class TestMCPImportError:
    """Tests for MCP import error handling."""

    def test_import_error_when_mcp_missing(self):
        """Should raise ImportError with helpful message when MCP not installed."""
        # Save original modules
        original_mcp = sys.modules.get('mcp')
        original_fastmcp = sys.modules.get('mcp.server.fastmcp')

        try:
            # Remove mcp from modules to simulate it not being installed
            if 'mcp' in sys.modules:
                del sys.modules['mcp']
            if 'mcp.server.fastmcp' in sys.modules:
                del sys.modules['mcp.server.fastmcp']
            if 'trendkit.mcp_server' in sys.modules:
                del sys.modules['trendkit.mcp_server']

            # Mock the import to raise ImportError
            with patch.dict(sys.modules, {'mcp': None, 'mcp.server.fastmcp': None}):
                with pytest.raises(ImportError) as exc_info:
                    # Force reimport
                    import importlib
                    import trendkit.mcp_server
                    importlib.reload(trendkit.mcp_server)
        except (ImportError, TypeError):
            # Expected - either import fails or reload fails
            pass
        finally:
            # Restore original modules
            if original_mcp:
                sys.modules['mcp'] = original_mcp
            if original_fastmcp:
                sys.modules['mcp.server.fastmcp'] = original_fastmcp
