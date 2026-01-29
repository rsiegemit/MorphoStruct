"""
Intervertebral disc scaffold generator with annulus fibrosus and nucleus pulposus.

Creates a disc-shaped structure with:
- Annulus fibrosus: concentric rings with alternating fiber angles
- Nucleus pulposus: soft gel-like center with high porosity
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class IntervertebralDiscParams:
    """Parameters for intervertebral disc scaffold generation."""
    disc_diameter: float = 20.0
    disc_height: float = 5.0
    af_ring_count: int = 3  # Annulus fibrosus concentric rings
    np_diameter: float = 8.0  # Nucleus pulposus diameter
    af_layer_angle: float = 30.0  # Fiber angle alternates ±30°
    fiber_diameter: float = 0.2
    np_porosity: float = 0.85  # High porosity for gel-like center
    resolution: int = 16


def generate_intervertebral_disc(params: IntervertebralDiscParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate an intervertebral disc scaffold.

    Creates two distinct regions:
    1. Nucleus pulposus (center) - highly porous gel-like structure
    2. Annulus fibrosus (outer) - concentric rings with alternating fiber angles

    Args:
        params: IntervertebralDiscParams specifying geometry and structure

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, ring_count,
                     af_volume, np_volume, scaffold_type
    """
    disc_radius = params.disc_diameter / 2
    np_radius = params.np_diameter / 2
    fiber_radius = params.fiber_diameter / 2

    # Create nucleus pulposus (porous center)
    np_manifold = create_nucleus_pulposus(
        radius=np_radius,
        height=params.disc_height,
        porosity=params.np_porosity,
        resolution=params.resolution
    )

    # Create annulus fibrosus (concentric rings)
    af_manifolds = []

    ring_width = (disc_radius - np_radius) / params.af_ring_count

    for ring_idx in range(params.af_ring_count):
        r_inner = np_radius + ring_idx * ring_width
        r_outer = r_inner + ring_width

        # Alternating fiber angle: +30°, -30°, +30°, etc.
        fiber_angle = params.af_layer_angle if (ring_idx % 2 == 0) else -params.af_layer_angle

        ring_fibers = create_af_ring(
            r_inner=r_inner,
            r_outer=r_outer,
            height=params.disc_height,
            fiber_angle=fiber_angle,
            fiber_radius=fiber_radius,
            resolution=params.resolution
        )

        af_manifolds.extend(ring_fibers)

    # Combine all parts
    all_parts = [np_manifold] + af_manifolds

    result = batch_union(all_parts)

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    # Approximate volume distribution
    np_vol_ratio = (np_radius ** 2) / (disc_radius ** 2)
    np_volume = volume * np_vol_ratio
    af_volume = volume * (1 - np_vol_ratio)

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'ring_count': params.af_ring_count,
        'af_volume_mm3': af_volume,
        'np_volume_mm3': np_volume,
        'fiber_count': len(af_manifolds),
        'scaffold_type': 'intervertebral_disc'
    }

    return result, stats


