"""
Voronoi lattice scaffold generator.

Creates organic, randomized cellular structures based on Voronoi tessellation.
The structure mimics natural trabecular bone architecture.

Properties:
- Randomized but controllable structure (via seed)
- Interconnected pore network
- Biomimetic appearance similar to cancellous bone
- Tunable cell density and strut thickness
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

try:
    from scipy.spatial import Voronoi
    HAS_SCIPY = True
except ImportError:
    Voronoi = None
    HAS_SCIPY = False

from ..core import batch_union


@dataclass
class VoronoiParams:
    """
    Parameters for Voronoi lattice scaffold generation.

    Attributes:
        bounding_box_mm: Scaffold dimensions (x, y, z) in millimeters
        cell_count: Number of Voronoi seed points (10-100 typical)
        strut_diameter_mm: Strut diameter in millimeters (0.2-0.8mm typical)
        seed: Random seed for reproducibility (None for random)
        resolution: Number of segments for cylindrical struts (6-12)
        margin_factor: Margin around bbox for seed points (0.1-0.5)
    """
    bounding_box_mm: tuple[float, float, float] = (6.0, 6.0, 6.0)
    cell_count: int = 20
    strut_diameter_mm: float = 0.3
    seed: int | None = None
    resolution: int = 6
    margin_factor: float = 0.2


def make_strut(p1: np.ndarray, p2: np.ndarray, radius: float, resolution: int) -> m3d.Manifold:
    """
    Create a cylindrical strut between two points.

    Args:
        p1: Starting point (x, y, z)
        p2: Ending point (x, y, z)
        radius: Strut radius
        resolution: Number of segments around cylinder

    Returns:
        Manifold representing the strut cylinder
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    length = np.sqrt(dx*dx + dy*dy + dz*dz)

    if length < 1e-6:
        return m3d.Manifold()

    strut = m3d.Manifold.cylinder(length, radius, radius, resolution)

    h = np.sqrt(dx*dx + dy*dy)
    if h > 0.001 or abs(dz) > 0.001:
        angle_y = np.arctan2(h, dz) * 180 / np.pi
        angle_z = np.arctan2(dy, dx) * 180 / np.pi
        strut = strut.rotate([0, angle_y, 0])
        strut = strut.rotate([0, 0, angle_z])

    return strut.translate([p1[0], p1[1], p1[2]])


def generate_seed_points(
    bbox: tuple[float, float, float],
    count: int,
    margin: float,
    rng: np.random.Generator
) -> np.ndarray:
    """
    Generate random seed points for Voronoi tessellation.

    Points are generated within the bounding box plus a margin to ensure
    good edge coverage. Mirror points are added outside to handle boundaries.

    Args:
        bbox: Bounding box dimensions (x, y, z)
        count: Number of interior seed points
        margin: Margin around bbox for extended seed region
        rng: Numpy random generator

    Returns:
        Array of seed points (N, 3)
    """
    bx, by, bz = bbox

    # Generate interior points
    interior = rng.uniform(
        low=[0, 0, 0],
        high=[bx, by, bz],
        size=(count, 3)
    )

    # Add mirror points outside each face for better boundary behavior
    # This prevents infinite Voronoi ridges at boundaries
    mirror_points = []

    for point in interior:
        # Mirror across each face if point is close to that face
        x, y, z = point
        threshold = max(bx, by, bz) * 0.3

        if x < threshold:
            mirror_points.append([-x, y, z])
        if x > bx - threshold:
            mirror_points.append([2*bx - x, y, z])
        if y < threshold:
            mirror_points.append([x, -y, z])
        if y > by - threshold:
            mirror_points.append([x, 2*by - y, z])
        if z < threshold:
            mirror_points.append([x, y, -z])
        if z > bz - threshold:
            mirror_points.append([x, y, 2*bz - z])

    if mirror_points:
        all_points = np.vstack([interior, np.array(mirror_points)])
    else:
        all_points = interior

    return all_points


