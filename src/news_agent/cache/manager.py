import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Any, Optional
from news_agent.config.models import CachingConfig

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages file-based caching with TTL support"""

    def __init__(self, cache_dir: Path, config: CachingConfig):
        self.cache_dir = cache_dir
        self.config = config
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for given key using hash to prevent collisions"""
        # Use SHA256 hash to create safe, collision-resistant filenames
        key_hash = hashlib.sha256(key.encode('utf-8')).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def set(self, key: str, data: Any) -> None:
        """Store data in cache with current timestamp"""
        if not self.config.enabled:
            return

        try:
            cache_path = self._get_cache_path(key)
            cache_data = {
                "timestamp": time.time(),
                "data": data
            }

            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        except (TypeError, ValueError) as e:
            # JSON serialization error
            logger.warning(f"Failed to serialize cache data for key '{key}': {e}")
        except (IOError, OSError) as e:
            # File I/O error
            logger.warning(f"Failed to write cache file for key '{key}': {e}")
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error caching data for key '{key}': {e}")

    def get(self, key: str) -> Optional[Any]:
        """Retrieve data from cache if not expired"""
        if not self.config.enabled:
            return None

        try:
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
        except json.JSONDecodeError as e:
            # Corrupted JSON file
            logger.warning(f"Corrupted cache file for key '{key}': {e}")
            # Try to remove the corrupted file
            try:
                if cache_path.exists():
                    cache_path.unlink()
            except Exception:
                pass
            return None
        except KeyError as e:
            # Missing required keys in cache data
            logger.warning(f"Invalid cache data structure for key '{key}': missing {e}")
            return None
        except (IOError, OSError) as e:
            # File I/O error
            logger.warning(f"Failed to read cache file for key '{key}': {e}")
            return None
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error retrieving cache for key '{key}': {e}")
            return None

    def clear(self, key: Optional[str] = None) -> None:
        """Clear specific cache entry or all cache"""
        try:
            if key:
                # Clear specific cache entry
                cache_path = self._get_cache_path(key)
                if cache_path.exists():
                    cache_path.unlink()
            else:
                # Clear all cache entries
                for cache_file in self.cache_dir.glob("*.json"):
                    try:
                        cache_file.unlink()
                    except (IOError, OSError) as e:
                        logger.warning(f"Failed to delete cache file '{cache_file}': {e}")
        except (IOError, OSError) as e:
            # File deletion error
            logger.warning(f"Failed to clear cache for key '{key}': {e}")
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error clearing cache for key '{key}': {e}")
