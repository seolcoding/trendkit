"""Tests for trendkit cache layer."""

import time
import pytest
from trendkit import cache
from trendkit.cache import LRUCache, CacheEntry, CacheStats


class TestCacheEntry:
    """Tests for CacheEntry."""

    def test_entry_not_expired(self):
        """Entry should not be expired when TTL hasn't passed."""
        entry = CacheEntry(value="test", expires_at=time.time() + 100)
        assert not entry.is_expired()

    def test_entry_expired(self):
        """Entry should be expired after TTL passes."""
        entry = CacheEntry(value="test", expires_at=time.time() - 1)
        assert entry.is_expired()


class TestCacheStats:
    """Tests for CacheStats."""

    def test_hit_rate_zero_total(self):
        """Hit rate should be 0 when no requests."""
        stats = CacheStats()
        assert stats.hit_rate == 0.0

    def test_hit_rate_calculation(self):
        """Hit rate should be calculated correctly."""
        stats = CacheStats(hits=80, misses=20)
        assert stats.hit_rate == 0.8

    def test_to_dict(self):
        """Stats should convert to dict."""
        stats = CacheStats(hits=100, misses=25, size=50, max_size=1000)
        d = stats.to_dict()
        assert d["hits"] == 100
        assert d["misses"] == 25
        assert d["size"] == 50
        assert "80.0%" in d["hit_rate"]


class TestLRUCache:
    """Tests for LRUCache."""

    def test_set_and_get(self):
        """Cache should store and retrieve values."""
        c = LRUCache()
        c.set("key1", "value1")
        assert c.get("key1") == "value1"

    def test_get_nonexistent(self):
        """Cache should return None for missing keys."""
        c = LRUCache()
        assert c.get("nonexistent") is None

    def test_ttl_expiration(self):
        """Cache should expire entries after TTL."""
        c = LRUCache(default_ttl=1)
        c.set("key", "value", ttl=1)
        assert c.get("key") == "value"
        time.sleep(1.1)
        assert c.get("key") is None

    def test_lru_eviction(self):
        """Cache should evict least recently used."""
        c = LRUCache(max_size=2)
        c.set("a", 1)
        c.set("b", 2)
        c.set("c", 3)  # Should evict 'a'
        assert c.get("a") is None
        assert c.get("b") == 2
        assert c.get("c") == 3

    def test_access_updates_lru(self):
        """Accessing an entry should update its LRU position."""
        c = LRUCache(max_size=2)
        c.set("a", 1)
        c.set("b", 2)
        c.get("a")  # Access 'a' to make it recently used
        c.set("c", 3)  # Should evict 'b' instead of 'a'
        assert c.get("a") == 1
        assert c.get("b") is None
        assert c.get("c") == 3

    def test_delete(self):
        """Cache should delete specific keys."""
        c = LRUCache()
        c.set("key", "value")
        assert c.delete("key") is True
        assert c.get("key") is None
        assert c.delete("key") is False

    def test_clear(self):
        """Cache should clear all entries."""
        c = LRUCache()
        c.set("a", 1)
        c.set("b", 2)
        count = c.clear()
        assert count == 2
        assert c.get("a") is None
        assert c.get("b") is None

    def test_cleanup_expired(self):
        """Cache should remove expired entries."""
        c = LRUCache()
        c.set("short", "value", ttl=1)
        c.set("long", "value", ttl=100)
        time.sleep(1.1)
        count = c.cleanup_expired()
        assert count == 1
        assert c.get("short") is None
        assert c.get("long") == "value"

    def test_stats(self):
        """Cache should track statistics."""
        c = LRUCache()
        c.set("key", "value")
        c.get("key")  # Hit
        c.get("missing")  # Miss
        stats = c.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1

    def test_reset_stats(self):
        """Cache should reset statistics."""
        c = LRUCache()
        c.get("key")  # Miss
        c.reset_stats()
        stats = c.stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0


class TestCacheDecorator:
    """Tests for cache decorator."""

    def test_cached_function(self):
        """Decorator should cache function results."""
        c = LRUCache()
        call_count = 0

        @c.cached(ttl=60)
        def expensive_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call should execute function
        result1 = expensive_func(5)
        assert result1 == 10
        assert call_count == 1

        # Second call should use cache
        result2 = expensive_func(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented

    def test_cached_with_different_args(self):
        """Decorator should cache different args separately."""
        c = LRUCache()
        call_count = 0

        @c.cached(ttl=60)
        def func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        func(5)
        func(10)
        assert call_count == 2

    def test_cache_bypass(self):
        """Decorator should allow cache bypass."""
        c = LRUCache()
        call_count = 0

        @c.cached(ttl=60)
        def func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        func(5)
        func(5, cache=False)  # Bypass cache
        assert call_count == 2


class TestGlobalCache:
    """Tests for global cache functions."""

    def test_clear(self):
        """Global clear should work."""
        cache.configure()  # Reset
        count = cache.clear()
        assert isinstance(count, int)

    def test_stats(self):
        """Global stats should work."""
        cache.configure()  # Reset
        stats = cache.stats()
        assert "hits" in stats
        assert "misses" in stats
        assert "size" in stats

    def test_configure(self):
        """Configure should set new cache settings."""
        cache.configure(max_size=100, default_ttl=60)
        stats = cache.stats()
        assert stats["max_size"] == 100


class TestCacheKeyGeneration:
    """Tests for cache key generation."""

    def test_same_args_same_key(self):
        """Same arguments should generate same key."""
        c = LRUCache()
        key1 = c._make_key("func", (1, 2), {"a": "b"})
        key2 = c._make_key("func", (1, 2), {"a": "b"})
        assert key1 == key2

    def test_different_args_different_key(self):
        """Different arguments should generate different keys."""
        c = LRUCache()
        key1 = c._make_key("func", (1, 2), {})
        key2 = c._make_key("func", (1, 3), {})
        assert key1 != key2

    def test_kwarg_order_irrelevant(self):
        """Kwarg order should not affect key."""
        c = LRUCache()
        key1 = c._make_key("func", (), {"a": 1, "b": 2})
        key2 = c._make_key("func", (), {"b": 2, "a": 1})
        assert key1 == key2
