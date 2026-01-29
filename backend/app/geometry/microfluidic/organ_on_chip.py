"""
Organ-on-chip microfluidic scaffold generator.

Creates microfluidic channels with tissue chambers for organ-on-chip applications.
Features:
- Configurable inlet channels leading to tissue chambers
- Rectangular tissue chambers (larger cavities for cell culture)
- Output channels for perfusion
- Negative space (channels) carved from solid block
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from typing import Literal
from ..core import batch_union


@dataclass
class OrganOnChipParams:
    """Parameters for organ-on-chip microfluidic scaffold generation."""
    channel_width_mm: float = 0.3  # 300µm default
    channel_depth_mm: float = 0.1  # 100µm default
    chamber_size_mm: tuple[float, float, float] = (1.5, 1.0, 0.15)  # x, y, z (reduced from 3.0, 2.0)
    chamber_count: int = 1  # Reduced from 2
    inlet_count: int = 1  # Reduced from 2
    chip_size_mm: tuple[float, float, float] = (6.0, 4.0, 1.0)  # x, y, z (reduced from 15.0, 10.0, 2.0)
    resolution: int = 6  # Reduced from 8


def make_channel(
    start: np.ndarray,
    end: np.ndarray,
    width: float,
    depth: float,
    resolution: int
) -> m3d.Manifold:
    """
    Create a rectangular channel between two points.

    Args:
        start: Starting point (x, y, z)
        end: Ending point (x, y, z)
        width: Channel width (cross-section)
        depth: Channel depth (cross-section)
        resolution: Mesh resolution

    Returns:
        Manifold representing the channel volume
    """
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = np.sqrt(dx*dx + dy*dy + dz*dz)

    if length < 1e-6:
        return m3d.Manifold()

    # Create rectangular channel along X axis
    channel = m3d.Manifold.cube([length, width, depth], center=True)
    channel = channel.translate([length/2, 0, 0])

    # Calculate rotation to align with direction vector
    h = np.sqrt(dx*dx + dy*dy)  # horizontal distance

    if h > 0.001 or abs(dz) > 0.001:
        # Rotate to align with direction
        angle_z = np.arctan2(dy, dx) * 180 / np.pi
        angle_y = np.arctan2(-dz, h) * 180 / np.pi

        channel = channel.rotate([0, 0, angle_z])
        channel = channel.rotate([0, angle_y, 0])

    return channel.translate([start[0], start[1], start[2]])


def make_chamber(
    center: np.ndarray,
    size: tuple[float, float, float],
    resolution: int
) -> m3d.Manifold:
    """
    Create a rectangular tissue chamber.

    Args:
        center: Center point (x, y, z)
        size: Chamber dimensions (x, y, z)
        resolution: Mesh resolution

    Returns:
        Manifold representing the chamber volume
    """
    chamber = m3d.Manifold.cube(list(size), center=True)
    return chamber.translate([center[0], center[1], center[2]])


def generate_organ_on_chip(params: OrganOnChipParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate an organ-on-chip microfluidic scaffold.

    Creates a solid chip with microfluidic channels and tissue chambers
    carved out as negative space.

    Args:
        params: OrganOnChipParams specifying geometry

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry (solid chip with channels removed)
        - stats_dict: Dictionary with triangle_count, volume_mm3, channel_count,
                     chamber_count, scaffold_type

    Raises:
        ValueError: If no channels are generated
    """
    chip_x, chip_y, chip_z = params.chip_size_mm
    chamber_x, chamber_y, chamber_z = params.chamber_size_mm

    # Create solid chip base
    chip_base = m3d.Manifold.cube([chip_x, chip_y, chip_z], center=True)

    # Calculate chamber positions (evenly spaced along X axis)
    chamber_spacing = chip_x / (params.chamber_count + 1)
    chamber_centers = []
    for i in range(params.chamber_count):
        x_pos = -chip_x/2 + chamber_spacing * (i + 1)
        chamber_centers.append(np.array([x_pos, 0.0, 0.0]))

    # Create chambers
    chambers = []
    for center in chamber_centers:
        chamber = make_chamber(center, params.chamber_size_mm, params.resolution)
        chambers.append(chamber)

    # Create inlet channels
    inlet_channels = []
    inlet_spacing = chip_y / (params.inlet_count + 1)

    for i in range(params.inlet_count):
        y_pos = -chip_y/2 + inlet_spacing * (i + 1)

        # Inlet from top edge to first chamber
        start = np.array([-chip_x/2, y_pos, 0.0])
        end = np.array([chamber_centers[0][0] - chamber_x/2, y_pos, 0.0])

        channel = make_channel(
            start, end,
            params.channel_width_mm,
            params.channel_depth_mm,
            params.resolution
        )
        inlet_channels.append(channel)

    # Create inter-chamber channels
    inter_channels = []
    for i in range(len(chamber_centers) - 1):
        # Connect chambers along centerline
        start = np.array([
            chamber_centers[i][0] + chamber_x/2,
            0.0,
            0.0
        ])
        end = np.array([
            chamber_centers[i+1][0] - chamber_x/2,
            0.0,
            0.0
        ])

        channel = make_channel(
            start, end,
            params.channel_width_mm,
            params.channel_depth_mm,
            params.resolution
        )
        inter_channels.append(channel)

    # Create outlet channels
    outlet_channels = []
    for i in range(params.inlet_count):
        y_pos = -chip_y/2 + inlet_spacing * (i + 1)

        # Outlet from last chamber to right edge
        start = np.array([chamber_centers[-1][0] + chamber_x/2, y_pos, 0.0])
        end = np.array([chip_x/2, y_pos, 0.0])

        channel = make_channel(
            start, end,
            params.channel_width_mm,
            params.channel_depth_mm,
            params.resolution
        )
        outlet_channels.append(channel)

    # Combine all channel/chamber features
    all_features = chambers + inlet_channels + inter_channels + outlet_channels

    if not all_features:
        raise ValueError("No channels or chambers generated")

    # Union all features
    features_combined = batch_union(all_features)

    # Subtract from chip base (create negative space)
    result = chip_base - features_combined

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    total_channels = len(inlet_channels) + len(inter_channels) + len(outlet_channels)

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'channel_count': total_channels,
        'chamber_count': params.chamber_count,
        'scaffold_type': 'organ_on_chip'
    }

    return result, stats


def generate_organ_on_chip_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate organ-on-chip from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching OrganOnChipParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    # Handle chamber_size variations
    chamber_size = params.get('chamber_size_mm', params.get('chamber_size', (3.0, 2.0, 0.15)))
    if isinstance(chamber_size, dict):
        chamber_size = (chamber_size['x'], chamber_size['y'], chamber_size['z'])

    # Handle chip_size variations
    chip_size = params.get('chip_size_mm', params.get('chip_size', (15.0, 10.0, 2.0)))
    if isinstance(chip_size, dict):
        chip_size = (chip_size['x'], chip_size['y'], chip_size['z'])

    return generate_organ_on_chip(OrganOnChipParams(
        channel_width_mm=params.get('channel_width_mm', params.get('channel_width', 0.3)),
        channel_depth_mm=params.get('channel_depth_mm', params.get('channel_depth', 0.1)),
        chamber_size_mm=tuple(chamber_size) if chamber_size != (3.0, 2.0, 0.15) else (1.5, 1.0, 0.15),
        chamber_count=params.get('chamber_count', 1),
        inlet_count=params.get('inlet_count', 1),
        chip_size_mm=tuple(chip_size) if chip_size != (15.0, 10.0, 2.0) else (6.0, 4.0, 1.0),
        resolution=params.get('resolution', 6)
    ))
