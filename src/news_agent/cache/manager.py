import json
import time
from pathlib import Path
from typing import Any, Optional
from news_agent.config.models import CachingConfig


class CacheManager:
    """Manages file-based caching with TTL support"""

    def __init__(self, cache_dir: Path, config: CachingConfig):
        self.cache_dir = cache_dir
        self.config = config
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for given key"""
        # Use hash to avoid filesystem issues with special chars
        safe_key = key.replace('/', '_').replace(':', '_')
        return self.cache_dir / f"{safe_key}.json"

    def set(self, key: str, data: Any) -> None:
        """Store data in cache with current timestamp"""
        if not self.config.enabled:
            return

        cache_path = self._get_cache_path(key)
        cache_data = {
            "timestamp": time.time(),
            "data": data
        }

        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve data from cache if not expired"""
        if not self.config.enabled:
            return None

        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        with open(cache_path, 'r') as f:
            cache_data = json.load(f)

        # Check if expired
        age_hours = (time.time() - cache_data["timestamp"]) / 3600
        if age_hours > self.config.ttl_hours:
            cache_path.unlink()
            return None

        return cache_data["data"]

    def clear(self, key: Optional[str] = None) -> None:
        """Clear specific cache entry or all cache"""
        if key:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
        else:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
