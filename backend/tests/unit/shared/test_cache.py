"""Tests unitaires pour le module de cache."""

import pytest
import time
from unittest.mock import MagicMock

from shared.infrastructure.cache import TTLCache, ttl_cache, make_cache_key


class TestTTLCache:
    """Tests pour la classe TTLCache."""

    @pytest.fixture
    def cache(self):
        """Cree un cache pour les tests."""
        return TTLCache(max_size=10)

    def test_set_and_get(self, cache):
        """Test set et get basiques."""
        cache.set("key1", "value1", ttl=60)
        result = cache.get("key1")
        assert result == "value1"

    def test_get_nonexistent_key(self, cache):
        """Test get pour une cle inexistante retourne None."""
        result = cache.get("nonexistent")
        assert result is None

    def test_ttl_expiration(self, cache):
        """Test que les entrees expirent apres TTL."""
        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"

        # Attendre que le TTL expire
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_delete(self, cache):
        """Test suppression d'une cle."""
        cache.set("key1", "value1", ttl=60)
        assert cache.get("key1") == "value1"

        result = cache.delete("key1")
        assert result is True
        assert cache.get("key1") is None

    def test_delete_nonexistent(self, cache):
        """Test suppression d'une cle inexistante."""
        result = cache.delete("nonexistent")
        assert result is False

    def test_invalidate_pattern(self, cache):
        """Test invalidation par pattern."""
        cache.set("prefix:key1", "value1", ttl=60)
        cache.set("prefix:key2", "value2", ttl=60)
        cache.set("other:key3", "value3", ttl=60)

        count = cache.invalidate_pattern("prefix:")
        assert count == 2
        assert cache.get("prefix:key1") is None
        assert cache.get("prefix:key2") is None
        assert cache.get("other:key3") == "value3"

    def test_clear(self, cache):
        """Test vidage complet du cache."""
        cache.set("key1", "value1", ttl=60)
        cache.set("key2", "value2", ttl=60)

        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_max_size_eviction(self):
        """Test eviction quand max_size est atteint."""
        cache = TTLCache(max_size=5)

        # Remplir le cache
        for i in range(10):
            cache.set(f"key{i}", f"value{i}", ttl=60)

        # Verifier que le cache ne depasse pas max_size
        assert len(cache._cache) <= 5

    def test_thread_safety(self, cache):
        """Test que le cache est thread-safe."""
        import threading

        def add_values():
            for i in range(100):
                cache.set(f"thread_{threading.current_thread().name}_{i}", i, ttl=60)

        threads = [threading.Thread(target=add_values) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Le cache devrait avoir des entrees (peut avoir evicte certaines)
        assert len(cache._cache) > 0


class TestMakeCacheKey:
    """Tests pour la fonction make_cache_key."""

    def test_same_args_same_key(self):
        """Test que les memes args donnent la meme cle."""
        key1 = make_cache_key("arg1", "arg2", kwarg1="val1")
        key2 = make_cache_key("arg1", "arg2", kwarg1="val1")
        assert key1 == key2

    def test_different_args_different_key(self):
        """Test que des args differents donnent des cles differentes."""
        key1 = make_cache_key("arg1", "arg2")
        key2 = make_cache_key("arg1", "arg3")
        assert key1 != key2

    def test_kwargs_order_independent(self):
        """Test que l'ordre des kwargs n'affecte pas la cle."""
        key1 = make_cache_key(kwarg1="val1", kwarg2="val2")
        key2 = make_cache_key(kwarg2="val2", kwarg1="val1")
        assert key1 == key2


class TestTTLCacheDecorator:
    """Tests pour le decorateur ttl_cache."""

    def test_caches_result(self):
        """Test que le resultat est mis en cache."""
        call_count = 0

        @ttl_cache(ttl_seconds=60, key_prefix="test")
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Premier appel
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Deuxieme appel (depuis le cache)
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Pas d'appel supplementaire

    def test_different_args_not_cached_together(self):
        """Test que des args differents ont des caches separes."""
        call_count = 0

        @ttl_cache(ttl_seconds=60, key_prefix="test2")
        def func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        func(5)
        func(10)
        assert call_count == 2

    def test_invalidate_cache(self):
        """Test invalidation du cache via la methode wrapper."""
        call_count = 0

        @ttl_cache(ttl_seconds=60, key_prefix="test3")
        def func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Premier appel
        func(5)
        assert call_count == 1

        # Invalider le cache
        func.invalidate_cache()

        # Deuxieme appel (pas depuis le cache)
        func(5)
        assert call_count == 2
