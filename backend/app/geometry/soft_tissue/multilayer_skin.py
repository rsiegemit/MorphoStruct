"""
Multilayer skin scaffold generator with epidermis, dermis, and hypodermis.

Provides parametric generation of skin tissue scaffolds with:
- Epidermis layer (0.1-0.2mm thickness)
- Dermis layer (1-2mm thickness) with higher porosity
- Hypodermis layer (2-5mm thickness) with highest porosity
- Optional vertical vascular channels
- Gradient porosity from outer to inner layers
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class MultilayerSkinParams:
    """Parameters for multilayer skin scaffold generation."""
    epidermis_thickness_mm: float = 0.1
    dermis_thickness_mm: float = 0.8
    hypodermis_thickness_mm: float = 1.2
    diameter_mm: float = 5.0
    pore_gradient: tuple[float, float, float] = (0.2, 0.35, 0.5)  # epidermis, dermis, hypodermis
    vascular_channel_diameter_mm: float = 0.15
    vascular_channel_count: int = 4
    resolution: int = 12


def make_porous_layer(
    diameter: float,
    thickness: float,
    z_offset: float,
    porosity: float,
    pore_size: float,
    resolution: int
) -> m3d.Manifold:
    """
    Create a single porous disc layer.

    Args:
        diameter: Outer diameter of layer
        thickness: Layer thickness
        z_offset: Z position of layer bottom
        porosity: Fraction of volume to be porous (0-1)
        pore_size: Size of individual pores
        resolution: Circular resolution

    Returns:
        Manifold representing the porous layer
    """
    # Create base disc
    radius = diameter / 2
    base = m3d.Manifold.cylinder(thickness, radius, radius, resolution)
    base = base.translate([0, 0, z_offset])

    if porosity <= 0.01:
        return base

    # Calculate pore grid spacing from porosity
    # Assuming circular pores in square grid
    pore_radius = pore_size / 2
    spacing = pore_size / np.sqrt(porosity)

    # Create pore grid
    pores = []
    n_pores = max(1, int(diameter / spacing))

    for i in range(n_pores):
        for j in range(n_pores):
            x = (i - n_pores / 2 + 0.5) * spacing
            y = (j - n_pores / 2 + 0.5) * spacing

            # Check if pore is within circular boundary
            if np.sqrt(x*x + y*y) < radius - pore_radius:
                pore = m3d.Manifold.cylinder(
                    thickness * 1.1,  # Slightly taller to ensure clean subtraction
                    pore_radius,
                    pore_radius,
                    resolution // 2
                )
                pore = pore.translate([x, y, z_offset - thickness * 0.05])
                pores.append(pore)

    if not pores:
        return base

    # Subtract pores from base
    pores_union = batch_union(pores)
    return base - pores_union


def make_vascular_channel(
    diameter: float,
    total_thickness: float,
    channel_diameter: float,
    x_pos: float,
    y_pos: float,
    resolution: int
) -> m3d.Manifold:
    """
    Create a vertical vascular channel through all layers.

    Args:
        diameter: Outer diameter of scaffold
        total_thickness: Total height of all layers
        channel_diameter: Diameter of vascular channel
        x_pos: X position of channel
        y_pos: Y position of channel
        resolution: Circular resolution

    Returns:
        Manifold representing the channel
    """
    channel_radius = channel_diameter / 2
    radius = diameter / 2

    # Check if channel is within boundary
    if np.sqrt(x_pos*x_pos + y_pos*y_pos) > radius - channel_radius:
        return m3d.Manifold()

    channel = m3d.Manifold.cylinder(
        total_thickness * 1.1,
        channel_radius,
        channel_radius,
        resolution // 2
    )
    return channel.translate([x_pos, y_pos, -total_thickness * 0.05])


def generate_multilayer_skin(params: MultilayerSkinParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a multilayer skin scaffold.

    Args:
        params: MultilayerSkinParams specifying geometry and structure

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, layer_thicknesses,
                     porosity_gradient, scaffold_type

    Raises:
        ValueError: If parameters are invalid
    """
    if params.epidermis_thickness_mm <= 0 or params.dermis_thickness_mm <= 0 or params.hypodermis_thickness_mm <= 0:
        raise ValueError("Layer thicknesses must be positive")

    total_thickness = (
        params.epidermis_thickness_mm +
        params.dermis_thickness_mm +
        params.hypodermis_thickness_mm
    )

    # Pore size scales with layer porosity
    epidermis_pore_size = 0.15  # Small pores for epidermis
    dermis_pore_size = 0.25     # Medium pores for dermis
    hypodermis_pore_size = 0.35 # Large pores for hypodermis

    # Create layers from bottom to top
    layers = []

    # Hypodermis (bottom layer)
    z_hypo = 0
    hypo = make_porous_layer(
        params.diameter_mm,
        params.hypodermis_thickness_mm,
        z_hypo,
        params.pore_gradient[2],
        hypodermis_pore_size,
        params.resolution
    )
    layers.append(hypo)

    # Dermis (middle layer)
    z_dermis = z_hypo + params.hypodermis_thickness_mm
    dermis = make_porous_layer(
        params.diameter_mm,
        params.dermis_thickness_mm,
        z_dermis,
        params.pore_gradient[1],
        dermis_pore_size,
        params.resolution
    )
    layers.append(dermis)

    # Epidermis (top layer)
    z_epi = z_dermis + params.dermis_thickness_mm
    epi = make_porous_layer(
        params.diameter_mm,
        params.epidermis_thickness_mm,
        z_epi,
        params.pore_gradient[0],
        epidermis_pore_size,
        params.resolution
    )
    layers.append(epi)

    # Create vascular channels if requested
    if params.vascular_channel_count > 0 and params.vascular_channel_diameter_mm > 0:
        # Distribute channels in circular pattern
        radius = params.diameter_mm / 2 * 0.6  # 60% of radius
        channels = []

        for i in range(params.vascular_channel_count):
            angle = 2 * np.pi * i / params.vascular_channel_count
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)

            channel = make_vascular_channel(
                params.diameter_mm,
                total_thickness,
                params.vascular_channel_diameter_mm,
                x, y,
                params.resolution
            )
            if channel.num_vert() > 0:
                channels.append(channel)

        if channels:
            channels_union = batch_union(channels)
            # Union all layers first, then subtract channels
            result = batch_union(layers)
            result = result - channels_union
        else:
            result = batch_union(layers)
    else:
        result = batch_union(layers)

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'layer_thicknesses_mm': {
            'epidermis': params.epidermis_thickness_mm,
            'dermis': params.dermis_thickness_mm,
            'hypodermis': params.hypodermis_thickness_mm,
            'total': total_thickness
        },
        'porosity_gradient': {
            'epidermis': params.pore_gradient[0],
            'dermis': params.pore_gradient[1],
            'hypodermis': params.pore_gradient[2]
        },
        'vascular_channels': params.vascular_channel_count,
        'scaffold_type': 'multilayer_skin'
    }

    return result, stats


def generate_multilayer_skin_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate multilayer skin scaffold from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching MultilayerSkinParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    pore_gradient = params.get('pore_gradient', (0.3, 0.5, 0.7))
    if isinstance(pore_gradient, dict):
        pore_gradient = (
            pore_gradient.get('epidermis', 0.3),
            pore_gradient.get('dermis', 0.5),
            pore_gradient.get('hypodermis', 0.7)
        )

    return generate_multilayer_skin(MultilayerSkinParams(
        epidermis_thickness_mm=params.get('epidermis_thickness_mm', 0.1),
        dermis_thickness_mm=params.get('dermis_thickness_mm', 0.8),
        hypodermis_thickness_mm=params.get('hypodermis_thickness_mm', 1.2),
        diameter_mm=params.get('diameter_mm', 5.0),
        pore_gradient=pore_gradient,
        vascular_channel_diameter_mm=params.get('vascular_channel_diameter_mm', 0.15),
        vascular_channel_count=params.get('vascular_channel_count', 4),
        resolution=params.get('resolution', 12)
    ))
