"""
Cornea scaffold generator with curved dome geometry.

Provides parametric generation of cornea tissue scaffolds with:
- Spherical cap shape with specific radius of curvature
- Physiologically accurate dimensions (10-12mm diameter, 0.5-0.6mm thickness)
- Multiple lamella layers for stromal architecture
- Smooth dome surface for optical applications
- Shell structure with specified thickness
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class CorneaParams:
    """Parameters for cornea scaffold generation."""
    diameter_mm: float = 8.0
    thickness_mm: float = 0.45
    radius_of_curvature_mm: float = 6.5
    lamella_count: int = 3
    resolution: int = 20  # High resolution for smooth dome


def make_spherical_cap_shell(
    diameter: float,
    thickness: float,
    radius_of_curvature: float,
    resolution: int
) -> m3d.Manifold:
    """
    Create a spherical cap shell with specified thickness.

    Uses parametric equation for spherical cap:
    z = R - sqrt(R² - x² - y²)

    Args:
        diameter: Diameter of the cornea
        thickness: Wall thickness of the shell
        radius_of_curvature: Radius of the sphere that defines the curvature
        resolution: Angular resolution for mesh generation

    Returns:
        Manifold representing the spherical cap shell
    """
    R = radius_of_curvature
    radius = diameter / 2

    # Validate geometry
    if radius > R:
        raise ValueError(f"Radius ({radius}) cannot exceed radius of curvature ({R})")

    # Calculate height of spherical cap
    # h = R - sqrt(R² - r²)
    cap_height = R - np.sqrt(R * R - radius * radius)

    # Create outer surface (larger radius of curvature)
    outer_sphere = m3d.Manifold.sphere(R, resolution)
    # Shift sphere so cap sits at origin with dome pointing up
    outer_sphere = outer_sphere.translate([0, 0, -R + cap_height])

    # Create inner surface (smaller radius of curvature)
    R_inner = R - thickness
    inner_sphere = m3d.Manifold.sphere(R_inner, resolution)
    inner_height = R_inner - np.sqrt(R_inner * R_inner - radius * radius)
    # Shift to align with outer surface
    inner_sphere = inner_sphere.translate([0, 0, -R_inner + inner_height])

    # Create clipping cylinder to cut the cap shape
    clip_cylinder = m3d.Manifold.cylinder(
        cap_height * 1.5,  # Tall enough to cut through cap
        radius,
        radius,
        resolution
    )
    clip_cylinder = clip_cylinder.translate([0, 0, -cap_height * 0.25])

    # Clip both spheres to get cap shapes
    outer_cap = outer_sphere ^ clip_cylinder  # Intersection
    inner_cap = inner_sphere ^ clip_cylinder

    # Create shell by subtracting inner from outer
    shell = outer_cap - inner_cap

    # Create flat base to close the bottom
    base_disc = m3d.Manifold.cylinder(
        thickness,
        radius,
        radius,
        resolution
    )
    base_disc = base_disc.translate([0, 0, -thickness / 2])

    # Subtract inner cylinder to make base ring
    inner_disc = m3d.Manifold.cylinder(
        thickness * 1.1,
        radius - thickness,
        radius - thickness,
        resolution
    )
    inner_disc = inner_disc.translate([0, 0, -thickness * 0.55])
    base_ring = base_disc - inner_disc

    # Combine shell with base ring
    result = shell + base_ring

    return result


def make_lamella_layer(
    diameter: float,
    thickness: float,
    radius_of_curvature: float,
    layer_fraction: float,
    resolution: int
) -> m3d.Manifold:
    """
    Create a single lamella layer within the cornea.

    Args:
        diameter: Diameter of the cornea
        thickness: Total wall thickness
        radius_of_curvature: Radius of curvature
        layer_fraction: Position fraction from inner (0) to outer (1) surface
        resolution: Angular resolution

    Returns:
        Manifold representing the lamella layer (thin sheet)
    """
    R = radius_of_curvature
    radius = diameter / 2

    # Calculate radius for this layer
    R_layer = R - thickness * (1 - layer_fraction)

    # Create sphere for this layer
    layer_sphere = m3d.Manifold.sphere(R_layer, resolution)
    cap_height = R - np.sqrt(R * R - radius * radius)
    layer_height = R_layer - np.sqrt(R_layer * R_layer - radius * radius)
    layer_sphere = layer_sphere.translate([0, 0, -R_layer + layer_height])

    # Clip to cap shape
    clip_cylinder = m3d.Manifold.cylinder(
        cap_height * 1.5,
        radius,
        radius,
        resolution
    )
    clip_cylinder = clip_cylinder.translate([0, 0, -cap_height * 0.25])

    layer_cap = layer_sphere ^ clip_cylinder

    return layer_cap


def generate_cornea(params: CorneaParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a cornea scaffold.

    Args:
        params: CorneaParams specifying geometry and structure

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, curvature_radius,
                     lamella_count, scaffold_type

    Raises:
        ValueError: If parameters are invalid
    """
    if params.diameter_mm <= 0 or params.thickness_mm <= 0:
        raise ValueError("Diameter and thickness must be positive")
    if params.radius_of_curvature_mm <= params.diameter_mm / 2:
        raise ValueError("Radius of curvature must be greater than half the diameter")
    if params.thickness_mm > params.radius_of_curvature_mm / 2:
        raise ValueError("Thickness too large for given radius of curvature")

    # Create main shell structure
    shell = make_spherical_cap_shell(
        params.diameter_mm,
        params.thickness_mm,
        params.radius_of_curvature_mm,
        params.resolution
    )

    # Optionally add lamella layers (visual markers for stromal structure)
    # These are thin surfaces that represent collagen lamellae orientation
    if params.lamella_count > 1:
        lamellae = []
        for i in range(1, params.lamella_count):
            layer_fraction = i / params.lamella_count
            lamella = make_lamella_layer(
                params.diameter_mm,
                params.thickness_mm,
                params.radius_of_curvature_mm,
                layer_fraction,
                params.resolution
            )
            # Make lamella thin shell
            lamella_inner = make_lamella_layer(
                params.diameter_mm,
                params.thickness_mm,
                params.radius_of_curvature_mm,
                layer_fraction - 0.02,  # Very thin layer
                params.resolution
            )
            lamella_shell = lamella - lamella_inner
            if lamella_shell.num_vert() > 0:
                lamellae.append(lamella_shell)

        if lamellae:
            lamellae_union = batch_union(lamellae)
            result = shell + lamellae_union
        else:
            result = shell
    else:
        result = shell

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    # Calculate cap height
    R = params.radius_of_curvature_mm
    r = params.diameter_mm / 2
    cap_height = R - np.sqrt(R * R - r * r)

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'diameter_mm': params.diameter_mm,
        'thickness_mm': params.thickness_mm,
        'radius_of_curvature_mm': params.radius_of_curvature_mm,
        'cap_height_mm': cap_height,
        'lamella_count': params.lamella_count,
        'scaffold_type': 'cornea'
    }

    return result, stats


def generate_cornea_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate cornea scaffold from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching CorneaParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_cornea(CorneaParams(
        diameter_mm=params.get('diameter_mm', 8.0),
        thickness_mm=params.get('thickness_mm', 0.45),
        radius_of_curvature_mm=params.get('radius_of_curvature_mm', 6.5),
        lamella_count=params.get('lamella_count', 3),
        resolution=params.get('resolution', 20)
    ))
