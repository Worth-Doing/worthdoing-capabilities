"""Tests for the CacheStore."""

import time

import pytest

from worthdoing_capabilities.cache.store import CacheStore


@pytest.fixture
def store():
    """Create a fresh CacheStore for each test."""
    return CacheStore()


class TestCacheSetAndGet:
    """Test basic set/get operations."""

    def test_set_and_get_returns_hit(self, store):
        store.set("key1", {"data": 42}, ttl_seconds=60)

        result = store.get("key1")

        assert result.hit is True
        assert result.value == {"data": 42}

    def test_cache_miss_returns_hit_false(self, store):
        result = store.get("nonexistent")

        assert result.hit is False
        assert result.value is None

    def test_overwrite_existing_key(self, store):
        store.set("key", "old", ttl_seconds=60)
        store.set("key", "new", ttl_seconds=60)

        result = store.get("key")

        assert result.hit is True
        assert result.value == "new"


class TestCacheTTL:
    """Test TTL-based expiration."""

    def test_expired_entry_returns_miss(self, store):
        store.set("expiring", "value", ttl_seconds=0)

        # A TTL of 0 means it expires immediately; small sleep to ensure
        time.sleep(0.05)
        result = store.get("expiring")

        assert result.hit is False

    def test_non_expired_entry_returns_hit(self, store):
        store.set("lasting", "value", ttl_seconds=300)

        result = store.get("lasting")

        assert result.hit is True
        assert result.value == "value"


class TestCacheKeyGeneration:
    """Test deterministic cache key generation."""

    def test_same_input_produces_same_key(self, store):
        key1 = store.generate_key("cap.test", {"query": "hello"})
        key2 = store.generate_key("cap.test", {"query": "hello"})

        assert key1 == key2

    def test_different_input_produces_different_key(self, store):
        key1 = store.generate_key("cap.test", {"query": "hello"})
        key2 = store.generate_key("cap.test", {"query": "world"})

        assert key1 != key2

    def test_different_capability_produces_different_key(self, store):
        key1 = store.generate_key("cap.one", {"query": "hello"})
        key2 = store.generate_key("cap.two", {"query": "hello"})

        assert key1 != key2

    def test_key_is_deterministic_across_dict_ordering(self, store):
        key1 = store.generate_key("cap.test", {"a": 1, "b": 2})
        key2 = store.generate_key("cap.test", {"b": 2, "a": 1})

        assert key1 == key2


class TestCacheInvalidateAndClear:
    """Test invalidate and clear operations."""

    def test_invalidate_removes_single_entry(self, store):
        store.set("k1", "v1", ttl_seconds=60)
        store.set("k2", "v2", ttl_seconds=60)

        removed = store.invalidate("k1")

        assert removed is True
        assert store.get("k1").hit is False
        assert store.get("k2").hit is True

    def test_invalidate_nonexistent_key_returns_false(self, store):
        result = store.invalidate("does_not_exist")

        assert result is False

    def test_clear_empties_entire_store(self, store):
        store.set("k1", "v1", ttl_seconds=60)
        store.set("k2", "v2", ttl_seconds=60)

        removed_count = store.clear()

        assert removed_count == 2
        assert store.get("k1").hit is False
        assert store.get("k2").hit is False


class TestCacheStats:
    """Test cache statistics tracking."""

    def test_initial_stats_are_zero(self, store):
        stats = store.stats()

        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["size"] == 0

    def test_stats_track_hits_and_misses(self, store):
        store.set("k", "v", ttl_seconds=60)

        store.get("k")       # hit
        store.get("k")       # hit
        store.get("missing") # miss

        stats = store.stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["size"] == 1

    def test_stats_include_total_lookups_and_hit_rate(self, store):
        store.set("k", "v", ttl_seconds=60)

        store.get("k")       # hit
        store.get("missing") # miss

        stats = store.stats()
        assert stats["total_lookups"] == 2
        assert stats["hit_rate"] == pytest.approx(0.5)
