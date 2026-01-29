"""
Articular cartilage scaffold generator with zonal architecture.

Creates a three-zone scaffold mimicking native articular cartilage:
- Superficial zone: tangential collagen orientation, small pores
- Middle zone: random orientation, medium pores
- Deep zone: perpendicular orientation, large pores
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass


@dataclass
class ArticularCartilageParams:
    """Parameters for articular cartilage scaffold generation."""
    total_thickness: float = 2.0
    zone_ratios: tuple[float, float, float] = (0.2, 0.4, 0.4)  # superficial, middle, deep
    pore_gradient: tuple[float, float, float] = (0.15, 0.25, 0.35)  # pore radius per zone
    diameter: float = 8.0
    resolution: int = 16


def generate_articular_cartilage(params: ArticularCartilageParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate an articular cartilage scaffold with zonal architecture.

    Creates three distinct zones with varying pore characteristics:
    1. Superficial zone (top) - small pores, tangential orientation
    2. Middle zone - medium pores, random orientation
    3. Deep zone (bottom) - large pores, perpendicular orientation

    Args:
        params: ArticularCartilageParams specifying geometry and structure

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, zone_count,
                     zone_thicknesses, scaffold_type
    """
    radius = params.diameter / 2
    total_height = params.total_thickness

    # Normalize zone ratios
    total_ratio = sum(params.zone_ratios)
    zone_ratios = [r / total_ratio for r in params.zone_ratios]

    # Calculate zone thicknesses
    zone_thicknesses = [r * total_height for r in zone_ratios]

    # Create base cylinder
    base = m3d.Manifold.cylinder(total_height, radius, radius, params.resolution)

    # Create pores for each zone
    all_pores = []
    z_current = 0

    # Deep zone (bottom) - vertical channels
    deep_thickness = zone_thicknesses[2]
    deep_pores = create_deep_zone_pores(
        z_start=z_current,
        z_end=z_current + deep_thickness,
        radius=radius,
        pore_radius=params.pore_gradient[2],
        resolution=params.resolution
    )
    all_pores.extend(deep_pores)
    z_current += deep_thickness

    # Middle zone - random spherical pores
    middle_thickness = zone_thicknesses[1]
    middle_pores = create_middle_zone_pores(
        z_start=z_current,
        z_end=z_current + middle_thickness,
        radius=radius,
        pore_radius=params.pore_gradient[1],
        resolution=params.resolution
    )
    all_pores.extend(middle_pores)
    z_current += middle_thickness

    # Superficial zone (top) - horizontal channels
    superficial_thickness = zone_thicknesses[0]
    superficial_pores = create_superficial_zone_pores(
        z_start=z_current,
        z_end=z_current + superficial_thickness,
        radius=radius,
        pore_radius=params.pore_gradient[0],
        resolution=params.resolution
    )
    all_pores.extend(superficial_pores)

    # Subtract pores from base
    result = base
    for pore in all_pores:
        result = result - pore

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'zone_count': 3,
        'zone_thicknesses_mm': zone_thicknesses,
        'pore_count': len(all_pores),
        'scaffold_type': 'articular_cartilage'
    }

    return result, stats


def create_deep_zone_pores(
    z_start: float,
    z_end: float,
    radius: float,
    pore_radius: float,
    resolution: int
) -> list[m3d.Manifold]:
    """
    Create vertical channels for deep zone (perpendicular to surface).

    Args:
        z_start: Start height of zone
        z_end: End height of zone
        radius: Outer radius of scaffold
        pore_radius: Radius of pore channels
        resolution: Angular resolution

    Returns:
        List of pore manifolds
    """
    pores = []
    height = z_end - z_start
    spacing = pore_radius * 4  # Spacing between channels

    n_radial = max(1, int(radius / spacing))

    for i in range(n_radial):
        r = (i + 0.5) * (radius / n_radial) * 0.8
        circumference = 2 * np.pi * r
        n_angular = max(3, int(circumference / spacing))

        for j in range(n_angular):
            angle = j * 2 * np.pi / n_angular
            x = r * np.cos(angle)
            y = r * np.sin(angle)

            # Vertical cylinder
            pore = m3d.Manifold.cylinder(height, pore_radius, pore_radius, resolution)
            pore = pore.translate([x, y, z_start])
            pores.append(pore)

    return pores


def create_middle_zone_pores(
    z_start: float,
    z_end: float,
    radius: float,
    pore_radius: float,
    resolution: int
) -> list[m3d.Manifold]:
    """
    Create random spherical pores for middle zone.

    Args:
        z_start: Start height of zone
        z_end: End height of zone
        radius: Outer radius of scaffold
        pore_radius: Radius of spherical pores
        resolution: Angular resolution

    Returns:
        List of pore manifolds
    """
    pores = []
    height = z_end - z_start
    spacing = pore_radius * 3

    n_radial = max(1, int(radius / spacing))
    n_vertical = max(1, int(height / spacing))

    for i in range(n_radial):
        r = (i + 0.5) * (radius / n_radial) * 0.8
        circumference = 2 * np.pi * r
        n_angular = max(3, int(circumference / spacing))

        for j in range(n_angular):
            angle = j * 2 * np.pi / n_angular

            for k in range(n_vertical):
                x = r * np.cos(angle)
                y = r * np.sin(angle)
                z = z_start + (k + 0.5) * (height / n_vertical)

                # Spherical pore
                pore = m3d.Manifold.sphere(pore_radius, resolution)
                pore = pore.translate([x, y, z])
                pores.append(pore)

    return pores


def create_superficial_zone_pores(
    z_start: float,
    z_end: float,
    radius: float,
    pore_radius: float,
    resolution: int
) -> list[m3d.Manifold]:
    """
    Create tangential (horizontal) channels for superficial zone.

    Args:
        z_start: Start height of zone
        z_end: End height of zone
        radius: Outer radius of scaffold
        pore_radius: Radius of pore channels
        resolution: Angular resolution

    Returns:
        List of pore manifolds
    """
    pores = []
    height = z_end - z_start
    spacing = pore_radius * 3
    n_layers = max(2, int(height / spacing))

    for layer in range(n_layers):
        z = z_start + (layer + 0.5) * (height / n_layers)

        # Radial channels at this height
        n_radial = 8  # Number of radial channels
        for i in range(n_radial):
            angle = i * 2 * np.pi / n_radial

            # Channel from center to edge
            length = radius * 0.8
            cylinder = m3d.Manifold.cylinder(length, pore_radius, pore_radius, resolution)

            # Rotate to horizontal and point outward
            cylinder = cylinder.rotate([0, 90, 0])  # Make horizontal
            cylinder = cylinder.rotate([0, 0, angle * 180 / np.pi])  # Rotate around Z
            cylinder = cylinder.translate([0, 0, z])

            pores.append(cylinder)

    return pores


def generate_articular_cartilage_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate articular cartilage from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching ArticularCartilageParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    zone_ratios = params.get('zone_ratios', [0.2, 0.4, 0.4])
    if isinstance(zone_ratios, list):
        zone_ratios = tuple(zone_ratios)

    pore_gradient = params.get('pore_gradient', [0.15, 0.25, 0.35])
    if isinstance(pore_gradient, list):
        pore_gradient = tuple(pore_gradient)

    return generate_articular_cartilage(ArticularCartilageParams(
        total_thickness=params.get('total_thickness', 2.0),
        zone_ratios=zone_ratios,
        pore_gradient=pore_gradient,
        diameter=params.get('diameter', 8.0),
        resolution=params.get('resolution', 16)
    ))
