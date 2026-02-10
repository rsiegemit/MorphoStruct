"""
Shared in-memory scaffold cache.

Stores generated manifold objects, STL bytes, and metadata
so they can be retrieved by scaffold_id for downstream operations
like tiling, export, etc.

In production, replace with Redis or a proper cache.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

_scaffold_cache: Dict[str, Tuple[object, bytes, Dict[str, Any]]] = {}
_CACHE_MAX_SIZE = 50


def cache_scaffold(
    scaffold_id: str,
    manifold: object,
    stl_bytes: bytes,
    metadata: Dict[str, Any],
) -> None:
    """Cache a generated scaffold with LRU-like eviction."""
    if len(_scaffold_cache) >= _CACHE_MAX_SIZE:
        oldest_key = next(iter(_scaffold_cache))
        del _scaffold_cache[oldest_key]

    _scaffold_cache[scaffold_id] = (manifold, stl_bytes, metadata)


def get_scaffold(scaffold_id: str) -> Optional[Tuple[object, bytes, Dict[str, Any]]]:
    """Retrieve a cached scaffold by ID. Returns None if not found."""
    return _scaffold_cache.get(scaffold_id)


def has_scaffold(scaffold_id: str) -> bool:
    """Check if a scaffold is in cache."""
    return scaffold_id in _scaffold_cache


def remove_scaffold(scaffold_id: str) -> bool:
    """Remove a scaffold from cache. Returns True if it existed."""
    if scaffold_id in _scaffold_cache:
        del _scaffold_cache[scaffold_id]
        return True
    return False


def cache_size() -> int:
    """Return number of cached scaffolds."""
    return len(_scaffold_cache)