def get_voronoi_edges(
    vor: Voronoi,
    bbox: tuple[float, float, float],
    margin: float = 0.1
) -> list[tuple[np.ndarray, np.ndarray]]:
    """
    Extract Voronoi edges that lie within or near the bounding box.

    Args:
        vor: Scipy Voronoi object
        bbox: Bounding box dimensions (x, y, z)
        margin: Margin for including edges near boundaries

    Returns:
        List of (p1, p2) tuples defining edge endpoints
    """
    bx, by, bz = bbox
    edges = []

    for ridge_vertices in vor.ridge_vertices:
        if -1 in ridge_vertices:
            # Ridge goes to infinity - skip
            continue

        v1 = vor.vertices[ridge_vertices[0]]
        v2 = vor.vertices[ridge_vertices[1]]

        # Check if edge is within bounds (with margin)
        margin_x = bx * margin
        margin_y = by * margin
        margin_z = bz * margin

        # Check if both points are reasonably within bounds
        in_bounds_1 = (
            -margin_x <= v1[0] <= bx + margin_x and
            -margin_y <= v1[1] <= by + margin_y and
            -margin_z <= v1[2] <= bz + margin_z
        )
        in_bounds_2 = (
            -margin_x <= v2[0] <= bx + margin_x and
            -margin_y <= v2[1] <= by + margin_y and
            -margin_z <= v2[2] <= bz + margin_z
        )

        if in_bounds_1 and in_bounds_2:
            # Clip points to bounding box
            p1 = np.clip(v1, [0, 0, 0], [bx, by, bz])
            p2 = np.clip(v2, [0, 0, 0], [bx, by, bz])

            # Only add if edge has meaningful length after clipping
            if np.linalg.norm(p2 - p1) > 0.1:
                edges.append((p1, p2))

    return edges


def generate_voronoi(params: VoronoiParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a Voronoi lattice scaffold.

    Algorithm:
    1. Generate random seed points (with reproducible seed)
    2. Compute 3D Voronoi tessellation
    3. Extract edges that lie within bounding box
    4. Create cylindrical struts along each edge
    5. Union all struts and clip to bounding box

    Args:
        params: VoronoiParams configuration object

    Returns:
        Tuple of (manifold, statistics_dict)

        Statistics include:
            - triangle_count: Number of triangles in mesh
            - volume_mm3: Scaffold volume
            - relative_density: Volume fraction
            - cell_count: Number of Voronoi cells
            - strut_count: Number of struts created
            - scaffold_type: 'voronoi'

    Raises:
        ImportError: If required libraries are not installed
        ValueError: If no struts are generated
    """
    if not HAS_MANIFOLD:
        raise ImportError(
            "manifold3d is required for geometry operations. "
            "Install with: pip install manifold3d"
        )
    if not HAS_SCIPY:
        raise ImportError(
            "scipy is required for Voronoi tessellation. "
            "Install with: pip install scipy"
        )

    bbox = params.bounding_box_mm
    bx, by, bz = bbox
    radius = params.strut_diameter_mm / 2

    # Initialize random generator
    rng = np.random.default_rng(params.seed)

    # Generate seed points with mirror boundary handling
    points = generate_seed_points(
        bbox,
        params.cell_count,
        params.margin_factor,
        rng
    )

    # Compute Voronoi tessellation
    vor = Voronoi(points)

    # Extract edges within bounding box
    edges = get_voronoi_edges(vor, bbox, margin=0.05)

    if not edges:
        raise ValueError("No Voronoi edges generated within bounding box")

    # Create strut manifolds
    strut_manifolds = []
    for p1, p2 in edges:
        strut = make_strut(p1, p2, radius, params.resolution)
        if strut.num_vert() > 0:
            strut_manifolds.append(strut)

    if not strut_manifolds:
        raise ValueError("No valid struts created for Voronoi lattice")

    # Union all struts
    result = batch_union(strut_manifolds)

    # Clip to bounding box
    clip_box = m3d.Manifold.cube([bx, by, bz])
    result = result ^ clip_box

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0
    solid_volume = bx * by * bz
    relative_density = volume / solid_volume if solid_volume > 0 else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'relative_density': relative_density,
        'cell_count': params.cell_count,
        'strut_count': len(edges),
        'seed': params.seed,
        'scaffold_type': 'voronoi'
    }

    return result, stats


def generate_voronoi_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate Voronoi scaffold from dictionary parameters.

    Args:
        params: Dictionary with keys matching VoronoiParams fields

    Returns:
        Tuple of (manifold, statistics_dict)
    """
    bbox = params.get('bounding_box_mm', params.get('bounding_box', (6, 6, 6)))
    if isinstance(bbox, dict):
        bbox = (bbox['x'], bbox['y'], bbox['z'])

    return generate_voronoi(VoronoiParams(
        bounding_box_mm=tuple(bbox),
        cell_count=params.get('cell_count', 20),
        strut_diameter_mm=params.get('strut_diameter_mm', 0.3),
        seed=params.get('seed', None),
        resolution=params.get('resolution', 6),
        margin_factor=params.get('margin_factor', 0.2)
    ))
