"""
Spinal cord scaffold generator.

Generates spinal cord structures with butterfly-shaped gray matter core
and surrounding white matter channels.
"""

import manifold3d as m3d
import numpy as np
from dataclasses import dataclass


@dataclass
class SpinalCordParams:
    """Parameters for spinal cord scaffold generation."""

    cord_diameter_mm: float = 8.0  # Human spinal cord ~10-15mm
    channel_diameter_um: float = 250.0  # White matter axon channels
    channel_count: int = 12  # Channels surrounding gray matter
    gray_matter_ratio: float = 0.4  # Gray matter takes ~40% of cross-section
    length_mm: float = 25.0
    resolution: int = 20

    def __post_init__(self):
        if self.gray_matter_ratio < 0.2 or self.gray_matter_ratio > 0.6:
            raise ValueError("gray_matter_ratio must be between 0.2 and 0.6")
        if self.channel_count < 8:
            raise ValueError("channel_count must be at least 8")


def generate_spinal_cord(params: SpinalCordParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a spinal cord scaffold with gray matter core and white matter channels.

    Creates a butterfly/H-shaped gray matter core in the center, surrounded by
    white matter region with parallel guidance channels for axon tracts.

    Args:
        params: SpinalCordParams with generation parameters

    Returns:
        Tuple of (manifold, stats_dict)

    Raises:
        ValueError: If parameters are invalid
    """
    cord_radius = params.cord_diameter_mm / 2
    channel_radius_mm = params.channel_diameter_um / 2000.0

    # Gray matter butterfly shape (simplified as H-shaped extrusion)
    gray_width = cord_radius * np.sqrt(params.gray_matter_ratio)
    gray_height = gray_width * 1.2  # Slightly taller than wide

    # Create gray matter as H-shape (two vertical bars + horizontal bar)
    def create_gray_matter() -> m3d.Manifold:
        """Create butterfly-shaped gray matter core."""
        bar_width = gray_width * 0.3
        bar_height = gray_height

        # Left vertical bar (dorsal horn)
        left = m3d.Manifold.cube([bar_width, bar_width, params.length_mm], center=True)
        left = left.translate([-gray_width * 0.35, 0, 0])

        # Right vertical bar (ventral horn)
        right = m3d.Manifold.cube([bar_width, bar_width, params.length_mm], center=True)
        right = right.translate([gray_width * 0.35, 0, 0])

        # Horizontal connecting bar (gray commissure)
        center = m3d.Manifold.cube([gray_width * 0.8, bar_width * 0.6, params.length_mm], center=True)

        # Union all parts
        from ..core import batch_union
        return batch_union([left, right, center])

    gray_matter = create_gray_matter()

    # Create outer cord boundary (white matter region)
    outer_cord = m3d.Manifold.cylinder(
        params.length_mm,
        cord_radius,
        cord_radius,
        params.resolution
    )

    # Create white matter region (outer cord minus gray matter)
    white_matter_base = outer_cord - gray_matter

    # Add white matter guidance channels
    channels = []
    channel_ring_radius = (cord_radius + gray_width / 2) / 2  # Between gray and outer edge

    for i in range(params.channel_count):
        angle = 2 * np.pi * i / params.channel_count
        x = channel_ring_radius * np.cos(angle)
        y = channel_ring_radius * np.sin(angle)

        # Create vertical channel
        channel = m3d.Manifold.cylinder(
            params.length_mm + 0.4,
            channel_radius_mm,
            channel_radius_mm,
            8
        ).translate([x, y, -0.2])
        channels.append(channel)

    # Subtract channels from white matter
    from ..core import batch_union
    all_channels = batch_union(channels)
    white_matter = white_matter_base - all_channels

    # Combine gray and white matter
    spinal_cord = batch_union([gray_matter, white_matter])

    # Calculate statistics
    mesh = spinal_cord.to_mesh()
    volume = spinal_cord.volume() if hasattr(spinal_cord, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'cord_diameter_mm': params.cord_diameter_mm,
        'gray_matter_ratio': params.gray_matter_ratio,
        'channel_count': params.channel_count,
        'channel_diameter_um': params.channel_diameter_um,
        'scaffold_type': 'spinal_cord'
    }

    return spinal_cord, stats


def generate_spinal_cord_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate a spinal cord scaffold from dictionary parameters.

    Args:
        params: Dictionary of parameters (will be unpacked into SpinalCordParams)

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_spinal_cord(SpinalCordParams(**params))
