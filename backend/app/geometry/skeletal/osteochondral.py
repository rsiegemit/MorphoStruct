"""
Osteochondral scaffold generator with gradient structure.

Creates a multi-layer scaffold transitioning from bone to calcified cartilage
to cartilage, with gradient porosity matching native osteochondral tissue.
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from typing import Literal


@dataclass
class OsteochondralParams:
    """Parameters for osteochondral scaffold generation."""
    bone_depth: float = 3.0
    cartilage_depth: float = 2.0
    transition_width: float = 1.0
    gradient_type: Literal['linear', 'exponential'] = 'linear'
    diameter: float = 8.0
    resolution: int = 16
    bone_porosity: float = 0.7
    cartilage_porosity: float = 0.85


def generate_osteochondral(params: OsteochondralParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate an osteochondral scaffold with gradient structure.

    Creates three zones:
    1. Bone zone (bottom) - higher density
    2. Transition zone (middle) - gradient density
    3. Cartilage zone (top) - lower density

    Uses layered cylinders with varying pore patterns to simulate gradient porosity.

    Args:
        params: OsteochondralParams specifying geometry and structure

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, layer_count,
                     bone_volume, cartilage_volume, scaffold_type
    """
    total_height = params.bone_depth + params.transition_width + params.cartilage_depth
    radius = params.diameter / 2

    # Create base cylinder
    base = m3d.Manifold.cylinder(total_height, radius, radius, params.resolution)

    # Create pores in different zones
    pore_manifolds = []

    # Bone zone - smaller, denser pores
    bone_pore_radius = 0.3
    bone_pore_spacing = 1.0
    pore_manifolds.extend(create_zone_pores(
        z_start=0,
        z_end=params.bone_depth,
        radius=radius,
        pore_radius=bone_pore_radius,
        pore_spacing=bone_pore_spacing,
        porosity=params.bone_porosity,
        resolution=params.resolution
    ))

    # Transition zone - gradient pores
    transition_layers = 5
    for i in range(transition_layers):
        t = i / (transition_layers - 1) if transition_layers > 1 else 0.5
        if params.gradient_type == 'exponential':
            t = t ** 2

        z_start = params.bone_depth + i * (params.transition_width / transition_layers)
        z_end = z_start + (params.transition_width / transition_layers)

        # Interpolate pore characteristics
        pore_radius = bone_pore_radius + t * (0.5 - bone_pore_radius)
        pore_spacing = bone_pore_spacing + t * (1.5 - bone_pore_spacing)
        layer_porosity = params.bone_porosity + t * (params.cartilage_porosity - params.bone_porosity)

        pore_manifolds.extend(create_zone_pores(
            z_start=z_start,
            z_end=z_end,
            radius=radius,
            pore_radius=pore_radius,
            pore_spacing=pore_spacing,
            porosity=layer_porosity,
            resolution=params.resolution
        ))

    # Cartilage zone - larger, sparser pores
    cartilage_pore_radius = 0.5
    cartilage_pore_spacing = 1.5
    pore_manifolds.extend(create_zone_pores(
        z_start=params.bone_depth + params.transition_width,
        z_end=total_height,
        radius=radius,
        pore_radius=cartilage_pore_radius,
        pore_spacing=cartilage_pore_spacing,
        porosity=params.cartilage_porosity,
        resolution=params.resolution
    ))

    # Subtract pores from base
    result = base
    for pore in pore_manifolds:
        result = result - pore

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    # Calculate volumes by zone (approximate)
    bone_volume = volume * (params.bone_depth / total_height)
    cartilage_volume = volume * (params.cartilage_depth / total_height)

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'layer_count': 3,
        'bone_volume_mm3': bone_volume,
        'cartilage_volume_mm3': cartilage_volume,
        'pore_count': len(pore_manifolds),
        'scaffold_type': 'osteochondral'
    }

    return result, stats


def create_zone_pores(
    z_start: float,
    z_end: float,
    radius: float,
    pore_radius: float,
    pore_spacing: float,
    porosity: float,
    resolution: int
) -> list[m3d.Manifold]:
    """
    Create pores for a specific zone.

    Args:
        z_start: Start height of zone
        z_end: End height of zone
        radius: Outer radius of scaffold
        pore_radius: Radius of individual pores
        pore_spacing: Spacing between pore centers
        porosity: Target porosity for this zone
        resolution: Angular resolution

    Returns:
        List of pore manifolds
    """
    pores = []
    z_height = z_end - z_start

    # Calculate radial and angular distribution
    n_radial = max(1, int(radius / pore_spacing))
    n_vertical = max(1, int(z_height / pore_spacing))

    # Adjust density based on porosity
    density_factor = porosity / 0.7  # Normalized to reference porosity

    for i in range(n_radial):
        r = (i + 0.5) * (radius / n_radial) * 0.8  # Stay within bounds
        circumference = 2 * np.pi * r
        n_angular = max(3, int(circumference / pore_spacing * density_factor))

        for j in range(n_angular):
            angle = j * 2 * np.pi / n_angular

            for k in range(n_vertical):
                z = z_start + (k + 0.5) * (z_height / n_vertical)

                # Pore position
                x = r * np.cos(angle)
                y = r * np.sin(angle)

                # Create spherical pore
                pore = m3d.Manifold.sphere(pore_radius, resolution)
                pore = pore.translate([x, y, z])
                pores.append(pore)

    return pores


def generate_osteochondral_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate osteochondral scaffold from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching OsteochondralParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_osteochondral(OsteochondralParams(
        bone_depth=params.get('bone_depth', 3.0),
        cartilage_depth=params.get('cartilage_depth', 2.0),
        transition_width=params.get('transition_width', 1.0),
        gradient_type=params.get('gradient_type', 'linear'),
        diameter=params.get('diameter', 8.0),
        resolution=params.get('resolution', 16),
        bone_porosity=params.get('bone_porosity', 0.7),
        cartilage_porosity=params.get('cartilage_porosity', 0.85)
    ))
