"""
Trachea scaffold generator.

Generates tracheal structures with C-shaped cartilage rings and posterior membrane.
"""

import manifold3d as m3d
import numpy as np
from dataclasses import dataclass


@dataclass
class TracheaParams:
    """Parameters for trachea scaffold generation."""

    outer_diameter_mm: float = 15.0  # Adult human trachea ~15-25mm
    ring_thickness_mm: float = 2.0  # Cartilage ring thickness ~2-4mm
    ring_spacing_mm: float = 3.0  # Spacing between rings ~3-5mm
    ring_count: int = 6  # Number of C-shaped rings
    length_mm: float = None  # Auto-calculated if None
    posterior_gap_angle_deg: float = 90.0  # Gap for posterior membrane (typically ~90°)
    resolution: int = 20

    def __post_init__(self):
        # Auto-calculate length if not provided
        if self.length_mm is None:
            self.length_mm = self.ring_count * (self.ring_thickness_mm + self.ring_spacing_mm)

        if self.ring_count < 1:
            raise ValueError("ring_count must be at least 1")
        if self.posterior_gap_angle_deg < 45 or self.posterior_gap_angle_deg > 135:
            raise ValueError("posterior_gap_angle_deg must be between 45 and 135")


def generate_trachea(params: TracheaParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a trachea scaffold with C-shaped cartilage rings.

    Creates a series of C-shaped rings (270° arcs) with gaps for the posterior
    membrane. Rings are evenly spaced along the length.

    Args:
        params: TracheaParams with generation parameters

    Returns:
        Tuple of (manifold, stats_dict)

    Raises:
        ValueError: If parameters are invalid
    """
    outer_radius = params.outer_diameter_mm / 2
    inner_radius = outer_radius - params.ring_thickness_mm

    if inner_radius <= 0:
        raise ValueError("Ring thickness exceeds radius")

    # Calculate ring arc angle (360 - gap)
    ring_arc_deg = 360.0 - params.posterior_gap_angle_deg
    ring_arc_rad = np.radians(ring_arc_deg)

    def create_c_ring(z_position: float) -> m3d.Manifold:
        """Create a single C-shaped ring at given z position."""
        # Create full ring
        outer_ring = m3d.Manifold.cylinder(
            params.ring_thickness_mm,
            outer_radius,
            outer_radius,
            params.resolution
        )

        inner_ring = m3d.Manifold.cylinder(
            params.ring_thickness_mm + 0.2,
            inner_radius,
            inner_radius,
            params.resolution
        ).translate([0, 0, -0.1])

        ring = outer_ring - inner_ring

        # Create gap cutter for posterior opening
        # Gap is centered at the back (negative Y direction)
        gap_angle_rad = np.radians(params.posterior_gap_angle_deg)
        gap_half = gap_angle_rad / 2

        # Create a wedge to cut out the gap
        # Use a large box rotated to cut out the posterior section
        gap_width = outer_radius * 2.5
        gap_depth = outer_radius * 1.5

        cutter = m3d.Manifold.cube(
            [gap_width, gap_depth, params.ring_thickness_mm + 0.4],
            center=True
        )
        # Position cutter at back of ring
        cutter = cutter.translate([0, -outer_radius, 0])

        # Rotate cutter to create proper gap angle
        # For 90° gap, we want 45° on each side from back center
        # No rotation needed if gap is directly at back

        # Subtract gap from ring
        c_ring = ring - cutter

        # Translate to z position
        c_ring = c_ring.translate([0, 0, z_position])

        return c_ring

    # Create all rings
    rings = []
    spacing = params.ring_thickness_mm + params.ring_spacing_mm

    for i in range(params.ring_count):
        z_pos = i * spacing + params.ring_thickness_mm / 2
        ring = create_c_ring(z_pos)
        rings.append(ring)

    # Combine all rings
    from ..core import batch_union
    trachea = batch_union(rings)

    # Calculate statistics
    mesh = trachea.to_mesh()
    volume = trachea.volume() if hasattr(trachea, 'volume') else 0

    actual_length = params.ring_count * spacing

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'outer_diameter_mm': params.outer_diameter_mm,
        'ring_thickness_mm': params.ring_thickness_mm,
        'ring_spacing_mm': params.ring_spacing_mm,
        'ring_count': params.ring_count,
        'posterior_gap_angle_deg': params.posterior_gap_angle_deg,
        'ring_arc_angle_deg': ring_arc_deg,
        'total_length_mm': actual_length,
        'scaffold_type': 'trachea'
    }

    return trachea, stats


def generate_trachea_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate a trachea scaffold from dictionary parameters.

    Args:
        params: Dictionary of parameters (will be unpacked into TracheaParams)

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_trachea(TracheaParams(**params))
