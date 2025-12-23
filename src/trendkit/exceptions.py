"""
Exception hierarchy for trendkit.

Exception tree:
    TrendkitError (base)
    ├── TrendkitAPIError
    │   ├── TrendkitRateLimitError
    │   ├── TrendkitTimeoutError
    │   └── TrendkitServiceError
    ├── TrendkitDriverError
    └── TrendkitValidationError
"""

from typing import Optional


class TrendkitError(Exception):
    """Base exception for all trendkit errors.

    Attributes:
        message: Human-readable error message
        suggestion: Suggested action to resolve the error
    """

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None
    ) -> None:
        self.message = message
        self.suggestion = suggestion
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with suggestion if available."""
        if self.suggestion:
            return f"{self.message}\n\n💡 Suggestion: {self.suggestion}"
        return self.message


class TrendkitAPIError(TrendkitError):
    """Error related to API calls to Google Trends.

    Attributes:
        status_code: HTTP status code if available
    """

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        status_code: Optional[int] = None
    ) -> None:
        self.status_code = status_code
        super().__init__(message, suggestion)


class TrendkitRateLimitError(TrendkitAPIError):
    """Raised when Google Trends rate limit is hit.

    Attributes:
        retry_after: Suggested wait time in seconds before retrying
    """

    def __init__(
        self,
        message: str = "Google Trends rate limit exceeded",
        retry_after: int = 60,
        suggestion: Optional[str] = None
    ) -> None:
        self.retry_after = retry_after
        if suggestion is None:
            suggestion = f"Wait {retry_after} seconds before retrying, or use cache=True to reduce API calls"
        super().__init__(message, suggestion, status_code=429)


class TrendkitTimeoutError(TrendkitAPIError):
    """Raised when API request times out.

    Attributes:
        timeout: The timeout value that was exceeded
        partial_results: Any partial results collected before timeout
    """

    def __init__(
        self,
        message: str = "Request timed out",
        timeout: Optional[float] = None,
        partial_results: Optional[list] = None,
        suggestion: Optional[str] = None
    ) -> None:
        self.timeout = timeout
        self.partial_results = partial_results or []
        if suggestion is None:
            suggestion = "Try reducing the limit parameter or increase timeout"
        super().__init__(message, suggestion, status_code=408)


class TrendkitServiceError(TrendkitAPIError):
    """Raised when Google Trends service is unavailable."""

    def __init__(
        self,
        message: str = "Google Trends service is currently unavailable",
        suggestion: Optional[str] = None
    ) -> None:
        if suggestion is None:
            suggestion = "The service may be temporarily down. Try again later"
        super().__init__(message, suggestion, status_code=503)


class TrendkitDriverError(TrendkitError):
    """Raised when Selenium driver encounters issues.

    This typically occurs when ChromeDriver is not installed or
    version mismatches with Chrome browser.
    """

    def __init__(
        self,
        message: str = "Selenium driver error",
        suggestion: Optional[str] = None
    ) -> None:
        if suggestion is None:
            suggestion = (
                "Ensure ChromeDriver is installed and matches your Chrome version.\n"
                "Install with: pip install webdriver-manager\n"
                "Or download from: https://chromedriver.chromium.org/"
            )
        super().__init__(message, suggestion)


class TrendkitValidationError(TrendkitError):
    """Raised when input validation fails.

    Attributes:
        parameter: The parameter that failed validation
        valid_values: List of valid values if applicable
    """

    def __init__(
        self,
        message: str,
        parameter: Optional[str] = None,
        valid_values: Optional[list] = None,
        suggestion: Optional[str] = None
    ) -> None:
        self.parameter = parameter
        self.valid_values = valid_values

        if suggestion is None and valid_values:
            suggestion = f"Valid values for '{parameter}': {valid_values}"

        super().__init__(message, suggestion)


# Retry configuration
class RetryConfig:
    """Configuration for exponential backoff retry."""

    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BASE_DELAY = 1.0  # seconds
    DEFAULT_MAX_DELAY = 60.0  # seconds
    DEFAULT_EXPONENTIAL_BASE = 2.0

    def __init__(
        self,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_delay: float = DEFAULT_BASE_DELAY,
        max_delay: float = DEFAULT_MAX_DELAY,
        exponential_base: float = DEFAULT_EXPONENTIAL_BASE
    ) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number (0-indexed).

        Uses exponential backoff: base_delay * (exponential_base ** attempt)

        Args:
            attempt: The attempt number (0 for first retry)

        Returns:
            Delay in seconds, capped at max_delay
        """
        delay = self.base_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)
