"""Tests for CLI interface."""

import json
import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest

# Skip if typer/rich not installed
pytest.importorskip("typer")
pytest.importorskip("rich")

from typer.testing import CliRunner
from trendkit.cli import app


runner = CliRunner()


class TestTrendCommand:
    """Tests for 'trendkit trend' command."""

    def test_trend_default(self):
        """trend command should work with defaults."""
        result = runner.invoke(app, ["trend", "--limit", "3"])
        assert result.exit_code == 0
        # Should show numbered list
        assert "1." in result.stdout

    def test_trend_json_output(self):
        """trend --json should output valid JSON."""
        result = runner.invoke(app, ["trend", "--limit", "3", "--json"])
        assert result.exit_code == 0
        # Should be valid JSON
        data = json.loads(result.stdout)
        assert isinstance(data, list)

    def test_trend_with_geo(self):
        """trend --geo should work."""
        result = runner.invoke(app, ["trend", "--geo", "US", "--limit", "3"])
        assert result.exit_code == 0

    def test_trend_standard_format(self):
        """trend --format standard should show table."""
        result = runner.invoke(app, ["trend", "--format", "standard", "--limit", "3"])
        assert result.exit_code == 0
        # Should contain table elements
        assert "Keyword" in result.stdout or "keyword" in result.stdout.lower()

    def test_trend_full_format(self):
        """trend --format full should work."""
        result = runner.invoke(app, ["trend", "--format", "full", "--limit", "2"])
        assert result.exit_code == 0


