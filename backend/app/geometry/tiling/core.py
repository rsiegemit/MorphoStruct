"""
Core manifold tiling engine.

Takes any scaffold manifold and tiles it onto curved 3D surfaces.
Supports surface tiling (shell) and volume filling modes.

Algorithm:
    1. Tile scaffold in flat XY plane (num_u x num_v copies)
    2. Refine mesh for smooth warping (refine_to_length)
    3. Normalise flat grid to parametric UV space of target surface
    4. Apply vectorised warp_batch to map onto curved surface
    5. For volume mode: create multiple radial layers and union them
"""

from __future__ import annotations

import manifold3d as m3d
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Tuple, Optional

from ..core import batch_union
from .surfaces import (
    SphereParams,
    EllipsoidParams,
    TorusParams,
    CylinderParams,
    SuperellipsoidParams,
    make_sphere_warp,
    make_ellipsoid_warp,
    make_torus_warp,
    make_cylinder_warp,
    make_superellipsoid_warp,
    sphere_parametric_bounds,
    ellipsoid_parametric_bounds,
    torus_parametric_bounds,
    cylinder_parametric_bounds,
    superellipsoid_parametric_bounds,
)


class TargetShape(str, Enum):
    """Target surface shapes for tiling."""
    SPHERE = "sphere"
    ELLIPSOID = "ellipsoid"
    TORUS = "torus"
    CYLINDER = "cylinder"
    SUPERELLIPSOID = "superellipsoid"


class TilingMode(str, Enum):
    """How patches are placed."""
    SURFACE = "surface"  # shell on surface
    VOLUME = "volume"    # fill entire volume with layers


@dataclass
class TilingParams:
    """
    Configuration for manifold tiling.

    Attributes:
        target_shape: Which surface to tile onto
        mode: Surface shell vs volume filling

        Shape dimensions (used based on target_shape):
            radius: Sphere / cylinder radius (mm)
            radius_x/y/z: Ellipsoid / superellipsoid semi-axes (mm)
            major_radius, minor_radius: Torus radii (mm)
            height: Cylinder height (mm)
            exponent_n, exponent_e: Superellipsoid shape exponents

        Tiling layout:
            num_tiles_u: Repetitions in U parametric direction
            num_tiles_v: Repetitions in V parametric direction

        Volume mode:
            num_layers: Radial layers for volume filling
            layer_spacing_mm: Distance between layers

        Mesh refinement:
            refine_edge_length_mm: Max edge length before warping.
                Smaller = smoother but more triangles. Set to 0 to skip.
    """
    # Target surface
    target_shape: TargetShape = TargetShape.SPHERE
    mode: TilingMode = TilingMode.SURFACE

    # Shape dimensions
    radius: float = 10.0
    radius_x: float = 10.0
    radius_y: float = 8.0
    radius_z: float = 6.0
    major_radius: float = 15.0
    minor_radius: float = 5.0
    height: float = 20.0
    exponent_n: float = 1.0
    exponent_e: float = 1.0

    # Tiling layout
    num_tiles_u: int = 4
    num_tiles_v: int = 4

    # Volume mode
    num_layers: int = 1
    layer_spacing_mm: float = 1.0

    # Mesh quality
    refine_edge_length_mm: float = 0.5


def _get_scaffold_dims(scaffold: m3d.Manifold) -> Tuple[float, float, float]:
    """Get bounding box dimensions (width, depth, height) of a scaffold."""
    # bounding_box() returns flat tuple: (x_min, y_min, z_min, x_max, y_max, z_max)
    bb = scaffold.bounding_box()
    return (bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2])


def _get_scaffold_origin(scaffold: m3d.Manifold) -> Tuple[float, float, float]:
    """Get bounding box minimum corner."""
    bb = scaffold.bounding_box()
    return (bb[0], bb[1], bb[2])


def _estimate_avg_edge_length(manifold: m3d.Manifold) -> float:
    """Estimate average edge length from bounding box and triangle count."""
    dims = _get_scaffold_dims(manifold)
    tri_count = manifold.num_tri()
    if tri_count == 0:
        return 0.0
    # Rough estimate: average triangle area ~ bbox_area / tri_count
    # average edge ~ sqrt(2 * area)
    bbox_area = 2 * (dims[0] * dims[1] + dims[1] * dims[2] + dims[0] * dims[2])
    avg_tri_area = bbox_area / max(tri_count, 1)
    return max(np.sqrt(2 * avg_tri_area), 0.01)


