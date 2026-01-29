"""
Nerve conduit scaffold generator.

Generates multi-channel nerve guidance conduits with internal microchannels for axon regeneration.
"""

import manifold3d as m3d
import numpy as np
from dataclasses import dataclass


@dataclass
class NerveConduitParams:
    """Parameters for nerve conduit scaffold generation."""

    outer_diameter_mm: float = 3.0
    channel_count: int = 4  # 1 central + 3 surrounding for faster generation
    channel_diameter_um: float = 150.0  # Micrometers (200-300um typical for axons)
    wall_thickness_mm: float = 0.4
    length_mm: float = 12.0
    resolution: int = 12

    def __post_init__(self):
        if self.channel_count < 1:
            raise ValueError("channel_count must be at least 1")
        if self.channel_diameter_um < 50 or self.channel_diameter_um > 500:
            raise ValueError("channel_diameter_um must be between 50 and 500")


def generate_nerve_conduit(params: NerveConduitParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a nerve conduit scaffold with internal guidance microchannels.

    Creates a hollow outer tube with multiple internal parallel channels to guide
    axon regeneration. Uses 1 central + N surrounding channels in hexagonal pattern.

    Args:
        params: NerveConduitParams with generation parameters

    Returns:
        Tuple of (manifold, stats_dict)

    Raises:
        ValueError: If channels don't fit within outer diameter
    """
    outer_radius = params.outer_diameter_mm / 2
    inner_radius = outer_radius - params.wall_thickness_mm
    channel_radius_mm = params.channel_diameter_um / 2000.0  # Convert um to mm

    if inner_radius <= 0:
        raise ValueError("Wall thickness exceeds radius")

    # Check if channels fit
    if params.channel_count == 1:
        max_channel_radius = inner_radius * 0.8
    else:
        # For multi-channel: 1 center + ring of channels
        # Ring radius is half the available inner space
        ring_radius = inner_radius * 0.5
        max_channel_radius = ring_radius * 0.4  # Leave space between channels

    if channel_radius_mm > max_channel_radius:
        raise ValueError(
            f"Channels too large: {params.channel_diameter_um}µm "
            f"exceeds max {max_channel_radius * 2000:.0f}µm for {params.channel_count} channels"
        )

    # Create outer wall
    outer = m3d.Manifold.cylinder(
        params.length_mm,
        outer_radius,
        outer_radius,
        params.resolution * 2
    )

    inner = m3d.Manifold.cylinder(
        params.length_mm + 0.2,
        inner_radius,
        inner_radius,
        params.resolution * 2
    ).translate([0, 0, -0.1])

    conduit = outer - inner

    # Create guidance channels
    channels = []

    if params.channel_count == 1:
        # Single central channel
        channel = m3d.Manifold.cylinder(
            params.length_mm + 0.4,
            channel_radius_mm,
            channel_radius_mm,
            params.resolution
        ).translate([0, 0, -0.2])
        channels.append(channel)
    else:
        # Central channel + hexagonal ring
        ring_radius = inner_radius * 0.5

        # Central channel
        central = m3d.Manifold.cylinder(
            params.length_mm + 0.4,
            channel_radius_mm,
            channel_radius_mm,
            params.resolution
        ).translate([0, 0, -0.2])
        channels.append(central)

        # Surrounding channels in circular pattern
        n_ring = params.channel_count - 1
        for i in range(n_ring):
            angle = 2 * np.pi * i / n_ring
            x = ring_radius * np.cos(angle)
            y = ring_radius * np.sin(angle)

            channel = m3d.Manifold.cylinder(
                params.length_mm + 0.4,
                channel_radius_mm,
                channel_radius_mm,
                params.resolution
            ).translate([x, y, -0.2])
            channels.append(channel)

    # Subtract channels from conduit
    from ..core import batch_union
    all_channels = batch_union(channels)
    conduit = conduit - all_channels

    # Calculate statistics
    mesh = conduit.to_mesh()
    volume = conduit.volume() if hasattr(conduit, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'outer_diameter_mm': params.outer_diameter_mm,
        'channel_count': params.channel_count,
        'channel_diameter_um': params.channel_diameter_um,
        'wall_thickness_mm': params.wall_thickness_mm,
        'scaffold_type': 'nerve_conduit'
    }

    return conduit, stats


def generate_nerve_conduit_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate a nerve conduit scaffold from dictionary parameters.

    Args:
        params: Dictionary of parameters (will be unpacked into NerveConduitParams)

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_nerve_conduit(NerveConduitParams(**params))
