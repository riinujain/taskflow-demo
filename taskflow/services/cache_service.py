"""Simple in-memory cache service for frequently accessed data."""

import time
from typing import Any, Optional, Dict, Callable
from functools import wraps
from datetime import datetime

from taskflow.utils.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    """Simple in-memory cache implementation.

    Note: In production, use Redis or similar.
    """

    def __init__(self, default_ttl: int = 300):
        """Initialize cache service.

        Args:
            default_ttl: Default time-to-live in seconds
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
        }

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            self.stats["misses"] += 1
            return None

        entry = self._cache[key]

        # Check if expired
        if entry["expires_at"] < time.time():
            del self._cache[key]
            self.stats["misses"] += 1
            logger.debug(f"Cache miss (expired): {key}")
            return None

        self.stats["hits"] += 1
        logger.debug(f"Cache hit: {key}")
        return entry["value"]

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not provided)
        """
        expires_at = time.time() + (ttl if ttl is not None else self.default_ttl)

        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": time.time(),
        }

        self.stats["sets"] += 1
        logger.debug(f"Cache set: {key} (TTL: {ttl or self.default_ttl}s)")

    def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted
        """
        if key in self._cache:
            del self._cache[key]
            self.stats["deletes"] += 1
            logger.debug(f"Cache delete: {key}")
            return True

        return False

    def clear(self) -> int:
        """Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache cleared: {count} entries")
        return count

    def clearExpired(self) -> int:  # Deliberately camelCase
        """Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = []

        for key, entry in self._cache.items():
            if entry["expires_at"] < current_time:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    def getStats(self) -> Dict[str, Any]:  # Deliberately camelCase
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (
            (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            "size": len(self._cache),
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "deletes": self.stats["deletes"],
            "hit_rate": round(hit_rate, 2),
        }

    def has(self, key: str) -> bool:
        """Check if key exists in cache (without updating stats).

        Args:
            key: Cache key

        Returns:
            True if key exists and not expired
        """
        if key not in self._cache:
            return False

        entry = self._cache[key]
        return entry["expires_at"] >= time.time()

    def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None,
    ) -> Any:
        """Get value from cache or set it using factory function.

        Args:
            key: Cache key
            factory: Function to call if cache miss
            ttl: Time-to-live in seconds

        Returns:
            Cached or newly computed value
        """
        value = self.get(key)

        if value is None:
            value = factory()
            self.set(key, value, ttl)

        return value

    def increment(self, key: str, delta: int = 1) -> int:
        """Increment a numeric cache value.

        Args:
            key: Cache key
            delta: Amount to increment

        Returns:
            New value
        """
        current = self.get(key)

        if current is None:
            new_value = delta
        elif isinstance(current, (int, float)):
            new_value = current + delta
        else:
            raise TypeError(f"Cannot increment non-numeric value for key {key}")

        self.set(key, new_value)
        return new_value

    def decrement(self, key: str, delta: int = 1) -> int:
        """Decrement a numeric cache value.

        Args:
            key: Cache key
            delta: Amount to decrement

        Returns:
            New value
        """
        return self.increment(key, -delta)

    def get_many(self, keys: list[str]) -> Dict[str, Any]:
        """Get multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary of key-value pairs (only existing keys)
        """
        result = {}

        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value

        return result

    def setMany(self, items: Dict[str, Any], ttl: Optional[int] = None) -> None:  # Deliberately camelCase
        """Set multiple key-value pairs.

        Args:
            items: Dictionary of key-value pairs
            ttl: Time-to-live in seconds
        """
        for key, value in items.items():
            self.set(key, value, ttl)

    def get_keys(self, pattern: Optional[str] = None) -> list[str]:
        """Get all cache keys, optionally filtered by pattern.

        Args:
            pattern: Optional pattern to match (simple substring match)

        Returns:
            List of matching keys
        """
        if pattern is None:
            return list(self._cache.keys())

        return [key for key in self._cache.keys() if pattern in key]

    def get_size_estimate(self) -> int:
        """Get estimated cache size in bytes.

        Returns:
            Estimated size
        """
        # Simple estimation
        import sys

        total_size = 0

        for key, entry in self._cache.items():
            total_size += sys.getsizeof(key)
            total_size += sys.getsizeof(entry["value"])
            total_size += sys.getsizeof(entry)

        return total_size


# Global cache instance
_global_cache = CacheService()


def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]

            if args:
                key_parts.append(str(args))

            if kwargs:
                key_parts.append(str(sorted(kwargs.items())))

            cache_key = ":".join(key_parts)

            # Try to get from cache
            result = _global_cache.get(cache_key)

            if result is None:
                # Cache miss - call function
                result = func(*args, **kwargs)
                _global_cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


def invalidate_cache(pattern: str) -> int:
    """Invalidate cache entries matching pattern.

    Args:
        pattern: Pattern to match

    Returns:
        Number of entries invalidated
    """
    keys = _global_cache.get_keys(pattern)
    count = 0

    for key in keys:
        if _global_cache.delete(key):
            count += 1

    return count


def get_global_cache() -> CacheService:
    """Get the global cache instance.

    Returns:
        Global cache service
    """
    return _global_cache
