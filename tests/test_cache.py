"""Unit tests for response caching."""

import time
import pytest
from pathlib import Path
from youtube_mcp.cache import ResponseCache


def test_cache_set_and_get(tmp_path):
    cache = ResponseCache(cache_dir=str(tmp_path), default_ttl=3600, enabled=True)
    
    key = {"query": "python tutorial", "max_results": 10}
    payload = {"success": True, "results": [{"title": "Learn Python"}]}

    # Initially not in cache
    assert cache.get("search", key) is None

    # Set cache
    assert cache.set("search", key, payload) is True

    # Retrieve from cache
    cached = cache.get("search", key)
    assert cached is not None
    assert cached["success"] is True
    assert cached["_cached"] is True
    assert cached["results"][0]["title"] == "Learn Python"


def test_cache_expiration(tmp_path):
    # TTL of 1 second
    cache = ResponseCache(cache_dir=str(tmp_path), default_ttl=1, enabled=True)
    
    key = "test_key"
    payload = {"data": 123}

    cache.set("test", key, payload, ttl=1)
    assert cache.get("test", key) is not None

    # Wait for expiration
    time.sleep(1.1)
    assert cache.get("test", key) is None


def test_cache_disabled(tmp_path):
    cache = ResponseCache(cache_dir=str(tmp_path), enabled=False)
    
    key = "disabled_key"
    payload = {"data": 456}

    assert cache.set("test", key, payload) is False
    assert cache.get("test", key) is None


def test_cache_clear(tmp_path):
    cache = ResponseCache(cache_dir=str(tmp_path), enabled=True)
    cache.set("a", "1", {"val": 1})
    cache.set("b", "2", {"val": 2})

    cleared = cache.clear()
    assert cleared == 2
    assert cache.get("a", "1") is None
