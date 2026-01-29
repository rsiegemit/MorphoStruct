"""
Hepatic lobule scaffold generator.

Creates hexagonal prism structures mimicking liver lobule architecture with:
- Hexagonal unit cells in honeycomb arrangement
- Portal triads at corners (portal vein, hepatic artery)
- Central vein through the center
- Optional sinusoidal channels connecting periphery to center
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class HepaticLobuleParams:
    """Parameters for hepatic lobule scaffold generation."""
    num_lobules: int = 1
    lobule_radius: float = 1.0  # mm (reduced from 1.5)
    lobule_height: float = 2.0  # mm (reduced from 3.0)
    wall_thickness: float = 0.1  # mm
    central_vein_radius: float = 0.15  # mm
    portal_vein_radius: float = 0.12  # mm
    show_sinusoids: bool = False
    sinusoid_radius: float = 0.025  # mm
    resolution: int = 6  # reduced from 8


def generate_honeycomb_centers(num_lobules: int, radius: float) -> list[tuple[float, float]]:
    """
    Generate center positions for hexagons in a honeycomb pattern.

    Args:
        num_lobules: Number of lobules to generate
        radius: Radius of each hexagonal lobule

    Returns:
        List of (x, y) center positions
    """
    if num_lobules <= 0:
        return []
    if num_lobules == 1:
        return [(0.0, 0.0)]

    hex_spacing = radius * np.sqrt(3)
    centers = [(0.0, 0.0)]
    added = {(0, 0)}
    axial_dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

    queue = [(0, 0)]
    while len(centers) < num_lobules and queue:
        q, r = queue.pop(0)
        for dq, dr in axial_dirs:
            nq, nr = q + dq, r + dr
            if (nq, nr) not in added and len(centers) < num_lobules:
                added.add((nq, nr))
                x = hex_spacing * (nq + nr * 0.5)
                y = hex_spacing * nr * (np.sqrt(3) / 2)
                centers.append((x, y))
                queue.append((nq, nr))

    return centers[:num_lobules]


def create_hexagon_prism(radius: float, height: float, wall_thickness: float, resolution: int = 32) -> m3d.Manifold:
    """
    Create a hexagonal prism (hollow) using manifold3d.

    Args:
        radius: Outer radius of hexagon
        height: Height of prism
        wall_thickness: Thickness of walls
        resolution: Number of segments (6 for hexagon)

    Returns:
        Hollow hexagonal prism manifold
    """
    outer = m3d.Manifold.cylinder(height, radius, radius, 6)
    inner_radius = radius - wall_thickness
    inner = m3d.Manifold.cylinder(height + 0.02, inner_radius, inner_radius, 6)
    inner = inner.translate([0, 0, -0.01])
    return outer - inner


def create_vertical_tube(x: float, y: float, height: float, radius: float, resolution: int = 16) -> m3d.Manifold:
    """
    Create a vertical cylindrical tube at position (x, y).

    Args:
        x, y: Position of tube center
        height: Height of tube
        radius: Radius of tube
        resolution: Number of segments around cylinder

    Returns:
        Vertical tube manifold
    """
    tube = m3d.Manifold.cylinder(height, radius, radius, resolution)
    return tube.translate([x, y, 0])


def get_hexagon_corners(center_x: float, center_y: float, radius: float) -> list[tuple[float, float]]:
    """
    Get the 6 corner positions of a hexagon at given center.

    Args:
        center_x, center_y: Center position
        radius: Radius to corners

    Returns:
        List of 6 (x, y) corner positions
    """
    rotation_offset = np.radians(30)
    angles = np.linspace(0, 2 * np.pi, 7)[:-1] + rotation_offset
    return [(center_x + radius * np.cos(a), center_y + radius * np.sin(a)) for a in angles]


def create_sinusoid(start_pos: tuple[float, float, float], end_pos: tuple[float, float, float],
                    radius: float, resolution: int = 8) -> m3d.Manifold | None:
    """
    Create a sinusoid channel between two points.

    Args:
        start_pos: (x, y, z) start position
        end_pos: (x, y, z) end position
        radius: Channel radius
        resolution: Number of segments around cylinder

    Returns:
        Cylindrical channel manifold or None if too short
    """
    x1, y1, z1 = start_pos
    x2, y2, z2 = end_pos

    dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
    length = np.sqrt(dx*dx + dy*dy + dz*dz)

    if length < 0.01:
        return None

    cyl = m3d.Manifold.cylinder(length, radius, radius, resolution)

    h = np.sqrt(dx*dx + dy*dy)
    if h > 0.001 or abs(dz) > 0.001:
        tilt = np.arctan2(h, dz) * 180 / np.pi
        azim = np.arctan2(dy, dx) * 180 / np.pi
        cyl = cyl.rotate([0, tilt, 0]).rotate([0, 0, azim])

    return cyl.translate([x1, y1, z1])


def generate_hepatic_lobule(params: HepaticLobuleParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a hepatic lobule scaffold.

    Args:
        params: HepaticLobuleParams specifying geometry

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, num_lobules, scaffold_type

    Raises:
        ValueError: If no geometry is generated
    """
    radius = params.lobule_radius
    height = params.lobule_height
    wall_thickness = params.wall_thickness
    resolution = params.resolution

    # Generate lobule centers
    centers = generate_honeycomb_centers(params.num_lobules, radius)

    # Create hexagonal prisms for each lobule
    scaffolds = []
    for cx, cy in centers:
        hex_prism = create_hexagon_prism(radius, height, wall_thickness, resolution)
        # Rotate 30 degrees to match typical hexagon orientation
        hex_prism = hex_prism.rotate([0, 0, 30])
        scaffolds.append(hex_prism.translate([cx, cy, 0]))

    # Create central veins
    central_veins = []
    for cx, cy in centers:
        cv = create_vertical_tube(cx, cy, height, params.central_vein_radius, resolution)
        central_veins.append(cv)

    # Create portal triads at corners
    portal_triads = []
    for cx, cy in centers:
        corners = get_hexagon_corners(cx, cy, radius)
        for corner_x, corner_y in corners:
            # Portal vein (larger)
            pv = create_vertical_tube(corner_x, corner_y, height, params.portal_vein_radius, resolution)
            portal_triads.append(pv)

    # Optional sinusoids
    sinusoids = []
    if params.show_sinusoids:
        for cx, cy in centers:
            corners = get_hexagon_corners(cx, cy, radius)
            # Create radial channels from each corner to center
            for corner_x, corner_y in corners:
                # Multiple levels along height
                for level in [0.25, 0.5, 0.75]:
                    z = height * level
                    start = (corner_x, corner_y, z)
                    end = (cx, cy, z)
                    sin_channel = create_sinusoid(start, end, params.sinusoid_radius, resolution)
                    if sin_channel:
                        sinusoids.append(sin_channel)

    # Combine all components
    all_parts = scaffolds + central_veins + portal_triads + sinusoids

    if not all_parts:
        raise ValueError("No geometry generated")

    result = batch_union(all_parts)

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'num_lobules': params.num_lobules,
        'scaffold_type': 'hepatic_lobule'
    }

    return result, stats


def generate_hepatic_lobule_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate hepatic lobule from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching HepaticLobuleParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_hepatic_lobule(HepaticLobuleParams(
        num_lobules=params.get('num_lobules', 1),
        lobule_radius=params.get('lobule_radius', 1.0),
        lobule_height=params.get('lobule_height', 2.0),
        wall_thickness=params.get('wall_thickness', 0.1),
        central_vein_radius=params.get('central_vein_radius', 0.15),
        portal_vein_radius=params.get('portal_vein_radius', 0.12),
        show_sinusoids=params.get('show_sinusoids', False),
        sinusoid_radius=params.get('sinusoid_radius', 0.025),
        resolution=params.get('resolution', 6)
    ))
