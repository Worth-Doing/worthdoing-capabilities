"""In-memory cache store for WorthDoing capability results."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CacheEntry:
    """A single cached result with expiry tracking."""

    value: Any
    expires_at: float
    created_at: float = field(default_factory=time.time)


@dataclass
class CacheResult:
    """Result of a cache lookup."""

    hit: bool
    value: Any = None


class CacheStore:
    """Thread-safe in-memory cache with TTL support."""

    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}
        self._hits: int = 0
        self._misses: int = 0

    def generate_key(self, capability_name: str, input_data: dict) -> str:
        """Generate a deterministic cache key from the capability name and input data.

        Args:
            capability_name: Name of the capability.
            input_data: The validated input data.

        Returns:
            A hex digest string suitable as a cache key.
        """
        raw = json.dumps(
            {"capability": capability_name, "input": input_data},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, key: str) -> CacheResult:
        """Look up a value in the cache.

        Args:
            key: The cache key.

        Returns:
            A CacheResult indicating hit/miss and the cached value if hit.
        """
        entry = self._store.get(key)

        if entry is None:
            self._misses += 1
            return CacheResult(hit=False)

        if time.time() > entry.expires_at:
            # Expired -- remove and treat as miss
            del self._store[key]
            self._misses += 1
            return CacheResult(hit=False)

        self._hits += 1
        return CacheResult(hit=True, value=entry.value)

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Store a value in the cache.

        Args:
            key: The cache key.
            value: The value to cache.
            ttl_seconds: Time-to-live in seconds.
        """
        now = time.time()
        self._store[key] = CacheEntry(
            value=value,
            expires_at=now + ttl_seconds,
            created_at=now,
        )

    def invalidate(self, key: str) -> bool:
        """Remove a specific entry from the cache.

        Returns:
            True if the key existed and was removed, False otherwise.
        """
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> int:
        """Clear all cache entries.

        Returns:
            The number of entries removed.
        """
        count = len(self._store)
        self._store.clear()
        return count

    def stats(self) -> dict[str, Any]:
        """Return cache statistics.

        Returns:
            A dict with hit/miss counts and current size.
        """
        # Purge expired entries for an accurate count
        now = time.time()
        expired_keys = [k for k, v in self._store.items() if now > v.expires_at]
        for k in expired_keys:
            del self._store[k]

        total = self._hits + self._misses
        return {
            "size": len(self._store),
            "hits": self._hits,
            "misses": self._misses,
            "total_lookups": total,
            "hit_rate": self._hits / total if total > 0 else 0.0,
        }
