"""
Pancreatic islet scaffold generator.

Creates spherical cluster structures with core-shell architecture:
- Porous spheres mimicking islet of Langerhans
- Multiple islets in cluster arrangement
- Controlled pore size and density
- Shell thickness for nutrient/gas exchange
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class PancreaticIsletParams:
    """Parameters for pancreatic islet scaffold generation."""
    islet_diameter: float = 150.0  # µm (reduced from 200)
    shell_thickness: float = 40.0  # µm (reduced from 50)
    pore_size: float = 20.0  # µm
    cluster_count: int = 3  # number of islets in cluster (reduced from 7)
    spacing: float = 250.0  # µm (reduced from 300)
    resolution: int = 10  # reduced from 16


def create_porous_sphere(center: np.ndarray, outer_radius: float, inner_radius: float,
                         pore_radius: float, pore_count: int, resolution: int) -> m3d.Manifold:
    """
    Create a porous spherical shell with evenly distributed pores.

    Args:
        center: Center position (x, y, z)
        outer_radius: Outer radius of sphere
        inner_radius: Inner radius (creates shell)
        pore_radius: Radius of pores
        pore_count: Number of pores
        resolution: Sphere resolution

    Returns:
        Porous sphere manifold
    """
    # Create outer and inner spheres for shell
    outer = m3d.Manifold.sphere(outer_radius, resolution)
    inner = m3d.Manifold.sphere(inner_radius, resolution)

    shell = outer - inner

    # Create pores using Fibonacci sphere distribution
    pores = []
    golden_ratio = (1 + np.sqrt(5)) / 2
    angle_increment = 2 * np.pi * golden_ratio

    for i in range(pore_count):
        # Fibonacci sphere points
        t = i / pore_count
        inclination = np.arccos(1 - 2 * t)
        azimuth = angle_increment * i

        # Position on sphere surface
        x = outer_radius * np.sin(inclination) * np.cos(azimuth)
        y = outer_radius * np.sin(inclination) * np.sin(azimuth)
        z = outer_radius * np.cos(inclination)

        # Create pore as small sphere cutting through shell
        pore = m3d.Manifold.sphere(pore_radius, 8)
        pore = pore.translate([x, y, z])
        pores.append(pore)

    # Subtract pores from shell
    if pores:
        pore_union = batch_union(pores)
        shell = shell - pore_union

    # Translate to center position
    return shell.translate([center[0], center[1], center[2]])


def create_solid_sphere(center: np.ndarray, radius: float, resolution: int) -> m3d.Manifold:
    """
    Create a solid sphere (for simpler islet model).

    Args:
        center: Center position (x, y, z)
        radius: Sphere radius
        resolution: Sphere resolution

    Returns:
        Sphere manifold
    """
    sphere = m3d.Manifold.sphere(radius, resolution)
    return sphere.translate([center[0], center[1], center[2]])


def generate_cluster_positions(count: int, spacing: float) -> list[np.ndarray]:
    """
    Generate positions for islets in a cluster arrangement.

    Uses hexagonal close packing pattern in 3D.

    Args:
        count: Number of islets
        spacing: Distance between centers

    Returns:
        List of position vectors
    """
    if count <= 0:
        return []
    if count == 1:
        return [np.array([0.0, 0.0, 0.0])]

    positions = [np.array([0.0, 0.0, 0.0])]

    # Layer 1: 6 around center in XY plane
    if count > 1:
        for i in range(min(6, count - 1)):
            angle = i * np.pi / 3
            x = spacing * np.cos(angle)
            y = spacing * np.sin(angle)
            positions.append(np.array([x, y, 0.0]))

    # Layer 2: Above and below
    if count > 7:
        remaining = count - 7
        layer_z = spacing * 0.866  # sqrt(3)/2

        # Above layer
        for i in range(min(3, remaining)):
            angle = i * 2 * np.pi / 3
            x = spacing * 0.5 * np.cos(angle)
            y = spacing * 0.5 * np.sin(angle)
            positions.append(np.array([x, y, layer_z]))

        # Below layer
        if remaining > 3:
            for i in range(min(3, remaining - 3)):
                angle = i * 2 * np.pi / 3 + np.pi / 3
                x = spacing * 0.5 * np.cos(angle)
                y = spacing * 0.5 * np.sin(angle)
                positions.append(np.array([x, y, -layer_z]))

    return positions[:count]


def generate_pancreatic_islet(params: PancreaticIsletParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a pancreatic islet scaffold with porous sphere clusters.

    Args:
        params: PancreaticIsletParams specifying geometry

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, islet_count, scaffold_type

    Raises:
        ValueError: If no islets are generated
    """
    # Convert µm to mm
    outer_radius = params.islet_diameter / 2000.0
    shell_thickness_mm = params.shell_thickness / 1000.0
    inner_radius = outer_radius - shell_thickness_mm
    pore_radius = params.pore_size / 2000.0
    spacing_mm = params.spacing / 1000.0

    if inner_radius <= 0:
        inner_radius = outer_radius * 0.5

    # Generate cluster positions
    positions = generate_cluster_positions(params.cluster_count, spacing_mm)

    # Create islets
    islets = []
    for pos in positions:
        # Calculate pore count based on surface area (reduced for faster generation)
        surface_area = 4 * np.pi * outer_radius**2
        pore_area = np.pi * pore_radius**2
        pore_count = max(3, int(surface_area / pore_area * 0.05))  # 5% porosity (reduced from 10%)

        # Create porous sphere
        islet = create_porous_sphere(
            pos, outer_radius, inner_radius,
            pore_radius, pore_count,
            params.resolution
        )
        if islet.num_vert() > 0:
            islets.append(islet)

    if not islets:
        raise ValueError("No islets generated")

    result = batch_union(islets)

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'islet_count': len(islets),
        'scaffold_type': 'pancreatic_islet'
    }

    return result, stats


def generate_pancreatic_islet_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate pancreatic islet from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching PancreaticIsletParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_pancreatic_islet(PancreaticIsletParams(
        islet_diameter=params.get('islet_diameter', 150.0),
        shell_thickness=params.get('shell_thickness', 40.0),
        pore_size=params.get('pore_size', 20.0),
        cluster_count=params.get('cluster_count', 3),
        spacing=params.get('spacing', 250.0),
        resolution=params.get('resolution', 10)
    ))
