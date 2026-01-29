"""
Ear Auricle scaffold generator for complex curved cartilage frameworks.

Provides parametric generation of simplified ear-shaped scaffolds with:
- Main body as ellipsoid base
- Helix rim as curved outer edge
- Shell structure with configurable thickness
- Parametric control over ear features
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class EarAuricleParams:
    """Parameters for ear auricle scaffold generation."""
    scale_factor: float = 0.6  # overall size multiplier (0.5-1.5) - reduced for faster generation
    thickness: float = 2.0  # mm, cartilage thickness
    helix_definition: float = 0.7  # 0-1, prominence of helix rim
    antihelix_depth: float = 0.3  # 0-1, depth of antihelix ridge
    resolution: int = 16  # circular resolution - reduced from 32 for faster generation


def generate_ear_auricle(params: EarAuricleParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate an ear auricle scaffold.

    Creates a simplified ear shape using:
    - Ellipsoid main body
    - Torus section for helix rim
    - Conchal bowl subtraction
    - Shell structure at specified thickness

    Args:
        params: EarAuricleParams specifying ear geometry

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, scaffold_type

    Raises:
        ValueError: If parameters are invalid
    """
    if params.scale_factor <= 0:
        raise ValueError("scale_factor must be positive")
    if params.thickness <= 0:
        raise ValueError("thickness must be positive")
    if not (0 <= params.helix_definition <= 1):
        raise ValueError("helix_definition must be between 0 and 1")
    if not (0 <= params.antihelix_depth <= 1):
        raise ValueError("antihelix_depth must be between 0 and 1")

    # Standard ear dimensions (will be scaled)
    ear_height = 60.0 * params.scale_factor  # mm
    ear_width = 30.0 * params.scale_factor  # mm
    ear_depth = 15.0 * params.scale_factor  # mm

    # Create main body as ellipsoid
    main_body = m3d.Manifold.sphere(1.0, params.resolution)
    main_body = main_body.scale([ear_width / 2, ear_depth / 2, ear_height / 2])

    # Create helix rim (outer curved edge) using torus section
    helix_major_radius = ear_width / 2.5
    helix_minor_radius = params.thickness * (1 + params.helix_definition)

    # Create torus for helix
    helix_torus = m3d.Manifold.revolve(
        m3d.CrossSection.circle(helix_minor_radius, params.resolution // 2),
        params.resolution
    )
    helix_torus = helix_torus.scale([1, 1, ear_height / (2 * helix_major_radius)])
    helix_torus = helix_torus.translate([helix_major_radius, 0, 0])

    # Cut helix to keep only outer section
    helix_cut_box = m3d.Manifold.cube([ear_width, ear_depth * 2, ear_height * 2], center=True)
    helix_cut_box = helix_cut_box.translate([ear_width / 4, 0, 0])
    helix = helix_torus ^ helix_cut_box

    # Create conchal bowl (ear canal depression)
    concha_radius = ear_width / 4
    concha_depth = ear_depth * 0.6
    concha = m3d.Manifold.sphere(concha_radius, params.resolution // 2)
    concha = concha.scale([1, concha_depth / concha_radius, 1])
    concha = concha.translate([-ear_width / 6, 0, 0])

    # Combine main body and helix
    ear_solid = main_body + helix

    # Subtract conchal bowl
    ear_solid = ear_solid - concha

    # Create antihelix ridge if depth > 0
    if params.antihelix_depth > 0:
        antihelix_height = ear_height * 0.6
        antihelix_radius = params.thickness * (0.5 + params.antihelix_depth)

        # Create antihelix as elongated cylinder
        antihelix = m3d.Manifold.cylinder(
            antihelix_height,
            antihelix_radius,
            antihelix_radius,
            params.resolution // 4
        )
        antihelix = antihelix.rotate([90, 0, 30])  # Tilt and rotate
        antihelix = antihelix.translate([-ear_width / 8, -ear_depth / 4, 0])

        # Add antihelix to solid
        ear_solid = ear_solid + antihelix

    # Create inner offset version for shell
    # Scale down from center to create thickness
    thickness_scale = 1.0 - (params.thickness / min(ear_width, ear_height) * 2)
    thickness_scale = max(0.3, thickness_scale)  # Ensure minimum thickness

    inner_solid = m3d.Manifold.sphere(1.0, params.resolution // 2)
    inner_solid = inner_solid.scale([
        ear_width / 2 * thickness_scale,
        ear_depth / 2 * thickness_scale,
        ear_height / 2 * thickness_scale
    ])

    # Subtract inner from outer to create shell
    result = ear_solid - inner_solid

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'scaffold_type': 'ear_auricle',
        'scale_factor': params.scale_factor,
        'thickness': params.thickness,
        'helix_definition': params.helix_definition,
        'antihelix_depth': params.antihelix_depth,
        'ear_dimensions': {
            'height': ear_height,
            'width': ear_width,
            'depth': ear_depth
        }
    }

    return result, stats


def generate_ear_auricle_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate ear auricle scaffold from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching EarAuricleParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_ear_auricle(EarAuricleParams(
        scale_factor=params.get('scale_factor', 0.6),
        thickness=params.get('thickness', 2.0),
        helix_definition=params.get('helix_definition', 0.7),
        antihelix_depth=params.get('antihelix_depth', 0.3),
        resolution=params.get('resolution', 16)
    ))
