"""
Liver sinusoid scaffold generator.

Creates core-shell tubular structures mimicking hepatic sinusoidal channels:
- Hollow tube with fenestrations (pores) in wall
- Small pore size (50-150nm scaled to printable size)
- Controlled fenestration density
- Perfusable lumen for blood flow simulation
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class LiverSinusoidParams:
    """Parameters for liver sinusoid scaffold generation."""
    sinusoid_diameter: float = 20.0  # µm (10-30µm)
    length: float = 2.0  # mm (reduced from 3.0 for faster generation)
    fenestration_size: float = 1.0  # µm (scaled from 50-150nm for printability)
    fenestration_density: float = 0.05  # 0.0-1.0 (reduced from 0.1 for faster generation)
    resolution: int = 8  # reduced from 10 for faster generation


def create_hollow_tube(length: float, outer_radius: float, inner_radius: float, resolution: int) -> m3d.Manifold:
    """
    Create a hollow tube along Z axis.

    Args:
        length: Tube length
        outer_radius: Outer radius
        inner_radius: Inner radius (lumen)
        resolution: Number of segments around cylinder

    Returns:
        Hollow tube manifold
    """
    outer = m3d.Manifold.cylinder(length, outer_radius, outer_radius, resolution)
    inner = m3d.Manifold.cylinder(length + 0.02, inner_radius, inner_radius, resolution)
    inner = inner.translate([0, 0, -0.01])
    return outer - inner


def create_fenestrations(length: float, radius: float, fenestration_radius: float,
                        density: float, resolution: int) -> list[m3d.Manifold]:
    """
    Create fenestration pores distributed on tube surface.

    Args:
        length: Tube length
        radius: Tube radius (where pores are placed)
        fenestration_radius: Radius of each pore
        density: Pore density (0.0-1.0)
        resolution: Pore resolution

    Returns:
        List of fenestration sphere manifolds
    """
    if density <= 0:
        return []

    # Calculate number of pores based on surface area and density
    surface_area = 2 * np.pi * radius * length
    pore_area = np.pi * fenestration_radius**2
    num_pores = max(5, int(surface_area / pore_area * density))

    fenestrations = []

    # Distribute pores evenly in cylindrical coordinates
    num_circumferential = max(4, int(np.sqrt(num_pores * 2)))
    num_axial = max(2, num_pores // num_circumferential)

    for i in range(num_axial):
        z = (i + 0.5) * length / num_axial

        # Alternate offset for each row (brick pattern)
        angle_offset = (i % 2) * np.pi / num_circumferential

        for j in range(num_circumferential):
            angle = 2 * np.pi * j / num_circumferential + angle_offset

            # Position on tube surface
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)

            # Create small sphere for fenestration
            pore = m3d.Manifold.sphere(fenestration_radius, 8)
            pore = pore.translate([x, y, z])
            fenestrations.append(pore)

    return fenestrations


def generate_liver_sinusoid(params: LiverSinusoidParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a liver sinusoid scaffold with fenestrations.

    Args:
        params: LiverSinusoidParams specifying geometry

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, fenestration_count, scaffold_type

    Raises:
        ValueError: If no geometry is generated
    """
    # Convert µm to mm
    outer_radius = params.sinusoid_diameter / 2000.0
    fenestration_radius = params.fenestration_size / 2000.0

    # Wall thickness is ~20% of diameter
    wall_thickness = outer_radius * 0.4
    inner_radius = outer_radius - wall_thickness

    if inner_radius <= 0:
        inner_radius = outer_radius * 0.5

    # Create hollow tube
    tube = create_hollow_tube(params.length, outer_radius, inner_radius, params.resolution)

    # Create fenestrations
    fenestrations = create_fenestrations(
        params.length, outer_radius,
        fenestration_radius, params.fenestration_density,
        params.resolution
    )

    # Subtract fenestrations from tube
    if fenestrations:
        fenestration_union = batch_union(fenestrations)
        result = tube - fenestration_union
    else:
        result = tube

    if result.num_vert() == 0:
        raise ValueError("No geometry generated")

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'fenestration_count': len(fenestrations),
        'scaffold_type': 'liver_sinusoid'
    }

    return result, stats


def generate_liver_sinusoid_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate liver sinusoid from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching LiverSinusoidParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_liver_sinusoid(LiverSinusoidParams(
        sinusoid_diameter=params.get('sinusoid_diameter', 20.0),
        length=params.get('length', 2.0),
        fenestration_size=params.get('fenestration_size', 1.0),
        fenestration_density=params.get('fenestration_density', 0.05),
        resolution=params.get('resolution', 8)
    ))
