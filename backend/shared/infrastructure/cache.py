"""Simple in-memory cache with TTL support.

This module provides a lightweight caching solution for read-heavy endpoints.
It can be replaced with Redis in the future for distributed caching.

Usage:
    from shared.infrastructure.cache import ttl_cache, cache_manager

    # Use decorator for simple caching
    @ttl_cache(ttl_seconds=60)
    def get_planning_charge(filters):
        ...

    # Or use cache manager directly
    result = cache_manager.get(key)
    if result is None:
        result = compute_expensive_result()
        cache_manager.set(key, result, ttl=60)
"""

import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple
from threading import Lock
import hashlib
import json


class TTLCache:
    """Thread-safe in-memory cache with TTL support."""

    def __init__(self, max_size: int = 1000):
        """
        Initialize the cache.

        Args:
            max_size: Maximum number of entries (LRU eviction when exceeded).
        """
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = Lock()
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key.

        Returns:
            Cached value or None if not found or expired.
        """
        with self._lock:
            if key not in self._cache:
                return None

            value, expires_at = self._cache[key]
            if time.time() > expires_at:
                # Expired
                del self._cache[key]
                return None

            return value

    def set(self, key: str, value: Any, ttl: int = 60) -> None:
        """
        Set a value in the cache.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time to live in seconds (default: 60).
        """
        with self._lock:
            # Simple LRU: remove oldest entries if cache is full
            if len(self._cache) >= self._max_size:
                self._evict_expired_and_oldest()

            expires_at = time.time() + ttl
            self._cache[key] = (value, expires_at)

    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.

        Args:
            key: Cache key.

        Returns:
            True if key was deleted, False if not found.
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.

        Args:
            pattern: Key prefix to match.

        Returns:
            Number of keys invalidated.
        """
        with self._lock:
            keys_to_delete = [k for k in self._cache if k.startswith(pattern)]
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete)

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()

    def _evict_expired_and_oldest(self) -> None:
        """Remove expired entries and oldest entries if still over limit."""
        now = time.time()
        # Remove expired
        expired_keys = [k for k, (_, exp) in self._cache.items() if exp < now]
        for key in expired_keys:
            del self._cache[key]

        # If still over limit, remove 10% oldest
        if len(self._cache) >= self._max_size:
            sorted_keys = sorted(
                self._cache.keys(),
                key=lambda k: self._cache[k][1]  # Sort by expiry time
            )
            to_remove = max(1, len(sorted_keys) // 10)
            for key in sorted_keys[:to_remove]:
                del self._cache[key]


# Global cache instance
cache_manager = TTLCache(max_size=500)


def make_cache_key(*args, **kwargs) -> str:
    """
    Create a cache key from function arguments.

    Args:
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Returns:
        MD5 hash of the arguments as cache key.
    """
    # Convert args and kwargs to a stable string representation
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    key_string = "|".join(key_parts)

    return hashlib.md5(key_string.encode()).hexdigest()


def ttl_cache(
    ttl_seconds: int = 60,
    key_prefix: str = "",
    include_args: bool = True,
):
    """
    Decorator for caching function results with TTL.

    Args:
        ttl_seconds: Cache TTL in seconds.
        key_prefix: Optional prefix for cache keys.
        include_args: Whether to include args in cache key (default True).

    Returns:
        Decorator function.

    Example:
        @ttl_cache(ttl_seconds=300, key_prefix="planning")
        def get_planning_charge(filters: dict):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            if include_args:
                arg_key = make_cache_key(*args, **kwargs)
            else:
                arg_key = ""

            prefix = key_prefix or func.__name__
            cache_key = f"{prefix}:{arg_key}" if arg_key else prefix

            # Check cache
            cached = cache_manager.get(cache_key)
            if cached is not None:
                return cached

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache_manager.set(cache_key, result, ttl=ttl_seconds)

            return result

        # Add method to invalidate cache
        wrapper.invalidate_cache = lambda: cache_manager.invalidate_pattern(
            key_prefix or func.__name__
        )

        return wrapper

    return decorator