class TestRelCommand:
    """Tests for 'trendkit rel' command (mocked)."""

    @patch("trendkit.cli.related")
    def test_rel_basic(self, mock_related):
        """rel command should work with keyword."""
        mock_related.return_value = ["query1", "query2", "query3"]
        result = runner.invoke(app, ["rel", "아이폰", "--limit", "3"])
        assert result.exit_code == 0
        assert "Related queries" in result.stdout or "query1" in result.stdout

    @patch("trendkit.cli.related")
    def test_rel_json_output(self, mock_related):
        """rel --json should output valid JSON."""
        mock_related.return_value = ["query1", "query2"]
        result = runner.invoke(app, ["rel", "아이폰", "--limit", "3", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)


class TestCmpCommand:
    """Tests for 'trendkit cmp' command (mocked)."""

    @patch("trendkit.cli.compare")
    def test_cmp_basic(self, mock_compare):
        """cmp command should work with keywords."""
        mock_compare.return_value = {"삼성": 45.0, "애플": 55.0}
        result = runner.invoke(app, ["cmp", "삼성", "애플"])
        assert result.exit_code == 0
        # Should show comparison table
        assert "삼성" in result.stdout or "Keyword" in result.stdout

    @patch("trendkit.cli.compare")
    def test_cmp_json_output(self, mock_compare):
        """cmp --json should output valid JSON."""
        mock_compare.return_value = {"삼성": 45.0, "애플": 55.0}
        result = runner.invoke(app, ["cmp", "삼성", "애플", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        assert "삼성" in data
        assert "애플" in data

    @patch("trendkit.cli.compare")
    def test_cmp_with_days(self, mock_compare):
        """cmp --days should work."""
        mock_compare.return_value = {"삼성": 50.0, "애플": 50.0}
        result = runner.invoke(app, ["cmp", "삼성", "애플", "--days", "30"])
        assert result.exit_code == 0


class TestHistCommand:
    """Tests for 'trendkit hist' command (mocked)."""

    @patch("trendkit.cli.interest")
    def test_hist_basic(self, mock_interest):
        """hist command should work with keywords."""
        mock_interest.return_value = {
            "dates": ["2024-12-01", "2024-12-02"],
            "values": {"BTS": [42, 45]}
        }
        result = runner.invoke(app, ["hist", "BTS", "--days", "7"])
        assert result.exit_code == 0
        assert "Interest over time" in result.stdout or "BTS" in result.stdout

    @patch("trendkit.cli.interest")
    def test_hist_json_output(self, mock_interest):
        """hist --json should output valid JSON."""
        mock_interest.return_value = {
            "dates": ["2024-12-01", "2024-12-02"],
            "values": {"BTS": [42, 45]}
        }
        result = runner.invoke(app, ["hist", "BTS", "--days", "7", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "dates" in data
        assert "values" in data


class TestBulkCommand:
    """Tests for 'trendkit bulk' command (mocked)."""

    @patch("trendkit.cli.trending_bulk")
    def test_bulk_with_output(self, mock_bulk):
        """bulk --output should save to file."""
        mock_bulk.return_value = [
            {"keyword": "test", "rank": 1, "traffic": "1000+"}
        ]

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            result = runner.invoke(app, [
                "bulk", "--limit", "10", "--output", filepath
            ])
            assert result.exit_code == 0
            assert "Saved" in result.stdout
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    @patch("trendkit.cli.trending_bulk")
    def test_bulk_json_output(self, mock_bulk):
        """bulk --json should output valid JSON."""
        mock_bulk.return_value = [
            {"keyword": "test", "rank": 1, "traffic": "1000+"}
        ]

        result = runner.invoke(app, ["bulk", "--limit", "10", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)

    @patch("trendkit.cli.trending_bulk")
    def test_bulk_enrich(self, mock_bulk):
        """bulk --enrich should show enriched data."""
        mock_bulk.return_value = {
            "metadata": {"geo": "KR", "hours": 168},
            "trends": [{"keyword": "test", "rank": 1, "traffic": "1000+", "news": [], "related": []}]
        }

        result = runner.invoke(app, ["bulk", "--limit", "5", "--enrich", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "metadata" in data
        assert "trends" in data

    @patch("trendkit.cli.trending_bulk")
    def test_bulk_table_output(self, mock_bulk):
        """bulk without --json should show table."""
        mock_bulk.return_value = [
            {"keyword": "test1", "rank": 1, "traffic": "1000+"},
            {"keyword": "test2", "rank": 2, "traffic": "500+"},
        ]

        result = runner.invoke(app, ["bulk", "--limit", "10"])
        assert result.exit_code == 0
        assert "Bulk Trending" in result.stdout
        assert "Keyword" in result.stdout
        assert "test1" in result.stdout
        assert "Total:" in result.stdout

    @patch("trendkit.cli.trending_bulk")
    def test_bulk_enrich_table_output(self, mock_bulk):
        """bulk --enrich without --json should show enriched table."""
        mock_bulk.return_value = {
            "metadata": {"geo": "KR", "hours": 168, "limit": 10, "total_items": 2},
            "trends": [
                {"keyword": "test1", "rank": 1, "traffic": "1000+", "news": [{"title": "News"}], "related": ["rel1"]},
                {"keyword": "test2", "rank": 2, "traffic": "500+", "news": [], "related": []},
            ]
        }

        result = runner.invoke(app, ["bulk", "--limit", "5", "--enrich"])
        assert result.exit_code == 0
        assert "Metadata" in result.stdout
        assert "News" in result.stdout  # Column header
        assert "Related" in result.stdout  # Column header
        assert "test1" in result.stdout


class TestCLIHelpMessages:
    """Tests for CLI help messages."""

    def test_main_help(self):
        """Main help should show available commands."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "trend" in result.stdout
        assert "rel" in result.stdout
        assert "cmp" in result.stdout

    def test_trend_help(self):
        """trend --help should show options."""
        result = runner.invoke(app, ["trend", "--help"])
        assert result.exit_code == 0
        assert "--geo" in result.stdout
        assert "--limit" in result.stdout
        assert "--format" in result.stdout

    def test_bulk_help(self):
        """bulk --help should show options."""
        result = runner.invoke(app, ["bulk", "--help"])
        assert result.exit_code == 0
        assert "--hours" in result.stdout
        assert "--enrich" in result.stdout
        assert "--output" in result.stdout
