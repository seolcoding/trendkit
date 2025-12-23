"""Tests for trendkit exceptions."""

import pytest
from trendkit import (
    TrendkitError,
    TrendkitAPIError,
    TrendkitRateLimitError,
    TrendkitTimeoutError,
    TrendkitServiceError,
    TrendkitDriverError,
    TrendkitValidationError,
    RetryConfig,
)


class TestTrendkitError:
    """Tests for base TrendkitError."""

    def test_basic_error(self):
        """TrendkitError should store message."""
        error = TrendkitError("Something went wrong")
        assert error.message == "Something went wrong"
        assert str(error) == "Something went wrong"

    def test_error_with_suggestion(self):
        """TrendkitError should include suggestion in message."""
        error = TrendkitError("Error occurred", suggestion="Try again later")
        assert error.suggestion == "Try again later"
        assert "💡 Suggestion:" in str(error)
        assert "Try again later" in str(error)


class TestTrendkitRateLimitError:
    """Tests for TrendkitRateLimitError."""

    def test_default_retry_after(self):
        """RateLimitError should have default retry_after."""
        error = TrendkitRateLimitError()
        assert error.retry_after == 60
        assert error.status_code == 429

    def test_custom_retry_after(self):
        """RateLimitError should accept custom retry_after."""
        error = TrendkitRateLimitError(retry_after=120)
        assert error.retry_after == 120

    def test_suggestion_includes_retry_time(self):
        """Suggestion should mention retry time."""
        error = TrendkitRateLimitError(retry_after=30)
        assert "30 seconds" in str(error)


class TestTrendkitTimeoutError:
    """Tests for TrendkitTimeoutError."""

    def test_timeout_error(self):
        """TimeoutError should store timeout value."""
        error = TrendkitTimeoutError(timeout=30.0)
        assert error.timeout == 30.0
        assert error.status_code == 408

    def test_partial_results(self):
        """TimeoutError should store partial results."""
        partial = [{"keyword": "test"}]
        error = TrendkitTimeoutError(partial_results=partial)
        assert error.partial_results == partial

    def test_empty_partial_results(self):
        """TimeoutError should default to empty list."""
        error = TrendkitTimeoutError()
        assert error.partial_results == []


class TestTrendkitServiceError:
    """Tests for TrendkitServiceError."""

    def test_default_suggestion(self):
        """ServiceError should have default suggestion when none provided."""
        error = TrendkitServiceError()
        assert error.suggestion is not None
        assert "try again" in error.suggestion.lower()
        assert error.status_code == 503

    def test_custom_message(self):
        """ServiceError should accept custom message."""
        error = TrendkitServiceError(message="Service down")
        assert "Service down" in str(error)

    def test_custom_suggestion(self):
        """ServiceError should use custom suggestion when provided."""
        error = TrendkitServiceError(suggestion="Contact support")
        assert error.suggestion == "Contact support"


class TestTrendkitDriverError:
    """Tests for TrendkitDriverError."""

    def test_default_suggestion(self):
        """DriverError should have helpful default suggestion."""
        error = TrendkitDriverError()
        assert "ChromeDriver" in str(error)
        assert "pip install" in str(error)

    def test_custom_message(self):
        """DriverError should accept custom message."""
        error = TrendkitDriverError(message="Browser crashed")
        assert "Browser crashed" in str(error)


class TestTrendkitValidationError:
    """Tests for TrendkitValidationError."""

    def test_validation_error(self):
        """ValidationError should store parameter name."""
        error = TrendkitValidationError(
            message="Invalid value",
            parameter="geo"
        )
        assert error.parameter == "geo"

    def test_valid_values(self):
        """ValidationError should list valid values."""
        error = TrendkitValidationError(
            message="Invalid geo",
            parameter="geo",
            valid_values=["KR", "US", "JP"]
        )
        assert error.valid_values == ["KR", "US", "JP"]
        assert "KR" in str(error)


class TestRetryConfig:
    """Tests for RetryConfig."""

    def test_default_config(self):
        """RetryConfig should have sensible defaults."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.exponential_base == 2.0

    def test_get_delay_exponential(self):
        """get_delay should use exponential backoff."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0)
        assert config.get_delay(0) == 1.0   # 1 * 2^0 = 1
        assert config.get_delay(1) == 2.0   # 1 * 2^1 = 2
        assert config.get_delay(2) == 4.0   # 1 * 2^2 = 4

    def test_get_delay_capped(self):
        """get_delay should cap at max_delay."""
        config = RetryConfig(base_delay=10.0, max_delay=30.0)
        assert config.get_delay(5) == 30.0  # Would be 320, capped at 30

    def test_custom_config(self):
        """RetryConfig should accept custom values."""
        config = RetryConfig(
            max_retries=5,
            base_delay=0.5,
            max_delay=10.0
        )
        assert config.max_retries == 5
        assert config.base_delay == 0.5
        assert config.max_delay == 10.0


class TestExceptionHierarchy:
    """Tests for exception inheritance."""

    def test_api_error_inherits_from_base(self):
        """TrendkitAPIError should inherit from TrendkitError."""
        assert issubclass(TrendkitAPIError, TrendkitError)

    def test_rate_limit_inherits_from_api_error(self):
        """TrendkitRateLimitError should inherit from TrendkitAPIError."""
        assert issubclass(TrendkitRateLimitError, TrendkitAPIError)

    def test_timeout_inherits_from_api_error(self):
        """TrendkitTimeoutError should inherit from TrendkitAPIError."""
        assert issubclass(TrendkitTimeoutError, TrendkitAPIError)

    def test_driver_error_inherits_from_base(self):
        """TrendkitDriverError should inherit from TrendkitError."""
        assert issubclass(TrendkitDriverError, TrendkitError)

    def test_validation_error_inherits_from_base(self):
        """TrendkitValidationError should inherit from TrendkitError."""
        assert issubclass(TrendkitValidationError, TrendkitError)

    def test_catching_base_catches_all(self):
        """Catching TrendkitError should catch all subclasses."""
        errors = [
            TrendkitRateLimitError(),
            TrendkitTimeoutError(),
            TrendkitDriverError(),
            TrendkitValidationError("test"),
        ]
        for error in errors:
            try:
                raise error
            except TrendkitError:
                pass  # Should catch all
