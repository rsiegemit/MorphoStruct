"""
Haversian bone scaffold generator with cortical bone microstructure.

Creates a solid cortical bone structure with longitudinal vascular channels
(Haversian canals) arranged in osteon patterns (hexagonal or random).
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from typing import Literal
from ..core import batch_union


@dataclass
class HaversianBoneParams:
    """Parameters for Haversian bone scaffold generation."""
    canal_diameter_um: float = 50.0
    canal_spacing_um: float = 400.0
    cortical_thickness: float = 5.0
    osteon_pattern: Literal['hexagonal', 'random'] = 'hexagonal'
    bounding_box: tuple[float, float, float] = (5.0, 5.0, 8.0)
    resolution: int = 8


def generate_haversian_bone(params: HaversianBoneParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a Haversian bone scaffold with osteon structure.

    Creates cortical bone with longitudinal vascular channels:
    - Solid cortical matrix
    - Haversian canals aligned along Z-axis (bone length)
    - Osteons arranged in hexagonal or random pattern

    Args:
        params: HaversianBoneParams specifying geometry and structure

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, canal_count,
                     osteon_pattern, scaffold_type
    """
    bx, by, bz = params.bounding_box
    canal_radius = params.canal_diameter_um / 2000.0  # Convert µm to mm
    canal_spacing = params.canal_spacing_um / 1000.0  # Convert µm to mm

    # Create base solid block
    base = m3d.Manifold.cube([bx, by, bz])

    # Generate canal positions based on pattern
    if params.osteon_pattern == 'hexagonal':
        canal_positions = generate_hexagonal_pattern(
            width=bx,
            depth=by,
            spacing=canal_spacing
        )
    else:  # random
        canal_positions = generate_random_pattern(
            width=bx,
            depth=by,
            spacing=canal_spacing
        )

    # Create Haversian canals (vertical cylinders)
    canals = []
    for x, y in canal_positions:
        # Check if position is within bounds
        if 0 < x < bx and 0 < y < by:
            canal = m3d.Manifold.cylinder(bz, canal_radius, canal_radius, params.resolution)
            canal = canal.translate([x, y, 0])
            canals.append(canal)

    # Subtract canals from solid base
    result = base
    for canal in canals:
        result = result - canal

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'canal_count': len(canals),
        'osteon_pattern': params.osteon_pattern,
        'porosity': 1.0 - (volume / (bx * by * bz)),
        'scaffold_type': 'haversian_bone'
    }

    return result, stats


def generate_hexagonal_pattern(
    width: float,
    depth: float,
    spacing: float
) -> list[tuple[float, float]]:
    """
    Generate hexagonal close-packed positions for osteons.

    Args:
        width: Width of region (X)
        depth: Depth of region (Y)
        spacing: Distance between osteon centers

    Returns:
        List of (x, y) positions
    """
    positions = []

    # Hexagonal grid parameters
    row_height = spacing * np.sqrt(3) / 2
    n_rows = int(depth / row_height) + 2
    n_cols = int(width / spacing) + 2

    for row in range(n_rows):
        y = row * row_height

        for col in range(n_cols):
            # Offset every other row for hexagonal packing
            x_offset = (spacing / 2) if (row % 2 == 1) else 0
            x = col * spacing + x_offset

            positions.append((x, y))

    return positions


def generate_random_pattern(
    width: float,
    depth: float,
    spacing: float
) -> list[tuple[float, float]]:
    """
    Generate random positions for osteons with minimum spacing constraint.

    Args:
        width: Width of region (X)
        depth: Depth of region (Y)
        spacing: Minimum distance between osteon centers

    Returns:
        List of (x, y) positions
    """
    positions = []

    # Estimate number of canals based on area and spacing
    area = width * depth
    canal_area = spacing ** 2
    n_canals = int(area / canal_area * 0.8)  # 80% packing efficiency

    # Generate random positions with minimum spacing
    max_attempts = n_canals * 10
    attempts = 0

    while len(positions) < n_canals and attempts < max_attempts:
        x = np.random.uniform(0, width)
        y = np.random.uniform(0, depth)

        # Check minimum distance to existing positions
        valid = True
        for px, py in positions:
            dist = np.sqrt((x - px)**2 + (y - py)**2)
            if dist < spacing * 0.9:  # 90% of spacing for slight overlap
                valid = False
                break

        if valid:
            positions.append((x, y))

        attempts += 1

    return positions


def generate_haversian_bone_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate Haversian bone from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching HaversianBoneParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    bbox = params.get('bounding_box', (10, 10, 15))
    if isinstance(bbox, dict):
        bbox = (bbox['x'], bbox['y'], bbox['z'])

    return generate_haversian_bone(HaversianBoneParams(
        canal_diameter_um=params.get('canal_diameter_um', 50.0),
        canal_spacing_um=params.get('canal_spacing_um', 400.0),
        cortical_thickness=params.get('cortical_thickness', 5.0),
        osteon_pattern=params.get('osteon_pattern', 'hexagonal'),
        bounding_box=tuple(bbox),
        resolution=params.get('resolution', 8)
    ))
