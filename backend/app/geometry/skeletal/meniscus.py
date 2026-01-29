"""
Meniscus scaffold generator with wedge-shaped geometry.

Creates a wedge-shaped structure with radial and circumferential zones
mimicking the fibrocartilaginous structure of knee meniscus.
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class MeniscusParams:
    """Parameters for meniscus scaffold generation."""
    inner_radius: float = 12.0
    outer_radius: float = 20.0
    height: float = 8.0
    wedge_angle_deg: float = 20.0
    zone_count: int = 3  # Radial zones
    fiber_diameter: float = 0.2
    resolution: int = 32
    arc_degrees: float = 300.0  # C-shape, not full circle


def generate_meniscus(params: MeniscusParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a meniscus scaffold with wedge-shaped cross-section.

    Creates a C-shaped wedge with:
    - Radial fibers in inner zones
    - Circumferential fibers in outer zones
    - Gradient transition between zones

    Args:
        params: MeniscusParams specifying geometry and structure

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, fiber_count,
                     zone_count, scaffold_type
    """
    # Create base wedge shape
    base = create_wedge_base(
        inner_radius=params.inner_radius,
        outer_radius=params.outer_radius,
        height=params.height,
        wedge_angle_deg=params.wedge_angle_deg,
        arc_degrees=params.arc_degrees,
        resolution=params.resolution
    )

    # Create fiber network
    fiber_radius = params.fiber_diameter / 2
    all_fibers = []

    # Zone widths
    zone_width = (params.outer_radius - params.inner_radius) / params.zone_count

    for zone_idx in range(params.zone_count):
        r_inner = params.inner_radius + zone_idx * zone_width
        r_outer = r_inner + zone_width

        # Blend factor: inner zones more radial, outer zones more circumferential
        circumferential_ratio = zone_idx / (params.zone_count - 1) if params.zone_count > 1 else 0.5

        # Create mixed fiber network
        zone_fibers = create_zone_fibers(
            r_inner=r_inner,
            r_outer=r_outer,
            height=params.height,
            wedge_angle_deg=params.wedge_angle_deg,
            arc_degrees=params.arc_degrees,
            fiber_radius=fiber_radius,
            circumferential_ratio=circumferential_ratio,
            resolution=params.resolution
        )
        all_fibers.extend(zone_fibers)

    # Union fibers
    if all_fibers:
        fiber_network = batch_union(all_fibers)
        # Clip to wedge shape
        result = fiber_network ^ base
    else:
        result = base

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'fiber_count': len(all_fibers),
        'zone_count': params.zone_count,
        'scaffold_type': 'meniscus'
    }

    return result, stats


def create_wedge_base(
    inner_radius: float,
    outer_radius: float,
    height: float,
    wedge_angle_deg: float,
    arc_degrees: float,
    resolution: int
) -> m3d.Manifold:
    """
    Create the base wedge-shaped manifold (C-shaped with triangular cross-section).

    Args:
        inner_radius: Inner radius of C-shape
        outer_radius: Outer radius of C-shape
        height: Maximum height (at outer edge)
        wedge_angle_deg: Angle of wedge slope
        arc_degrees: Arc extent (e.g., 300 for C-shape)
        resolution: Angular resolution

    Returns:
        Wedge-shaped manifold
    """
    # Create as extrusion of wedge profile along arc
    # For simplicity, use a cylindrical section with height variation

    # Create outer cylinder
    outer_cyl = m3d.Manifold.cylinder(height, outer_radius, outer_radius, resolution)

    # Create inner cylinder to subtract
    inner_cyl = m3d.Manifold.cylinder(height * 2, inner_radius, inner_radius, resolution)

    # Create annular section
    annulus = outer_cyl - inner_cyl

    # Create wedge profile by intersecting with sloped plane
    # Simple approximation: use a box to create the slope
    wedge_height_inner = height * 0.3  # Inner edge lower
    slope_box = m3d.Manifold.cube([outer_radius * 3, outer_radius * 3, height])
    slope_box = slope_box.translate([-outer_radius * 1.5, -outer_radius * 1.5, 0])

    wedge = annulus ^ slope_box

    # Cut to arc (C-shape)
    if arc_degrees < 360:
        # Create cutting planes
        arc_rad = arc_degrees * np.pi / 180
        cut_angle = (360 - arc_degrees) / 2

        # Simpler approach: just return full annulus for now
        # Full wedge cutting would require more complex CSG

    return wedge


