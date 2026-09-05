"""Intelligent response cache for YouTube API calls to preserve daily quota."""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Any, Callable, Dict, Optional


class ResponseCache:
    """Lightweight disk-based cache with TTL expiration for API responses."""

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        default_ttl: int = 3600,
        enabled: bool = True,
    ):
        self.enabled = enabled
        self.default_ttl = default_ttl

        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            env_dir = os.getenv("YOUTUBE_CACHE_DIR")
            if env_dir:
                self.cache_dir = Path(env_dir)
            else:
                self.cache_dir = Path.home() / ".cache" / "youtube_mcp"

        if self.enabled:
            try:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                # Fallback to current working directory cache
                self.cache_dir = Path(".cache_youtube_mcp")
                self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _hash_key(self, prefix: str, key_data: Any) -> str:
        """Generate a stable MD5 hash filename from prefix and arbitrary key arguments."""
        if isinstance(key_data, (dict, list)):
            serialized = json.dumps(key_data, sort_keys=True)
        else:
            serialized = str(key_data)
        hashed = hashlib.md5(serialized.encode("utf-8")).hexdigest()
        return f"{prefix}_{hashed}.json"

    def get(self, prefix: str, key_data: Any) -> Optional[Dict[str, Any]]:
        """Retrieve a cached entry if it exists and has not expired."""
        if not self.enabled:
            return None

        filename = self._hash_key(prefix, key_data)
        filepath = self.cache_dir / filename

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                entry = json.load(f)

            expires_at = entry.get("_expires_at", 0)
            if time.time() > expires_at:
                # Expired: clean up
                try:
                    filepath.unlink(missing_ok=True)
                except Exception:
                    pass
                return None

            data = entry.get("data")
            if isinstance(data, dict):
                data["_cached"] = True
                data["_cached_at"] = entry.get("_created_at")
            return data
        except Exception:
            return None

    def set(
        self,
        prefix: str,
        key_data: Any,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Write a value to the cache with an expiration timestamp."""
        if not self.enabled:
            return False

        filename = self._hash_key(prefix, key_data)
        filepath = self.cache_dir / filename
        ttl_seconds = ttl if ttl is not None else self.default_ttl

        now = time.time()
        entry = {
            "_created_at": now,
            "_expires_at": now + ttl_seconds,
            "data": value,
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(entry, f)
            return True
        except Exception:
            return False

    def clear(self) -> int:
        """Clear all cached files in the cache directory."""
        if not self.cache_dir.exists():
            return 0
        cleared = 0
        for p in self.cache_dir.glob("*.json"):
            try:
                p.unlink(missing_ok=True)
                cleared += 1
            except Exception:
                pass
        return cleared


# Singleton cache instance initialized from environment
_cache_instance: Optional[ResponseCache] = None


def get_cache() -> ResponseCache:
    """Retrieve or initialize the global ResponseCache."""
    global _cache_instance
    if _cache_instance is None:
        enabled = os.getenv("YOUTUBE_CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
        ttl = int(os.getenv("YOUTUBE_CACHE_TTL", "3600"))
        _cache_instance = ResponseCache(enabled=enabled, default_ttl=ttl)
    return _cache_instance