def _tile_flat(
    scaffold: m3d.Manifold,
    num_u: int,
    num_v: int,
) -> m3d.Manifold:
    """
    Tile scaffold in flat XY plane, num_u x num_v copies.

    Tiles are placed edge-to-edge using the scaffold's bounding box
    dimensions. Boolean union ensures shared edges are seamless.
    """
    width, depth, _height = _get_scaffold_dims(scaffold)
    ox, oy, oz = _get_scaffold_origin(scaffold)

    # Centre the single unit at origin in XY
    centred = scaffold.translate([-ox - width / 2, -oy - depth / 2, -oz])

    tiles = []
    for i in range(num_u):
        for j in range(num_v):
            x_offset = (i - num_u / 2.0 + 0.5) * width
            y_offset = (j - num_v / 2.0 + 0.5) * depth
            tile = centred.translate([x_offset, y_offset, 0.0])
            tiles.append(tile)

    if len(tiles) == 1:
        return tiles[0]
    return batch_union(tiles)


def _normalise_to_uv(
    flat: m3d.Manifold,
    u_range: Tuple[float, float],
    v_range: Tuple[float, float],
) -> m3d.Manifold:
    """
    Scale and translate flat tiled pattern so that:
        x maps to [u_min, u_max]
        y maps to [v_min, v_max]
        z is preserved (thickness)

    This puts vertices into parametric space ready for the warp function.
    """
    bb = flat.bounding_box()
    x_min, y_min, z_min = bb[0], bb[1], bb[2]
    x_max, y_max = bb[3], bb[4]

    x_span = x_max - x_min
    y_span = y_max - y_min
    u_span = u_range[1] - u_range[0]
    v_span = v_range[1] - v_range[0]

    sx = u_span / x_span if x_span > 1e-12 else 1.0
    sy = v_span / y_span if y_span > 1e-12 else 1.0

    # Translate so min corner is at origin, then scale, then shift to u/v range
    result = flat.translate([-x_min, -y_min, -z_min])
    result = result.scale([sx, sy, 1.0])
    result = result.translate([u_range[0], v_range[0], z_min])

    return result


def _build_warp_func(
    params: TilingParams,
    layer_offset: float = 0.0,
) -> Callable[[np.ndarray], np.ndarray]:
    """
    Build the vectorised warp function for the target surface.

    Returns a function that takes ndarray[n, 3] and returns ndarray[n, 3].
    The layer_offset shifts the scaffold radially for volume filling.
    """
    shape = params.target_shape

    if shape == TargetShape.SPHERE:
        base_warp = make_sphere_warp(SphereParams(radius=params.radius))
    elif shape == TargetShape.ELLIPSOID:
        base_warp = make_ellipsoid_warp(EllipsoidParams(
            radius_x=params.radius_x,
            radius_y=params.radius_y,
            radius_z=params.radius_z,
        ))
    elif shape == TargetShape.TORUS:
        base_warp = make_torus_warp(TorusParams(
            major_radius=params.major_radius,
            minor_radius=params.minor_radius,
        ))
    elif shape == TargetShape.CYLINDER:
        base_warp = make_cylinder_warp(CylinderParams(
            radius=params.radius,
            height=params.height,
        ))
    elif shape == TargetShape.SUPERELLIPSOID:
        base_warp = make_superellipsoid_warp(SuperellipsoidParams(
            radius_x=params.radius_x,
            radius_y=params.radius_y,
            radius_z=params.radius_z,
            exponent_n=params.exponent_n,
            exponent_e=params.exponent_e,
        ))
    else:
        raise ValueError(f"Unsupported target shape: {shape}")

    if abs(layer_offset) < 1e-12:
        return base_warp

    # Wrap to add radial layer offset to z before warping
    def offset_warp(verts: np.ndarray) -> np.ndarray:
        shifted = verts.copy()
        shifted[:, 2] = shifted[:, 2] + layer_offset
        return base_warp(shifted)

    return offset_warp