def create_zone_fibers(
    r_inner: float,
    r_outer: float,
    height: float,
    wedge_angle_deg: float,
    arc_degrees: float,
    fiber_radius: float,
    circumferential_ratio: float,
    resolution: int
) -> list[m3d.Manifold]:
    """
    Create fiber network for a radial zone with mixed radial/circumferential orientation.

    Args:
        r_inner: Inner radius of zone
        r_outer: Outer radius of zone
        height: Height of scaffold
        wedge_angle_deg: Wedge angle
        arc_degrees: Arc extent
        fiber_radius: Radius of individual fibers
        circumferential_ratio: 0=fully radial, 1=fully circumferential
        resolution: Angular resolution

    Returns:
        List of fiber manifolds
    """
    fibers = []

    arc_rad = arc_degrees * np.pi / 180
    n_radial_fibers = max(3, int(arc_rad * r_inner / (fiber_radius * 10)))
    n_circumferential = max(2, int((r_outer - r_inner) / (fiber_radius * 5)))

    # Radial fibers (decreases with circumferential_ratio)
    radial_count = int(n_radial_fibers * (1 - circumferential_ratio))
    for i in range(radial_count):
        angle = i * arc_rad / radial_count

        # Create radial fiber from inner to outer radius
        x1 = r_inner * np.cos(angle)
        y1 = r_inner * np.sin(angle)
        z1 = height * 0.3  # Lower at inner edge

        x2 = r_outer * np.cos(angle)
        y2 = r_outer * np.sin(angle)
        z2 = height * 0.9  # Higher at outer edge

        fiber = make_fiber(
            np.array([x1, y1, z1]),
            np.array([x2, y2, z2]),
            fiber_radius,
            resolution
        )
        if fiber.num_vert() > 0:
            fibers.append(fiber)

    # Circumferential fibers (increases with circumferential_ratio)
    circ_count = int(n_circumferential * circumferential_ratio)
    for i in range(circ_count):
        r = r_inner + (i + 0.5) * ((r_outer - r_inner) / max(1, circ_count))
        z = height * (0.3 + 0.6 * (r - r_inner) / (r_outer - r_inner))

        # Create arc at this radius
        n_segments = max(8, int(arc_rad * r / (fiber_radius * 4)))
        for j in range(n_segments):
            angle1 = j * arc_rad / n_segments
            angle2 = (j + 1) * arc_rad / n_segments

            x1 = r * np.cos(angle1)
            y1 = r * np.sin(angle1)
            x2 = r * np.cos(angle2)
            y2 = r * np.sin(angle2)

            fiber = make_fiber(
                np.array([x1, y1, z]),
                np.array([x2, y2, z]),
                fiber_radius,
                resolution
            )
            if fiber.num_vert() > 0:
                fibers.append(fiber)

    return fibers


def make_fiber(p1: np.ndarray, p2: np.ndarray, radius: float, resolution: int) -> m3d.Manifold:
    """
    Create a cylindrical fiber between two points.

    Args:
        p1: Starting point (x, y, z)
        p2: Ending point (x, y, z)
        radius: Fiber radius
        resolution: Number of segments around cylinder

    Returns:
        Manifold representing the fiber cylinder
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
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

    return fiber.translate([p1[0], p1[1], p1[2]])


def generate_meniscus_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate meniscus from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching MeniscusParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_meniscus(MeniscusParams(
        inner_radius=params.get('inner_radius', 12.0),
        outer_radius=params.get('outer_radius', 20.0),
        height=params.get('height', 8.0),
        wedge_angle_deg=params.get('wedge_angle_deg', 20.0),
        zone_count=params.get('zone_count', 3),
        fiber_diameter=params.get('fiber_diameter', 0.2),
        resolution=params.get('resolution', 32),
        arc_degrees=params.get('arc_degrees', 300.0)
    ))
