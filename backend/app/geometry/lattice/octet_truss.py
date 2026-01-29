"""
Octet truss lattice scaffold generator.

The octet truss is a stretch-dominated lattice with exceptional strength-to-weight
ratio. Each unit cell contains an octahedron surrounded by tetrahedra, creating
a highly efficient load-bearing structure.

Unit cell composition:
- 12 edge struts (cube edges)
- 24 face diagonal struts (6 faces x 4 diagonals each, but shared)
- 6 internal struts connecting face centers to body center

The structure is commonly used in aerospace and biomedical applications.
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
class OctetTrussParams:
    """
    Parameters for octet truss lattice generation.

    Attributes:
        bounding_box_mm: Scaffold dimensions (x, y, z) in millimeters
        cell_size_mm: Unit cell size in millimeters (1-5mm typical)
        strut_diameter_mm: Strut diameter in millimeters (0.2-1mm typical)
        resolution: Number of segments for cylindrical struts (6-16)
    """
    bounding_box_mm: tuple[float, float, float] = (6.0, 6.0, 6.0)
    cell_size_mm: float = 3.0
    strut_diameter_mm: float = 0.3
    resolution: int = 6


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

    # Create cylinder along Z axis
    strut = m3d.Manifold.cylinder(length, radius, radius, resolution)

    # Calculate rotation to align with direction vector
    h = np.sqrt(dx*dx + dy*dy)
    if h > 0.001 or abs(dz) > 0.001:
        angle_y = np.arctan2(h, dz) * 180 / np.pi
        angle_z = np.arctan2(dy, dx) * 180 / np.pi
        strut = strut.rotate([0, angle_y, 0])
        strut = strut.rotate([0, 0, angle_z])

    return strut.translate([p1[0], p1[1], p1[2]])


def get_octet_truss_struts(cell_origin: np.ndarray, cell_size: float) -> list[tuple[np.ndarray, np.ndarray]]:
    """
    Get strut endpoints for an octet truss unit cell.

    The octet truss consists of:
    - 12 edge struts (cube edges)
    - Face diagonals connecting face centers to corners
    - Internal octahedron struts

    This implementation uses the FCC (face-centered cubic) node arrangement:
    - 8 corner nodes
    - 6 face center nodes

    Args:
        cell_origin: Origin point (x, y, z) of the unit cell
        cell_size: Size of the unit cell

    Returns:
        List of (p1, p2) tuples defining strut endpoints
    """
    L = cell_size
    o = cell_origin

    # 8 corner nodes
    corners = []
    for i in [0, 1]:
        for j in [0, 1]:
            for k in [0, 1]:
                corners.append(o + np.array([i, j, k]) * L)

    # 6 face center nodes (FCC positions)
    face_centers = [
        o + np.array([0.5, 0.5, 0]) * L,    # bottom face
        o + np.array([0.5, 0.5, 1]) * L,    # top face
        o + np.array([0.5, 0, 0.5]) * L,    # front face
        o + np.array([0.5, 1, 0.5]) * L,    # back face
        o + np.array([0, 0.5, 0.5]) * L,    # left face
        o + np.array([1, 0.5, 0.5]) * L,    # right face
    ]

    struts = []

    # Edge struts (12 edges of the cube)
    # X-direction edges
    for j in [0, 1]:
        for k in [0, 1]:
            p1 = o + np.array([0, j, k]) * L
            p2 = o + np.array([1, j, k]) * L
            struts.append((p1, p2))

    # Y-direction edges
    for i in [0, 1]:
        for k in [0, 1]:
            p1 = o + np.array([i, 0, k]) * L
            p2 = o + np.array([i, 1, k]) * L
            struts.append((p1, p2))

    # Z-direction edges
    for i in [0, 1]:
        for j in [0, 1]:
            p1 = o + np.array([i, j, 0]) * L
            p2 = o + np.array([i, j, 1]) * L
            struts.append((p1, p2))

    # Face diagonal struts: connect each face center to its 4 corners
    # Bottom face (z=0)
    fc = o + np.array([0.5, 0.5, 0]) * L
    for i in [0, 1]:
        for j in [0, 1]:
            corner = o + np.array([i, j, 0]) * L
            struts.append((fc, corner))

    # Top face (z=1)
    fc = o + np.array([0.5, 0.5, 1]) * L
    for i in [0, 1]:
        for j in [0, 1]:
            corner = o + np.array([i, j, 1]) * L
            struts.append((fc, corner))

    # Front face (y=0)
    fc = o + np.array([0.5, 0, 0.5]) * L
    for i in [0, 1]:
        for k in [0, 1]:
            corner = o + np.array([i, 0, k]) * L
            struts.append((fc, corner))

    # Back face (y=1)
    fc = o + np.array([0.5, 1, 0.5]) * L
    for i in [0, 1]:
        for k in [0, 1]:
            corner = o + np.array([i, 1, k]) * L
            struts.append((fc, corner))

    # Left face (x=0)
    fc = o + np.array([0, 0.5, 0.5]) * L
    for j in [0, 1]:
        for k in [0, 1]:
            corner = o + np.array([0, j, k]) * L
            struts.append((fc, corner))

    # Right face (x=1)
    fc = o + np.array([1, 0.5, 0.5]) * L
    for j in [0, 1]:
        for k in [0, 1]:
            corner = o + np.array([1, j, k]) * L
            struts.append((fc, corner))

    # Internal octahedron struts: connect adjacent face centers
    # Each face center connects to 4 adjacent face centers
    # Bottom-to-sides
    struts.append((face_centers[0], face_centers[2]))  # bottom to front
    struts.append((face_centers[0], face_centers[3]))  # bottom to back
    struts.append((face_centers[0], face_centers[4]))  # bottom to left
    struts.append((face_centers[0], face_centers[5]))  # bottom to right

    # Top-to-sides
    struts.append((face_centers[1], face_centers[2]))  # top to front
    struts.append((face_centers[1], face_centers[3]))  # top to back
    struts.append((face_centers[1], face_centers[4]))  # top to left
    struts.append((face_centers[1], face_centers[5]))  # top to right

    # Horizontal ring (front-left-back-right-front)
    struts.append((face_centers[2], face_centers[4]))  # front to left
    struts.append((face_centers[4], face_centers[3]))  # left to back
    struts.append((face_centers[3], face_centers[5]))  # back to right
    struts.append((face_centers[5], face_centers[2]))  # right to front

    return struts


def generate_octet_truss(params: OctetTrussParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate an octet truss lattice scaffold.

    Args:
        params: OctetTrussParams configuration object

    Returns:
        Tuple of (manifold, statistics_dict)

        Statistics include:
            - triangle_count: Number of triangles in mesh
            - volume_mm3: Scaffold volume
            - relative_density: Volume fraction (solid/total)
            - cell_count: Number of unit cells
            - strut_count: Number of unique struts
            - scaffold_type: 'octet_truss'

    Raises:
        ImportError: If manifold3d is not installed
        ValueError: If no struts are generated
    """
    if not HAS_MANIFOLD:
        raise ImportError(
            "manifold3d is required for geometry operations. "
            "Install with: pip install manifold3d"
        )

    bx, by, bz = params.bounding_box_mm
    cell = params.cell_size_mm
    radius = params.strut_diameter_mm / 2

    # Calculate number of cells
    nx = max(1, int(bx / cell))
    ny = max(1, int(by / cell))
    nz = max(1, int(bz / cell))

    # Collect unique struts across all cells
    all_strut_endpoints = set()

    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                origin = np.array([i, j, k], dtype=float) * cell
                struts = get_octet_truss_struts(origin, cell)
                for p1, p2 in struts:
                    key = tuple(sorted([tuple(p1.round(6)), tuple(p2.round(6))]))
                    all_strut_endpoints.add(key)

    # Create strut manifolds
    strut_manifolds = []
    for (p1_tuple, p2_tuple) in all_strut_endpoints:
        p1 = np.array(p1_tuple)
        p2 = np.array(p2_tuple)
        strut = make_strut(p1, p2, radius, params.resolution)
        if strut.num_vert() > 0:
            strut_manifolds.append(strut)

    if not strut_manifolds:
        raise ValueError("No struts generated for octet truss")

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
        'cell_count': nx * ny * nz,
        'strut_count': len(all_strut_endpoints),
        'scaffold_type': 'octet_truss'
    }

    return result, stats


def generate_octet_truss_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate octet truss scaffold from dictionary parameters.

    Args:
        params: Dictionary with keys matching OctetTrussParams fields

    Returns:
        Tuple of (manifold, statistics_dict)
    """
    bbox = params.get('bounding_box_mm', params.get('bounding_box', (6, 6, 6)))
    if isinstance(bbox, dict):
        bbox = (bbox['x'], bbox['y'], bbox['z'])

    return generate_octet_truss(OctetTrussParams(
        bounding_box_mm=tuple(bbox),
        cell_size_mm=params.get('cell_size_mm', 3.0),
        strut_diameter_mm=params.get('strut_diameter_mm', 0.3),
        resolution=params.get('resolution', 6)
    ))
