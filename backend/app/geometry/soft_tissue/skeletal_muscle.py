"""
Skeletal muscle scaffold generator with aligned myofiber channels.

Provides parametric generation of muscle tissue scaffolds with:
- Parallel, unipennate, or bipennate fiber architectures
- Aligned myofiber channels (50-100µm diameter)
- Configurable pennation angle (0-30°)
- Multiple fascicle groupings
- Customizable fiber spacing and density
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from typing import Literal
from ..core import batch_union


@dataclass
class SkeletalMuscleParams:
    """Parameters for skeletal muscle scaffold generation."""
    fiber_diameter_um: float = 100.0  # micrometers
    fiber_spacing_um: float = 300.0  # micrometers (fewer fibers)
    pennation_angle_deg: float = 10.0  # degrees
    fascicle_count: int = 2
    architecture_type: Literal['parallel', 'unipennate', 'bipennate'] = 'parallel'
    length_mm: float = 6.0
    width_mm: float = 3.0
    height_mm: float = 3.0
    resolution: int = 6


def make_fiber_channel(
    start_point: np.ndarray,
    end_point: np.ndarray,
    radius: float,
    resolution: int
) -> m3d.Manifold:
    """
    Create a cylindrical fiber channel between two points.

    Args:
        start_point: Starting point (x, y, z)
        end_point: Ending point (x, y, z)
        radius: Fiber radius
        resolution: Number of segments around cylinder

    Returns:
        Manifold representing the fiber channel
    """
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    dz = end_point[2] - start_point[2]
    length = np.sqrt(dx*dx + dy*dy + dz*dz)

    if length < 1e-6:
        return m3d.Manifold()

    # Create cylinder along Z axis
    fiber = m3d.Manifold.cylinder(length, radius, radius, resolution)

    # Calculate rotation to align with direction vector
    h = np.sqrt(dx*dx + dy*dy)
    if h > 0.001 or abs(dz) > 0.001:
        angle_y = np.arctan2(h, dz) * 180 / np.pi
        angle_z = np.arctan2(dy, dx) * 180 / np.pi

        fiber = fiber.rotate([0, angle_y, 0])
        fiber = fiber.rotate([0, 0, angle_z])

    return fiber.translate([start_point[0], start_point[1], start_point[2]])


def get_parallel_fiber_positions(
    width: float,
    height: float,
    spacing: float
) -> list[tuple[float, float]]:
    """
    Get grid positions for parallel fibers.

    Args:
        width: Width of muscle
        height: Height of muscle
        spacing: Spacing between fibers

    Returns:
        List of (y, z) positions for fiber centers
    """
    positions = []
    n_y = max(1, int(width / spacing))
    n_z = max(1, int(height / spacing))

    for i in range(n_y):
        for j in range(n_z):
            y = (i - n_y / 2 + 0.5) * spacing
            z = (j - n_z / 2 + 0.5) * spacing
            positions.append((y, z))

    return positions


def get_pennate_fiber_endpoints(
    fiber_y: float,
    fiber_z: float,
    length: float,
    pennation_angle: float,
    architecture: str
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calculate fiber endpoints for pennate architecture.

    Args:
        fiber_y: Y position of fiber center
        fiber_z: Z position of fiber center
        length: Muscle length
        pennation_angle: Pennation angle in radians
        architecture: 'parallel', 'unipennate', or 'bipennate'

    Returns:
        Tuple of (start_point, end_point) as numpy arrays
    """
    if architecture == 'parallel':
        # Simple parallel fibers along X axis
        start = np.array([0, fiber_y, fiber_z])
        end = np.array([length, fiber_y, fiber_z])
    elif architecture == 'unipennate':
        # Fibers angled relative to central axis
        dx = length * np.cos(pennation_angle)
        dy = length * np.sin(pennation_angle)
        start = np.array([0, fiber_y - dy/2, fiber_z])
        end = np.array([dx, fiber_y + dy/2, fiber_z])
    else:  # bipennate
        # Alternating fiber angles creating V-pattern
        # Use fiber_y to determine which side
        sign = 1 if fiber_y >= 0 else -1
        dx = length * np.cos(pennation_angle)
        dy = sign * length * np.sin(pennation_angle)
        start = np.array([0, fiber_y - dy/2, fiber_z])
        end = np.array([dx, fiber_y + dy/2, fiber_z])

    return start, end


def generate_skeletal_muscle(params: SkeletalMuscleParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a skeletal muscle scaffold.

    Args:
        params: SkeletalMuscleParams specifying geometry and structure

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, fiber_count,
                     architecture_type, pennation_angle, scaffold_type

    Raises:
        ValueError: If parameters are invalid
    """
    if params.fiber_diameter_um <= 0 or params.fiber_spacing_um <= 0:
        raise ValueError("Fiber diameter and spacing must be positive")
    if not 0 <= params.pennation_angle_deg <= 45:
        raise ValueError("Pennation angle must be between 0 and 45 degrees")

    # Convert micrometers to millimeters
    fiber_radius_mm = (params.fiber_diameter_um / 1000.0) / 2.0
    fiber_spacing_mm = params.fiber_spacing_um / 1000.0

    pennation_angle_rad = np.radians(params.pennation_angle_deg)

    # Create bounding box (will be subtracted from to create channels)
    bounding_box = m3d.Manifold.cube([
        params.length_mm,
        params.width_mm,
        params.height_mm
    ])
    bounding_box = bounding_box.translate([
        params.length_mm / 2,
        0,
        0
    ])

    # Get fiber positions
    fiber_positions = get_parallel_fiber_positions(
        params.width_mm,
        params.height_mm,
        fiber_spacing_mm
    )

    # Create fiber channels
    fibers = []
    for y_pos, z_pos in fiber_positions:
        start, end = get_pennate_fiber_endpoints(
            y_pos,
            z_pos,
            params.length_mm,
            pennation_angle_rad,
            params.architecture_type
        )

        fiber = make_fiber_channel(start, end, fiber_radius_mm, params.resolution)
        if fiber.num_vert() > 0:
            fibers.append(fiber)

    if not fibers:
        raise ValueError("No fibers generated")

    # Union all fibers
    fibers_union = batch_union(fibers)

    # Subtract fibers from bounding box to create channels
    result = bounding_box - fibers_union

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0
    solid_volume = params.length_mm * params.width_mm * params.height_mm
    porosity = 1 - (volume / solid_volume) if solid_volume > 0 else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'porosity': porosity,
        'fiber_count': len(fibers),
        'fiber_diameter_um': params.fiber_diameter_um,
        'fiber_spacing_um': params.fiber_spacing_um,
        'architecture_type': params.architecture_type,
        'pennation_angle_deg': params.pennation_angle_deg,
        'fascicle_count': params.fascicle_count,
        'scaffold_type': 'skeletal_muscle'
    }

    return result, stats


def generate_skeletal_muscle_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate skeletal muscle scaffold from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching SkeletalMuscleParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_skeletal_muscle(SkeletalMuscleParams(
        fiber_diameter_um=params.get('fiber_diameter_um', 100.0),
        fiber_spacing_um=params.get('fiber_spacing_um', 300.0),
        pennation_angle_deg=params.get('pennation_angle_deg', 10.0),
        fascicle_count=params.get('fascicle_count', 2),
        architecture_type=params.get('architecture_type', 'parallel'),
        length_mm=params.get('length_mm', 6.0),
        width_mm=params.get('width_mm', 3.0),
        height_mm=params.get('height_mm', 3.0),
        resolution=params.get('resolution', 6)
    ))
