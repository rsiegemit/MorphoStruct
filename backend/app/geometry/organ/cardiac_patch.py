"""
Cardiac patch scaffold generator.

Creates aligned microfibrous scaffolds for cardiomyocyte culture with:
- Parallel fibers in grid pattern
- Angular offset between layers for mechanical reinforcement
- Controlled fiber spacing and diameter
- Multi-layer architecture
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class CardiacPatchParams:
    """Parameters for cardiac patch scaffold generation."""
    fiber_spacing: float = 500.0  # µm (increased from 300 to reduce fiber count)
    fiber_diameter: float = 100.0  # µm (50-200µm)
    patch_size: tuple[float, float, float] = (5.0, 5.0, 0.5)  # mm (reduced from 10x10x1)
    layer_count: int = 2  # reduced from 3
    alignment_angle: float = 0.0  # degrees, angle offset between layers
    resolution: int = 6  # reduced from 8


def make_fiber(start: np.ndarray, end: np.ndarray, radius: float, resolution: int) -> m3d.Manifold:
    """
    Create a cylindrical fiber between two points.

    Args:
        start: Starting point (x, y, z)
        end: Ending point (x, y, z)
        radius: Fiber radius
        resolution: Number of segments around cylinder

    Returns:
        Fiber manifold
    """
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = np.sqrt(dx*dx + dy*dy + dz*dz)

    if length < 1e-6:
        return m3d.Manifold()

    fiber = m3d.Manifold.cylinder(length, radius, radius, resolution)

    h = np.sqrt(dx*dx + dy*dy)
    if h > 0.001 or abs(dz) > 0.001:
        tilt = np.arctan2(h, dz) * 180 / np.pi
        azim = np.arctan2(dy, dx) * 180 / np.pi
        fiber = fiber.rotate([0, tilt, 0]).rotate([0, 0, azim])

    return fiber.translate([start[0], start[1], start[2]])


def generate_cardiac_patch(params: CardiacPatchParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a cardiac patch scaffold with aligned microfibers.

    Args:
        params: CardiacPatchParams specifying geometry

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, fiber_count, scaffold_type

    Raises:
        ValueError: If no fibers are generated
    """
    # Convert µm to mm
    spacing_mm = params.fiber_spacing / 1000.0
    diameter_mm = params.fiber_diameter / 1000.0
    radius_mm = diameter_mm / 2.0

    px, py, pz = params.patch_size
    layer_height = pz / params.layer_count

    all_fibers = []
    total_fiber_count = 0

    for layer_idx in range(params.layer_count):
        z_center = (layer_idx + 0.5) * layer_height

        # Calculate layer rotation angle
        layer_angle = params.alignment_angle * layer_idx
        angle_rad = np.radians(layer_angle)
        cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)

        # Generate fibers in X direction (along patch)
        num_fibers_y = int(py / spacing_mm) + 1
        for i in range(num_fibers_y):
            y_pos = -py/2 + i * spacing_mm

            # Fiber runs across entire X dimension
            start_local = np.array([-px/2, y_pos, 0])
            end_local = np.array([px/2, y_pos, 0])

            # Rotate fiber by layer angle
            start_rot = np.array([
                start_local[0] * cos_a - start_local[1] * sin_a,
                start_local[0] * sin_a + start_local[1] * cos_a,
                z_center
            ])
            end_rot = np.array([
                end_local[0] * cos_a - end_local[1] * sin_a,
                end_local[0] * sin_a + end_local[1] * cos_a,
                z_center
            ])

            # Clip to bounding box
            if abs(start_rot[0]) <= px/2 and abs(start_rot[1]) <= py/2:
                if abs(end_rot[0]) <= px/2 and abs(end_rot[1]) <= py/2:
                    fiber = make_fiber(start_rot, end_rot, radius_mm, params.resolution)
                    if fiber.num_vert() > 0:
                        all_fibers.append(fiber)
                        total_fiber_count += 1

        # Generate fibers in Y direction (perpendicular)
        num_fibers_x = int(px / spacing_mm) + 1
        for i in range(num_fibers_x):
            x_pos = -px/2 + i * spacing_mm

            # Fiber runs across entire Y dimension
            start_local = np.array([x_pos, -py/2, 0])
            end_local = np.array([x_pos, py/2, 0])

            # Rotate fiber by layer angle
            start_rot = np.array([
                start_local[0] * cos_a - start_local[1] * sin_a,
                start_local[0] * sin_a + start_local[1] * cos_a,
                z_center
            ])
            end_rot = np.array([
                end_local[0] * cos_a - end_local[1] * sin_a,
                end_local[0] * sin_a + end_local[1] * cos_a,
                z_center
            ])

            # Clip to bounding box
            if abs(start_rot[0]) <= px/2 and abs(start_rot[1]) <= py/2:
                if abs(end_rot[0]) <= px/2 and abs(end_rot[1]) <= py/2:
                    fiber = make_fiber(start_rot, end_rot, radius_mm, params.resolution)
                    if fiber.num_vert() > 0:
                        all_fibers.append(fiber)
                        total_fiber_count += 1

    if not all_fibers:
        raise ValueError("No fibers generated")

    result = batch_union(all_fibers)

    # Clip to exact bounding box
    bbox = m3d.Manifold.cube([px, py, pz])
    result = result ^ bbox

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'fiber_count': total_fiber_count,
        'scaffold_type': 'cardiac_patch'
    }

    return result, stats


def generate_cardiac_patch_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate cardiac patch from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching CardiacPatchParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    # Handle patch size variations
    patch_size = params.get('patch_size', (5.0, 5.0, 0.5))
    if isinstance(patch_size, dict):
        patch_size = (patch_size['x'], patch_size['y'], patch_size['z'])

    return generate_cardiac_patch(CardiacPatchParams(
        fiber_spacing=params.get('fiber_spacing', 500.0),
        fiber_diameter=params.get('fiber_diameter', 100.0),
        patch_size=tuple(patch_size),
        layer_count=params.get('layer_count', 2),
        alignment_angle=params.get('alignment_angle', 0.0),
        resolution=params.get('resolution', 6)
    ))
