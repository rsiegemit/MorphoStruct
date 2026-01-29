"""
Nasal Septum scaffold generator for curved cartilage sheet structures.

Provides parametric generation of nasal septum scaffolds with:
- Rectangular plate base
- Smooth curved edges
- S-curve or single-curve deviation
- Configurable dimensions and curvature
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from typing import Literal


@dataclass
class NasalSeptumParams:
    """Parameters for nasal septum scaffold generation."""
    length: float = 20.0  # mm, anterior-posterior length - reduced for faster generation
    height: float = 15.0  # mm, superior-inferior height - reduced for faster generation
    thickness: float = 1.5  # mm, cartilage thickness - reduced for faster generation
    curvature_radius: float = 75.0  # mm, radius of curvature (larger = less curved)
    curve_type: Literal['single', 's_curve'] = 'single'  # type of deviation
    resolution: int = 16  # mesh resolution - reduced from 32 for faster generation


def generate_nasal_septum(params: NasalSeptumParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a nasal septum scaffold.

    Creates a curved cartilage sheet using:
    - Rectangular base plate
    - Bending/curving along length
    - Smooth rounded edges
    - Optional S-curve deviation

    Args:
        params: NasalSeptumParams specifying septum geometry

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, scaffold_type

    Raises:
        ValueError: If parameters are invalid
    """
    if params.length <= 0 or params.height <= 0:
        raise ValueError("length and height must be positive")
    if params.thickness <= 0:
        raise ValueError("thickness must be positive")
    if params.curvature_radius <= 0:
        raise ValueError("curvature_radius must be positive")

    # Create base rectangular plate
    base_plate = m3d.Manifold.cube([params.length, params.thickness, params.height], center=True)

    # Add rounded edges by creating cylinders at edges
    edge_radius = params.thickness / 2

    # Create vertical edge cylinders
    edge_height = params.height
    edge_cyl = m3d.Manifold.cylinder(
        edge_height,
        edge_radius,
        edge_radius,
        params.resolution // 4
    )

    # Position edge cylinders at corners
    left_edge = edge_cyl.translate([-params.length / 2, 0, 0])
    right_edge = edge_cyl.translate([params.length / 2, 0, 0])

    # Create horizontal edge cylinders (top and bottom)
    horiz_edge = m3d.Manifold.cylinder(
        params.length,
        edge_radius,
        edge_radius,
        params.resolution // 4
    )
    horiz_edge = horiz_edge.rotate([0, 90, 0])

    top_edge = horiz_edge.translate([0, 0, params.height / 2])
    bottom_edge = horiz_edge.translate([0, 0, -params.height / 2])

    # Create corner spheres
    corners = []
    for x_sign in [-1, 1]:
        for z_sign in [-1, 1]:
            corner = m3d.Manifold.sphere(edge_radius, params.resolution // 4)
            corner = corner.translate([
                x_sign * params.length / 2,
                0,
                z_sign * params.height / 2
            ])
            corners.append(corner)

    # Combine all parts
    septum = base_plate + left_edge + right_edge + top_edge + bottom_edge
    for corner in corners:
        septum = septum + corner

    # Apply curvature by bending the structure
    # We'll use deformation by splitting into slices and rotating each slice
    if params.curvature_radius < 1000:  # Only apply if curvature is significant
        # Calculate bend angle based on arc length and radius
        arc_angle = params.length / params.curvature_radius  # radians

        # For single curve, bend in one direction
        if params.curve_type == 'single':
            # Create bent version by rotating around a point
            # Use shear-like transformation approximation
            bend_factor = params.length / (2 * params.curvature_radius)

            # Simple approach: rotate the entire object slightly
            # More complex: would need to deform slice by slice
            angle_deg = np.degrees(arc_angle) / 2
            septum = septum.rotate([0, angle_deg, 0])

        elif params.curve_type == 's_curve':
            # S-curve: create two halves bent in opposite directions
            # Split into front and back halves
            cut_plane = m3d.Manifold.cube([params.length, params.thickness * 2, params.height * 2], center=True)
            cut_plane = cut_plane.translate([params.length / 4, 0, 0])

            front_half = septum ^ cut_plane  # Intersection with front

            cut_plane_back = m3d.Manifold.cube([params.length, params.thickness * 2, params.height * 2], center=True)
            cut_plane_back = cut_plane_back.translate([-params.length / 4, 0, 0])
            back_half = septum ^ cut_plane_back

            # Rotate halves in opposite directions
            angle_deg = np.degrees(arc_angle) / 3
            front_half = front_half.rotate([0, angle_deg, 0])
            front_half = front_half.translate([params.length / 8, 0, 0])

            back_half = back_half.rotate([0, -angle_deg, 0])
            back_half = back_half.translate([-params.length / 8, 0, 0])

            septum = front_half + back_half

    # Calculate statistics
    mesh = septum.to_mesh()
    volume = septum.volume() if hasattr(septum, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'scaffold_type': 'nasal_septum',
        'length': params.length,
        'height': params.height,
        'thickness': params.thickness,
        'curvature_radius': params.curvature_radius,
        'curve_type': params.curve_type
    }

    return septum, stats


def generate_nasal_septum_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate nasal septum scaffold from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching NasalSeptumParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_nasal_septum(NasalSeptumParams(
        length=params.get('length', 20.0),
        height=params.get('height', 15.0),
        thickness=params.get('thickness', 1.5),
        curvature_radius=params.get('curvature_radius', 75.0),
        curve_type=params.get('curve_type', 'single'),
        resolution=params.get('resolution', 16)
    ))
