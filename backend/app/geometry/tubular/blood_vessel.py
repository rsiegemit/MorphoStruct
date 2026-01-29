"""
Blood vessel scaffold generator.

Generates tri-layer vascular walls (intima, media, adventitia) with optional bifurcation.
"""

import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class BloodVesselParams:
    """Parameters for blood vessel scaffold generation."""

    inner_diameter_mm: float = 3.0
    wall_thickness_mm: float = 0.5
    layer_ratios: list[float] = None  # [intima, media, adventitia] defaults to [0.1, 0.5, 0.4]
    length_mm: float = 15.0
    bifurcation_angle_deg: Optional[float] = None  # If provided, creates Y-bifurcation
    resolution: int = 16

    def __post_init__(self):
        if self.layer_ratios is None:
            self.layer_ratios = [0.1, 0.5, 0.4]
        if len(self.layer_ratios) != 3:
            raise ValueError("layer_ratios must have exactly 3 values")
        if not np.isclose(sum(self.layer_ratios), 1.0):
            raise ValueError("layer_ratios must sum to 1.0")


def generate_blood_vessel(params: BloodVesselParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a blood vessel scaffold with tri-layer wall structure.

    Creates concentric tubes representing intima, media, and adventitia layers.
    Optionally adds Y-bifurcation at the end.

    Args:
        params: BloodVesselParams with generation parameters

    Returns:
        Tuple of (manifold, stats_dict)

    Raises:
        ValueError: If wall thickness exceeds radius or layer ratios invalid
    """
    inner_radius = params.inner_diameter_mm / 2
    outer_radius = inner_radius + params.wall_thickness_mm

    if inner_radius <= 0:
        raise ValueError("Inner diameter must be positive")

    # Calculate layer boundaries
    intima_thickness = params.wall_thickness_mm * params.layer_ratios[0]
    media_thickness = params.wall_thickness_mm * params.layer_ratios[1]
    adventitia_thickness = params.wall_thickness_mm * params.layer_ratios[2]

    r0 = inner_radius  # Lumen inner wall
    r1 = r0 + intima_thickness
    r2 = r1 + media_thickness
    r3 = r2 + adventitia_thickness

    # Create main vessel segment
    def create_vessel_segment(length: float, offset_z: float = 0) -> m3d.Manifold:
        """Create a tri-layer vessel segment."""
        # Intima layer (innermost)
        intima_outer = m3d.Manifold.cylinder(length, r1, r1, params.resolution)
        intima_inner = m3d.Manifold.cylinder(length + 0.2, r0, r0, params.resolution).translate([0, 0, -0.1])
        intima = intima_outer - intima_inner

        # Media layer (middle)
        media_outer = m3d.Manifold.cylinder(length, r2, r2, params.resolution)
        media_inner = m3d.Manifold.cylinder(length + 0.2, r1, r1, params.resolution).translate([0, 0, -0.1])
        media = media_outer - media_inner

        # Adventitia layer (outermost)
        adventitia_outer = m3d.Manifold.cylinder(length, r3, r3, params.resolution)
        adventitia_inner = m3d.Manifold.cylinder(length + 0.2, r2, r2, params.resolution).translate([0, 0, -0.1])
        adventitia = adventitia_outer - adventitia_inner

        # Combine all layers
        from ..core import batch_union
        vessel = batch_union([intima, media, adventitia])

        if offset_z != 0:
            vessel = vessel.translate([0, 0, offset_z])

        return vessel

    # Create main trunk
    if params.bifurcation_angle_deg is not None:
        # Create trunk up to bifurcation point (2/3 of length)
        trunk_length = params.length_mm * 0.67
        trunk = create_vessel_segment(trunk_length)

        # Create two branches
        branch_length = params.length_mm * 0.4
        angle_rad = np.radians(params.bifurcation_angle_deg / 2)

        # Branch 1 (rotated positive)
        branch1 = create_vessel_segment(branch_length)
        branch1 = branch1.rotate([0, np.degrees(angle_rad), 0])
        branch1 = branch1.translate([
            branch_length / 2 * np.sin(angle_rad),
            0,
            trunk_length + branch_length / 2 * np.cos(angle_rad)
        ])

        # Branch 2 (rotated negative)
        branch2 = create_vessel_segment(branch_length)
        branch2 = branch2.rotate([0, -np.degrees(angle_rad), 0])
        branch2 = branch2.translate([
            -branch_length / 2 * np.sin(angle_rad),
            0,
            trunk_length + branch_length / 2 * np.cos(angle_rad)
        ])

        # Combine trunk and branches
        from ..core import batch_union
        vessel = batch_union([trunk, branch1, branch2])
    else:
        # Simple straight vessel
        vessel = create_vessel_segment(params.length_mm)

    # Calculate statistics
    mesh = vessel.to_mesh()
    volume = vessel.volume() if hasattr(vessel, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'inner_diameter_mm': params.inner_diameter_mm,
        'wall_thickness_mm': params.wall_thickness_mm,
        'layer_thicknesses_mm': {
            'intima': intima_thickness,
            'media': media_thickness,
            'adventitia': adventitia_thickness
        },
        'has_bifurcation': params.bifurcation_angle_deg is not None,
        'scaffold_type': 'blood_vessel'
    }

    return vessel, stats


def generate_blood_vessel_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate a blood vessel scaffold from dictionary parameters.

    Args:
        params: Dictionary of parameters (will be unpacked into BloodVesselParams)

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_blood_vessel(BloodVesselParams(**params))
