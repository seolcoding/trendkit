"""
Cache layer for trendkit with LRU and TTL support.

Usage:
    >>> from trendkit import trending
    >>> trending(limit=5, cache=True)  # Cache with default TTL (300s)
    >>> trending(limit=5, cache=True, ttl=60)  # Cache for 60 seconds

    >>> from trendkit.cache import cache
    >>> cache.clear()  # Clear all cached data
    >>> cache.stats()  # Get cache statistics
"""

import hashlib
import json
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


@dataclass
class CacheEntry:
    """A single cache entry with value and expiration time."""

    value: Any
    expires_at: float
    created_at: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        return time.time() > self.expires_at


@dataclass
class CacheStats:
    """Statistics about cache usage."""

    hits: int = 0
    misses: int = 0
    size: int = 0
    max_size: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{self.hit_rate:.1%}",
            "size": self.size,
            "max_size": self.max_size,
        }


class LRUCache:
    """Thread-safe LRU cache with TTL support.

    Attributes:
        max_size: Maximum number of entries (default: 1000)
        default_ttl: Default time-to-live in seconds (default: 300)
    """

    DEFAULT_MAX_SIZE = 1000
    DEFAULT_TTL = 300  # 5 minutes

    def __init__(
        self,
        max_size: int = DEFAULT_MAX_SIZE,
        default_ttl: int = DEFAULT_TTL
    ) -> None:
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats(max_size=max_size)
        self.max_size = max_size
        self.default_ttl = default_ttl

    def _make_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Create a unique cache key from function name and arguments."""
        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        key_data = {
            "func": func_name,
            "args": args,
            "kwargs": sorted_kwargs,
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if exists and not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                return None

            entry = self._cache[key]

            if entry.is_expired():
                del self._cache[key]
                self._stats.misses += 1
                self._stats.size = len(self._cache)
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._stats.hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        ttl = ttl or self.default_ttl

        with self._lock:
            # Remove oldest entries if at capacity
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)

            self._cache[key] = CacheEntry(
                value=value,
                expires_at=time.time() + ttl
            )
            self._stats.size = len(self._cache)

    def delete(self, key: str) -> bool:
        """Delete a specific key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.size = len(self._cache)
                return True
            return False

    def clear(self) -> int:
        """Clear all entries from cache.

        Returns:
            Number of entries cleared
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._stats.size = 0
            return count

    def cleanup_expired(self) -> int:
        """Remove all expired entries.

        Returns:
            Number of entries removed
        """
        with self._lock:
            expired_keys = [
                k for k, v in self._cache.items() if v.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
            self._stats.size = len(self._cache)
            return len(expired_keys)

    def stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with hits, misses, hit_rate, size, max_size
        """
        with self._lock:
            self._stats.size = len(self._cache)
            return self._stats.to_dict()

    def reset_stats(self) -> None:
        """Reset cache statistics."""
        with self._lock:
            self._stats.hits = 0
            self._stats.misses = 0

    def cached(
        self,
        ttl: Optional[int] = None,
        key_prefix: str = ""
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Decorator to cache function results.

        Args:
            ttl: Time-to-live in seconds
            key_prefix: Optional prefix for cache keys

        Returns:
            Decorated function with caching

        Example:
            >>> @cache.cached(ttl=60)
            ... def expensive_function(x):
            ...     return x * 2
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            def wrapper(*args: Any, **kwargs: Any) -> T:
                # Check if caching is enabled via kwargs
                use_cache = kwargs.pop("cache", True)
                custom_ttl = kwargs.pop("ttl", ttl)

                if not use_cache:
                    return func(*args, **kwargs)

                key = self._make_key(
                    f"{key_prefix}{func.__name__}",
                    args,
                    kwargs
                )

                # Try to get from cache
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value

                # Call function and cache result
                result = func(*args, **kwargs)
                self.set(key, result, custom_ttl)
                return result

            # Preserve function metadata
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper

        return decorator


# Global cache instance
_cache: Optional[LRUCache] = None


def get_cache() -> LRUCache:
    """Get or create the global cache instance."""
    global _cache
    if _cache is None:
        _cache = LRUCache()
    return _cache


def clear() -> int:
    """Clear all cached data.

    Returns:
        Number of entries cleared

    Example:
        >>> from trendkit import cache
        >>> cache.clear()
        42  # Number of entries cleared
    """
    return get_cache().clear()


def stats() -> dict:
    """Get cache statistics.

    Returns:
        Dictionary with cache statistics

    Example:
        >>> from trendkit import cache
        >>> cache.stats()
        {'hits': 100, 'misses': 20, 'hit_rate': '83.3%', 'size': 50, 'max_size': 1000}
    """
    return get_cache().stats()


def cleanup() -> int:
    """Remove expired entries from cache.

    Returns:
        Number of entries removed
    """
    return get_cache().cleanup_expired()


def configure(max_size: int = 1000, default_ttl: int = 300) -> None:
    """Configure cache settings.

    Args:
        max_size: Maximum number of entries
        default_ttl: Default time-to-live in seconds

    Note:
        This clears the existing cache.
    """
    global _cache
    _cache = LRUCache(max_size=max_size, default_ttl=default_ttl)
