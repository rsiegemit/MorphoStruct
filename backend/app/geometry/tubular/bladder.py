"""
Bladder scaffold generator.

Generates multi-layer bladder wall structures with dome-shaped geometry
representing urothelium, lamina propria, and detrusor muscle layers.
"""

import manifold3d as m3d
import numpy as np
from dataclasses import dataclass


@dataclass
class BladderParams:
    """Parameters for bladder scaffold generation."""

    diameter_mm: float = 40.0  # Adult human bladder ~50-100mm when moderately full
    wall_thickness_mm: float = 2.0  # Bladder wall ~2-5mm
    layer_count: int = 2  # Typically 3 layers: urothelium, lamina propria, detrusor
    dome_curvature: float = 0.6  # 0.5 = hemisphere, 1.0 = full sphere, <0.5 = flatter
    resolution: int = 20

    def __post_init__(self):
        if self.layer_count < 2 or self.layer_count > 4:
            raise ValueError("layer_count must be between 2 and 4")
        if self.dome_curvature < 0.3 or self.dome_curvature > 1.0:
            raise ValueError("dome_curvature must be between 0.3 and 1.0")


def generate_bladder(params: BladderParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a bladder scaffold with multi-layer dome-shaped wall.

    Creates a hemispherical dome structure with layered walls representing
    the urothelium (inner lining), lamina propria, and detrusor muscle.

    Args:
        params: BladderParams with generation parameters

    Returns:
        Tuple of (manifold, stats_dict)

    Raises:
        ValueError: If parameters are invalid
    """
    outer_radius = params.diameter_mm / 2
    inner_radius = outer_radius - params.wall_thickness_mm

    if inner_radius <= 0:
        raise ValueError("Wall thickness exceeds radius")

    # Calculate layer thicknesses (equal distribution)
    layer_thickness = params.wall_thickness_mm / params.layer_count

    # Create dome by intersecting sphere with half-space
    def create_dome_layer(radius: float) -> m3d.Manifold:
        """Create a hemispherical dome at given radius."""
        # Create sphere
        sphere = m3d.Manifold.sphere(radius, params.resolution)

        # Determine dome height based on curvature
        # curvature=0.5 → hemisphere (height=radius)
        # curvature=1.0 → full sphere (height=2*radius)
        # curvature<0.5 → flatter dome
        dome_height = radius * 2 * params.dome_curvature

        # Create cutting plane - keep everything above z=-(radius - dome_height)
        cut_z = -(radius - dome_height)

        # Create a large cube to cut with
        cutter = m3d.Manifold.cube([radius * 4, radius * 4, radius * 4], center=True)
        cutter = cutter.translate([0, 0, cut_z - radius * 2])

        # Subtract lower part
        dome = sphere - cutter

        return dome

    # Build layers from inside out
    layers = []

    for i in range(params.layer_count):
        r_inner = inner_radius + (i * layer_thickness)
        r_outer = inner_radius + ((i + 1) * layer_thickness)

        outer_dome = create_dome_layer(r_outer)
        inner_dome = create_dome_layer(r_inner)

        # Create layer as difference
        layer = outer_dome - inner_dome
        layers.append(layer)

    # Combine all layers
    from ..core import batch_union
    bladder = batch_union(layers)

    # Calculate statistics
    mesh = bladder.to_mesh()
    volume = bladder.volume() if hasattr(bladder, 'volume') else 0

    # Calculate dome height
    dome_height = outer_radius * 2 * params.dome_curvature

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'diameter_mm': params.diameter_mm,
        'wall_thickness_mm': params.wall_thickness_mm,
        'layer_count': params.layer_count,
        'layer_thickness_mm': layer_thickness,
        'dome_height_mm': dome_height,
        'dome_curvature': params.dome_curvature,
        'scaffold_type': 'bladder'
    }

    return bladder, stats


def generate_bladder_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate a bladder scaffold from dictionary parameters.

    Args:
        params: Dictionary of parameters (will be unpacked into BladderParams)

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_bladder(BladderParams(**params))
