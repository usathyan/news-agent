import tempfile
from pathlib import Path
import json
import time
import pytest
from news_agent.cache.manager import CacheManager
from news_agent.config.models import CachingConfig


@pytest.fixture
def cache_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def cache_config():
    return CachingConfig(enabled=True, ttl_hours=1)


def test_cache_set_and_get(cache_dir, cache_config):
    """Test setting and getting cached data"""
    cache = CacheManager(cache_dir, cache_config)

    test_data = {"key": "value", "items": [1, 2, 3]}
    cache.set("test_key", test_data)

    retrieved = cache.get("test_key")
    assert retrieved == test_data


def test_cache_expiration(cache_dir):
    """Test cache expires after TTL"""
    # Set very short TTL for testing
    config = CachingConfig(enabled=True, ttl_hours=1)
    cache = CacheManager(cache_dir, config)

    # Set cache with old timestamp
    cache_path = cache._get_cache_path("test_key")
    old_cache_data = {
        "timestamp": time.time() - (2 * 3600),  # 2 hours ago
        "data": {"data": "value"}
    }
    with open(cache_path, 'w') as f:
        json.dump(old_cache_data, f)

    # Should be expired
    assert cache.get("test_key") is None


def test_cache_disabled(cache_dir):
    """Test cache returns None when disabled"""
    config = CachingConfig(enabled=False, ttl_hours=1)
    cache = CacheManager(cache_dir, config)

    cache.set("test_key", {"data": "value"})
    assert cache.get("test_key") is None


def test_corrupted_cache_file(cache_dir, cache_config):
    """Test handling of corrupted cache files"""
    cache = CacheManager(cache_dir, cache_config)

    # Create a corrupted cache file
    cache_path = cache._get_cache_path("test_key")
    with open(cache_path, 'w') as f:
        f.write("not valid json{]")

    # Should return None and handle gracefully
    result = cache.get("test_key")
    assert result is None


def test_non_json_serializable_data(cache_dir, cache_config):
    """Test handling of non-JSON-serializable data"""
    cache = CacheManager(cache_dir, cache_config)

    # Try to cache non-serializable data (e.g., a function)
    def test_function():
        pass

    # Should handle gracefully without raising exception
    cache.set("test_key", test_function)

    # Should return None since it couldn't be cached
    result = cache.get("test_key")
    assert result is None


def test_clear_specific_key(cache_dir, cache_config):
    """Test clearing a specific cache entry"""
    cache = CacheManager(cache_dir, cache_config)

    # Set multiple cache entries
    cache.set("key1", {"data": "value1"})
    cache.set("key2", {"data": "value2"})
    cache.set("key3", {"data": "value3"})

    # Clear only key2
    cache.clear("key2")

    # key2 should be gone, others should remain
    assert cache.get("key1") == {"data": "value1"}
    assert cache.get("key2") is None
    assert cache.get("key3") == {"data": "value3"}


def test_clear_all_cache(cache_dir, cache_config):
    """Test clearing all cache entries"""
    cache = CacheManager(cache_dir, cache_config)

    # Set multiple cache entries
    cache.set("key1", {"data": "value1"})
    cache.set("key2", {"data": "value2"})
    cache.set("key3", {"data": "value3"})

    # Clear all cache
    cache.clear()

    # All entries should be gone
    assert cache.get("key1") is None
    assert cache.get("key2") is None
    assert cache.get("key3") is None


def test_cache_missing_data_key(cache_dir, cache_config):
    """Test handling of cache files with missing 'data' key"""
    cache = CacheManager(cache_dir, cache_config)

    # Create a cache file with missing 'data' key
    cache_path = cache._get_cache_path("test_key")
    invalid_cache_data = {
        "timestamp": time.time()
        # Missing 'data' key
    }
    with open(cache_path, 'w') as f:
        json.dump(invalid_cache_data, f)

    # Should return None and handle gracefully
    result = cache.get("test_key")
    assert result is None
