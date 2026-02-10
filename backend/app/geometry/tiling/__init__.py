"""
Manifold tiling module.

Tiles scaffold geometry onto curved 3D surfaces (sphere, ellipsoid, torus, cylinder).
Supports both surface tiling (shell) and volume filling modes.

Usage:
    from app.geometry.tiling import tile_scaffold_onto_surface, TilingParams, TargetShape

    params = TilingParams(
        target_shape=TargetShape.SPHERE,
        radius=10.0,
        num_tiles_u=4,
        num_tiles_v=4,
    )
    tiled, stats = tile_scaffold_onto_surface(scaffold_manifold, params)
"""

from .core import (
    tile_scaffold_onto_surface,
    TilingParams,
    TilingMode,
    TargetShape,
)

__all__ = [
    "tile_scaffold_onto_surface",
    "TilingParams",
    "TilingMode",
    "TargetShape",
]
