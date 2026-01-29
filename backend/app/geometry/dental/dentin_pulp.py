"""
Dentin-Pulp scaffold generator for tooth-like structures.

Provides parametric generation of tooth scaffolds with:
- Outer mineralized dentin shell (crown + root)
- Inner hollow pulp chamber
- Crown (dome-shaped) + root (tapered cylinder)
- Configurable dimensions and pulp chamber size
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class DentinPulpParams:
    """Parameters for dentin-pulp scaffold generation."""
    tooth_height: float = 6.0  # mm, total height (crown + root) - reduced for faster generation
    crown_diameter: float = 5.0  # mm, width of crown - reduced for faster generation
    root_length: float = 4.0  # mm, length of root portion - reduced for faster generation
    root_diameter: float = 2.5  # mm, diameter at root tip - reduced for faster generation
    pulp_chamber_size: float = 0.4  # ratio (0-1), relative size of pulp chamber
    dentin_thickness: float = 1.5  # mm, thickness of dentin shell - reduced for faster generation
    resolution: int = 16  # circular resolution - reduced from 32 for faster generation


def generate_dentin_pulp(params: DentinPulpParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a dentin-pulp tooth scaffold.

    Args:
        params: DentinPulpParams specifying tooth geometry

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, scaffold_type

    Raises:
        ValueError: If parameters are invalid
    """
    if params.pulp_chamber_size <= 0 or params.pulp_chamber_size >= 1:
        raise ValueError("pulp_chamber_size must be between 0 and 1")
    if params.dentin_thickness <= 0:
        raise ValueError("dentin_thickness must be positive")
    if params.crown_diameter <= params.root_diameter:
        raise ValueError("crown_diameter must be larger than root_diameter")

    crown_height = params.tooth_height - params.root_length
    if crown_height <= 0:
        raise ValueError("tooth_height must be greater than root_length")

    # Create crown as dome (sphere section)
    crown_radius = params.crown_diameter / 2
    sphere_radius = crown_radius  # Use crown radius as sphere radius

    # Create sphere and cut to get dome
    crown_sphere = m3d.Manifold.sphere(sphere_radius, params.resolution)

    # Cut plane to create dome (keep upper hemisphere)
    cut_box = m3d.Manifold.cube([params.crown_diameter * 2,
                                   params.crown_diameter * 2,
                                   sphere_radius], center=True)
    cut_box = cut_box.translate([0, 0, sphere_radius / 2])
    crown = crown_sphere ^ cut_box  # Intersection

    # Scale crown vertically to desired height
    crown = crown.scale([1, 1, crown_height / sphere_radius])

    # Position crown at top
    crown = crown.translate([0, 0, params.root_length])

    # Create root as tapered cylinder (cone frustum)
    root_top_radius = crown_radius
    root_bottom_radius = params.root_diameter / 2
    root = m3d.Manifold.cylinder(
        params.root_length,
        root_bottom_radius,
        root_top_radius,
        params.resolution
    )

    # Create outer tooth shell (crown + root)
    outer_tooth = crown + root

    # Create inner pulp chamber (scaled down version)
    pulp_scale = 1.0 - (params.dentin_thickness / min(crown_radius, root_top_radius))
    pulp_scale = max(0.1, pulp_scale)  # Ensure minimum size

    # Create pulp chamber by scaling outer shape
    pulp_crown = m3d.Manifold.sphere(sphere_radius * pulp_scale, params.resolution // 2)
    pulp_cut_box = m3d.Manifold.cube([params.crown_diameter * 2,
                                       params.crown_diameter * 2,
                                       sphere_radius * pulp_scale], center=True)
    pulp_cut_box = pulp_cut_box.translate([0, 0, sphere_radius * pulp_scale / 2])
    pulp_crown = pulp_crown ^ pulp_cut_box
    pulp_crown = pulp_crown.scale([1, 1, (crown_height * pulp_scale) / (sphere_radius * pulp_scale)])
    pulp_crown = pulp_crown.translate([0, 0, params.root_length])

    pulp_root = m3d.Manifold.cylinder(
        params.root_length * 0.9,  # Shorter than root
        root_bottom_radius * pulp_scale,
        root_top_radius * pulp_scale,
        params.resolution // 2
    )
    pulp_root = pulp_root.translate([0, 0, params.root_length * 0.05])  # Offset from bottom

    pulp_chamber = pulp_crown + pulp_root

    # Subtract pulp chamber from outer tooth to create hollow shell
    result = outer_tooth - pulp_chamber

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'scaffold_type': 'dentin_pulp',
        'tooth_height': params.tooth_height,
        'crown_diameter': params.crown_diameter,
        'root_length': params.root_length,
        'pulp_chamber_size': params.pulp_chamber_size,
        'dentin_thickness': params.dentin_thickness
    }

    return result, stats


def generate_dentin_pulp_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate dentin-pulp scaffold from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching DentinPulpParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_dentin_pulp(DentinPulpParams(
        tooth_height=params.get('tooth_height', 6.0),
        crown_diameter=params.get('crown_diameter', 5.0),
        root_length=params.get('root_length', 4.0),
        root_diameter=params.get('root_diameter', 2.5),
        pulp_chamber_size=params.get('pulp_chamber_size', 0.4),
        dentin_thickness=params.get('dentin_thickness', 1.5),
        resolution=params.get('resolution', 16)
    ))
