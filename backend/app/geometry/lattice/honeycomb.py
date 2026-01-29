"""
Honeycomb lattice scaffold generator.

Creates hexagonal honeycomb structures optimized for load-bearing applications.
The honeycomb pattern provides excellent strength-to-weight ratio and is
commonly used in structural applications.

Properties:
- High in-plane stiffness and strength
- Efficient material usage
- Uniform pore distribution
- Good for directional loading (perpendicular to honeycomb plane)
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass

try:
    import manifold3d as m3d
    HAS_MANIFOLD = True
except ImportError:
    m3d = None
    HAS_MANIFOLD = False

from ..core import batch_union


@dataclass
class HoneycombParams:
    """
    Parameters for honeycomb lattice scaffold generation.

    Attributes:
        bounding_box_mm: Scaffold dimensions (x, y, z) in millimeters
        cell_size_mm: Hexagon cell size (flat-to-flat distance) in mm (1-5mm typical)
        wall_thickness_mm: Wall thickness in millimeters (0.2-1mm typical)
        height_mm: Extrusion height in millimeters (if None, uses bounding_box z)
        resolution: Segments per hexagon side for smoothness (1 = sharp edges)
    """
    bounding_box_mm: tuple[float, float, float] = (6.0, 6.0, 3.0)
    cell_size_mm: float = 2.5
    wall_thickness_mm: float = 0.3
    height_mm: float | None = None
    resolution: int = 1


def create_hexagon_prism(
    center: tuple[float, float],
    radius: float,
    height: float,
    wall_thickness: float
) -> m3d.Manifold:
    """
    Create a hollow hexagonal prism (one honeycomb cell wall).

    The hexagon is created as outer - inner to form walls.

    Args:
        center: (x, y) center of hexagon
        radius: Circumradius (center to vertex)
        height: Extrusion height
        wall_thickness: Wall thickness

    Returns:
        Manifold representing the hollow hexagon prism
    """
    cx, cy = center

    # Create outer hexagon profile using cross-section and extrusion
    # Hexagon vertices at angles 0, 60, 120, 180, 240, 300 degrees
    angles = np.linspace(0, 2 * np.pi, 7)[:-1]  # 6 vertices

    # Outer hexagon vertices
    outer_verts = []
    for angle in angles:
        x = cx + radius * np.cos(angle)
        y = cy + radius * np.sin(angle)
        outer_verts.append([x, y])

    # Inner hexagon vertices (smaller radius for wall thickness)
    inner_radius = radius - wall_thickness / np.cos(np.pi / 6)  # Adjust for flat-to-flat
    if inner_radius <= 0:
        # Wall thickness too large, return solid hexagon
        inner_radius = radius * 0.1

    inner_verts = []
    for angle in angles:
        x = cx + inner_radius * np.cos(angle)
        y = cy + inner_radius * np.sin(angle)
        inner_verts.append([x, y])

    # Create outer prism
    outer_cross_section = m3d.CrossSection([outer_verts])
    outer_prism = m3d.Manifold.extrude(outer_cross_section, height)

    # Create inner prism (to subtract)
    inner_cross_section = m3d.CrossSection([inner_verts])
    inner_prism = m3d.Manifold.extrude(inner_cross_section, height + 0.1)
    inner_prism = inner_prism.translate([0, 0, -0.05])

    # Hollow hexagon = outer - inner
    return outer_prism - inner_prism


def create_hexagon_wall_segment(
    p1: tuple[float, float],
    p2: tuple[float, float],
    height: float,
    thickness: float
) -> m3d.Manifold:
    """
    Create a wall segment between two points.

    Args:
        p1: Start point (x, y)
        p2: End point (x, y)
        height: Wall height
        thickness: Wall thickness

    Returns:
        Manifold representing the wall segment
    """
    x1, y1 = p1
    x2, y2 = p2

    # Calculate wall direction and normal
    dx = x2 - x1
    dy = y2 - y1
    length = np.sqrt(dx*dx + dy*dy)

    if length < 1e-6:
        return m3d.Manifold()

    # Normal vector (perpendicular to wall)
    nx = -dy / length
    ny = dx / length

    # Half thickness offset
    ht = thickness / 2

    # Wall corners (rectangle)
    corners = [
        [x1 - nx * ht, y1 - ny * ht],
        [x2 - nx * ht, y2 - ny * ht],
        [x2 + nx * ht, y2 + ny * ht],
        [x1 + nx * ht, y1 + ny * ht],
    ]

    cross_section = m3d.CrossSection([corners])
    return m3d.Manifold.extrude(cross_section, height)


def generate_honeycomb_walls(
    bbox: tuple[float, float, float],
    cell_size: float,
    wall_thickness: float,
    height: float
) -> list[m3d.Manifold]:
    """
    Generate all wall segments for a honeycomb lattice.

    Uses flat-top hexagon orientation where cell_size is the flat-to-flat distance.

    Args:
        bbox: Bounding box (x, y, z)
        cell_size: Flat-to-flat hexagon size
        wall_thickness: Wall thickness
        height: Extrusion height

    Returns:
        List of wall manifolds
    """
    bx, by, bz = bbox

    # Hexagon geometry (flat-top orientation)
    # cell_size = flat-to-flat distance = 2 * apothem
    apothem = cell_size / 2  # Distance from center to flat edge
    circumradius = apothem / np.cos(np.pi / 6)  # Distance from center to vertex

    # Spacing between hex centers
    # Horizontal spacing (x direction): 1.5 * circumradius (because hexagons share edges)
    # Vertical spacing (y direction): cell_size (flat-to-flat)
    h_spacing = 1.5 * circumradius
    v_spacing = cell_size

    # Track unique wall segments to avoid duplicates
    wall_segments = set()

    # Generate hexagon centers in a grid pattern
    # Offset every other row for proper tessellation
    ny = int(by / v_spacing) + 2
    nx = int(bx / h_spacing) + 2

    for row in range(ny + 1):
        y_offset = row * v_spacing
        x_offset = (circumradius * 0.75) if (row % 2) else 0

        for col in range(nx + 1):
            cx = col * h_spacing + x_offset
            cy = y_offset

            # Skip if center is too far outside bounds
            if cx > bx + cell_size or cy > by + cell_size:
                continue
            if cx < -cell_size or cy < -cell_size:
                continue

            # Generate 6 vertices of this hexagon
            angles = np.linspace(0, 2 * np.pi, 7)[:-1]
            vertices = []
            for angle in angles:
                vx = cx + circumradius * np.cos(angle)
                vy = cy + circumradius * np.sin(angle)
                vertices.append((round(vx, 4), round(vy, 4)))

            # Add wall segments (edges of hexagon)
            for i in range(6):
                p1 = vertices[i]
                p2 = vertices[(i + 1) % 6]
                # Normalize segment direction for deduplication
                segment = tuple(sorted([p1, p2]))
                wall_segments.add(segment)

    # Create wall manifolds
    walls = []
    for (p1, p2) in wall_segments:
        # Only create walls that are at least partially within bounds
        if (max(p1[0], p2[0]) < 0 or min(p1[0], p2[0]) > bx or
            max(p1[1], p2[1]) < 0 or min(p1[1], p2[1]) > by):
            continue

        wall = create_hexagon_wall_segment(p1, p2, height, wall_thickness)
        if wall.num_vert() > 0:
            walls.append(wall)

    return walls


def generate_honeycomb(params: HoneycombParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a honeycomb lattice scaffold.

    Creates a hexagonal honeycomb pattern extruded to the specified height.
    The walls form a continuous interconnected structure ideal for
    load-bearing applications.

    Args:
        params: HoneycombParams configuration object

    Returns:
        Tuple of (manifold, statistics_dict)

        Statistics include:
            - triangle_count: Number of triangles in mesh
            - volume_mm3: Scaffold volume
            - relative_density: Volume fraction
            - wall_count: Number of wall segments
            - scaffold_type: 'honeycomb'

    Raises:
        ImportError: If manifold3d is not installed
        ValueError: If no walls are generated
    """
    if not HAS_MANIFOLD:
        raise ImportError(
            "manifold3d is required for geometry operations. "
            "Install with: pip install manifold3d"
        )

    bx, by, bz = params.bounding_box_mm
    height = params.height_mm if params.height_mm is not None else bz

    # Generate all wall segments
    walls = generate_honeycomb_walls(
        params.bounding_box_mm,
        params.cell_size_mm,
        params.wall_thickness_mm,
        height
    )

    if not walls:
        raise ValueError("No honeycomb walls generated")

    # Union all walls
    result = batch_union(walls)

    # Clip to bounding box
    clip_box = m3d.Manifold.cube([bx, by, height])
    result = result ^ clip_box

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0
    solid_volume = bx * by * height
    relative_density = volume / solid_volume if solid_volume > 0 else 0

    # Estimate cell count (approximate)
    apothem = params.cell_size_mm / 2
    circumradius = apothem / np.cos(np.pi / 6)
    cells_x = int(bx / (1.5 * circumradius))
    cells_y = int(by / params.cell_size_mm)

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'relative_density': relative_density,
        'wall_count': len(walls),
        'estimated_cell_count': cells_x * cells_y,
        'scaffold_type': 'honeycomb'
    }

    return result, stats


def generate_honeycomb_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate honeycomb scaffold from dictionary parameters.

    Args:
        params: Dictionary with keys matching HoneycombParams fields

    Returns:
        Tuple of (manifold, statistics_dict)
    """
    bbox = params.get('bounding_box_mm', params.get('bounding_box', (6, 6, 3)))
    if isinstance(bbox, dict):
        bbox = (bbox['x'], bbox['y'], bbox['z'])

    return generate_honeycomb(HoneycombParams(
        bounding_box_mm=tuple(bbox),
        cell_size_mm=params.get('cell_size_mm', 2.5),
        wall_thickness_mm=params.get('wall_thickness_mm', 0.3),
        height_mm=params.get('height_mm', None),
        resolution=params.get('resolution', 1)
    ))