def _get_parametric_bounds(
    params: TilingParams,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Get (u_range, v_range) for the target surface."""
    shape = params.target_shape

    if shape == TargetShape.SPHERE:
        return sphere_parametric_bounds(params.num_tiles_v)
    elif shape == TargetShape.ELLIPSOID:
        return ellipsoid_parametric_bounds(params.num_tiles_v)
    elif shape == TargetShape.TORUS:
        return torus_parametric_bounds()
    elif shape == TargetShape.CYLINDER:
        return cylinder_parametric_bounds(params.height)
    elif shape == TargetShape.SUPERELLIPSOID:
        return superellipsoid_parametric_bounds(params.num_tiles_v)
    else:
        raise ValueError(f"Unsupported target shape: {shape}")


def tile_scaffold_onto_surface(
    scaffold: m3d.Manifold,
    params: TilingParams,
) -> Tuple[m3d.Manifold, dict]:
    """
    Tile a scaffold onto a curved 3D surface.

    This is the main entry point for manifold tiling.

    Args:
        scaffold: Base scaffold unit (any manifold3d Manifold)
        params: Tiling configuration

    Returns:
        (tiled_manifold, stats_dict)

    Raises:
        ValueError: If parameters are invalid
    """
    # Validate
    if params.num_tiles_u < 1 or params.num_tiles_v < 1:
        raise ValueError("num_tiles_u and num_tiles_v must be >= 1")
    if params.mode == TilingMode.VOLUME and params.num_layers < 1:
        raise ValueError("num_layers must be >= 1 for volume mode")

    # Step 1: tile in flat XY plane
    flat_tiled = _tile_flat(scaffold, params.num_tiles_u, params.num_tiles_v)

    # Step 2: refine mesh for smooth warping
    # Safety: estimate vertex count to avoid memory exhaustion
    MAX_VERTICES = 5_000_000
    if params.refine_edge_length_mm > 0:
        pre_refine_tris = flat_tiled.num_tri()
        avg_edge = _estimate_avg_edge_length(flat_tiled)
        if avg_edge > 0:
            subdivisions = avg_edge / params.refine_edge_length_mm
            estimated_tris = int(pre_refine_tris * subdivisions * subdivisions)
            if estimated_tris > MAX_VERTICES:
                raise ValueError(
                    f"Refinement would create ~{estimated_tris:,} triangles "
                    f"(limit: {MAX_VERTICES:,}). "
                    f"Increase refine_edge_length_mm or reduce tile count."
                )
        flat_tiled = flat_tiled.refine_to_length(params.refine_edge_length_mm)

    # Step 3: normalise to parametric UV space
    u_range, v_range = _get_parametric_bounds(params)
    uv_normalised = _normalise_to_uv(flat_tiled, u_range, v_range)

    # Step 4: warp onto surface
    warp_fn = _build_warp_func(params, layer_offset=0.0)
    surface_layer = uv_normalised.warp_batch(warp_fn)

    # Step 5: volume filling (multiple radial layers)
    # Layers are distributed symmetrically around the surface:
    #   num_layers=1 -> [0]
    #   num_layers=2 -> [0, +spacing]
    #   num_layers=3 -> [-spacing, 0, +spacing]
    #   num_layers=4 -> [-1.5*s, -0.5*s, +0.5*s, +1.5*s]
    if params.mode == TilingMode.VOLUME and params.num_layers > 1:
        spacing = params.layer_spacing_mm
        offsets = [
            (i - (params.num_layers - 1) / 2.0) * spacing
            for i in range(params.num_layers)
        ]

        layers = []
        for offset in offsets:
            layer_warp = _build_warp_func(params, layer_offset=offset)
            layer = uv_normalised.warp_batch(layer_warp)
            layers.append(layer)

        result = batch_union(layers)
    else:
        result = surface_layer

    # Compute stats
    mesh = result.to_mesh()
    tri_count = len(np.array(mesh.tri_verts))
    volume = result.volume()

    stats = {
        "triangle_count": tri_count,
        "volume_mm3": abs(volume),
        "scaffold_type": "tiled_scaffold",
        "target_shape": params.target_shape.value,
        "tiling_mode": params.mode.value,
        "num_tiles_u": params.num_tiles_u,
        "num_tiles_v": params.num_tiles_v,
        "num_layers": params.num_layers if params.mode == TilingMode.VOLUME else 1,
        "total_patches": params.num_tiles_u * params.num_tiles_v,
    }

    return result, stats