def create_nucleus_pulposus(
    radius: float,
    height: float,
    porosity: float,
    resolution: int
) -> m3d.Manifold:
    """
    Create nucleus pulposus with high porosity (gel-like center).

    Args:
        radius: Radius of nucleus pulposus
        height: Height of disc
        porosity: Target porosity (0.8-0.95)
        resolution: Angular resolution

    Returns:
        Porous nucleus pulposus manifold
    """
    # Create base cylinder
    base = m3d.Manifold.cylinder(height, radius, radius, resolution)

    # Create random spherical pores for high porosity
    pore_radius = radius * 0.15
    pore_spacing = pore_radius * 3.5  # Increased spacing for faster generation

    n_radial = max(2, int(radius / pore_spacing))
    n_angular = max(4, int(2 * np.pi * radius / pore_spacing))
    n_vertical = max(2, int(height / pore_spacing))

    pores = []
    for i in range(n_radial):
        r = (i + 0.5) * (radius / n_radial) * 0.8

        for j in range(n_angular):
            angle = j * 2 * np.pi / n_angular

            for k in range(n_vertical):
                x = r * np.cos(angle)
                y = r * np.sin(angle)
                z = (k + 0.5) * (height / n_vertical)

                pore = m3d.Manifold.sphere(pore_radius, resolution // 2)
                pore = pore.translate([x, y, z])
                pores.append(pore)

    # Subtract pores from base
    result = base
    for pore in pores:
        result = result - pore

    return result


def create_af_ring(
    r_inner: float,
    r_outer: float,
    height: float,
    fiber_angle: float,
    fiber_radius: float,
    resolution: int
) -> list[m3d.Manifold]:
    """
    Create annulus fibrosus ring with angled fibers.

    Fibers spiral around the disc at a specific angle (±30° typical).

    Args:
        r_inner: Inner radius of ring
        r_outer: Outer radius of ring
        height: Height of disc
        fiber_angle: Fiber angle in degrees (+ or -)
        fiber_radius: Radius of individual fibers
        resolution: Angular and path resolution

    Returns:
        List of fiber manifolds forming this ring
    """
    fibers = []

    r_mid = (r_inner + r_outer) / 2
    ring_width = r_outer - r_inner

    # Number of fibers around circumference
    circumference = 2 * np.pi * r_mid
    fiber_spacing = fiber_radius * 6
    n_fibers = max(6, int(circumference / fiber_spacing))

    for i in range(n_fibers):
        # Starting angle for this fiber
        angle_start = i * 2 * np.pi / n_fibers

        # Create helical fiber path
        fiber = create_helical_fiber(
            r_mid=r_mid,
            ring_width=ring_width,
            height=height,
            angle_start=angle_start,
            fiber_angle=fiber_angle,
            fiber_radius=fiber_radius,
            resolution=resolution
        )

        if fiber.num_vert() > 0:
            fibers.append(fiber)

    return fibers


def create_helical_fiber(
    r_mid: float,
    ring_width: float,
    height: float,
    angle_start: float,
    fiber_angle: float,
    fiber_radius: float,
    resolution: int
) -> m3d.Manifold:
    """
    Create a helical fiber wrapping around at specified angle.

    Args:
        r_mid: Mid-radius of ring
        ring_width: Width of ring (radial extent)
        height: Height of disc
        angle_start: Starting angular position
        fiber_angle: Helix angle in degrees
        fiber_radius: Radius of fiber
        resolution: Number of segments for smooth curve

    Returns:
        Helical fiber manifold
    """
    # Number of segments for one complete wrap
    n_segments = max(8, int(2 * np.pi * r_mid / (fiber_radius * 3)))

    # Calculate pitch (vertical rise per full rotation)
    pitch = 2 * np.pi * r_mid * np.tan(fiber_angle * np.pi / 180)

    # Number of rotations to cover height
    n_rotations = height / abs(pitch) if pitch != 0 else 0.5

    # Generate path points
    path_points = []
    total_angle = n_rotations * 2 * np.pi

    for i in range(int(n_segments * n_rotations) + 1):
        t = i / (n_segments * n_rotations) if n_rotations > 0 else 0.5
        angle = angle_start + t * total_angle

        # Slight radial variation within ring width
        r = r_mid + (np.sin(i * 0.5) * ring_width * 0.3)

        x = r * np.cos(angle)
        y = r * np.sin(angle)
        z = t * height

        path_points.append(np.array([x, y, z]))

    # Create segments
    segments = []
    for i in range(len(path_points) - 1):
        p1 = path_points[i]
        p2 = path_points[i + 1]

        segment = make_fiber_segment(p1, p2, fiber_radius, resolution)
        if segment.num_vert() > 0:
            segments.append(segment)

    if not segments:
        return m3d.Manifold()

    # Union segments
    result = segments[0]
    for seg in segments[1:]:
        result = result + seg

    return result


def make_fiber_segment(p1: np.ndarray, p2: np.ndarray, radius: float, resolution: int) -> m3d.Manifold:
    """
    Create a cylindrical fiber segment between two points.

    Args:
        p1: Starting point (x, y, z)
        p2: Ending point (x, y, z)
        radius: Segment radius
        resolution: Number of segments around cylinder

    Returns:
        Manifold representing the segment cylinder
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    length = np.sqrt(dx*dx + dy*dy + dz*dz)

    if length < 1e-6:
        return m3d.Manifold()

    # Create cylinder along Z axis
    segment = m3d.Manifold.cylinder(length, radius, radius, resolution)

    # Calculate rotation to align with direction vector
    h = np.sqrt(dx*dx + dy*dy)
    if h > 0.001 or abs(dz) > 0.001:
        angle_y = np.arctan2(h, dz) * 180 / np.pi
        angle_z = np.arctan2(dy, dx) * 180 / np.pi

        segment = segment.rotate([0, angle_y, 0])
        segment = segment.rotate([0, 0, angle_z])

    return segment.translate([p1[0], p1[1], p1[2]])


def generate_intervertebral_disc_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate intervertebral disc from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching IntervertebralDiscParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_intervertebral_disc(IntervertebralDiscParams(
        disc_diameter=params.get('disc_diameter', 20.0),
        disc_height=params.get('disc_height', 5.0),
        af_ring_count=params.get('af_ring_count', 3),
        np_diameter=params.get('np_diameter', 8.0),
        af_layer_angle=params.get('af_layer_angle', 30.0),
        fiber_diameter=params.get('fiber_diameter', 0.2),
        np_porosity=params.get('np_porosity', 0.85),
        resolution=params.get('resolution', 16)
    ))
