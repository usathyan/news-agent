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
