"""
Lattice scaffold generator for cubic and BCC (body-centered cubic) structures.

Provides parametric generation of lattice-based scaffolds with:
- Cubic unit cells (12 edge struts per cell)
- BCC unit cells (12 edge struts + 8 diagonal struts per cell)
- Configurable cell size, strut diameter, and resolution
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from typing import Literal
from ..core import batch_union


@dataclass
class LatticeParams:
    """Parameters for lattice scaffold generation."""
    bounding_box_mm: tuple[float, float, float] = (10.0, 10.0, 10.0)
    unit_cell: Literal['cubic', 'bcc'] = 'cubic'
    cell_size_mm: float = 2.0
    strut_diameter_mm: float = 0.4
    resolution: int = 8


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

    # Create cylinder along Z axis (from z=0 to z=length)
    strut = m3d.Manifold.cylinder(length, radius, radius, resolution)

    # Calculate rotation angles to align with direction vector (p1 -> p2)
    # Similar approach to vascular.py make_cyl
    h = np.sqrt(dx*dx + dy*dy)  # horizontal distance
    if h > 0.001 or abs(dz) > 0.001:
        # Rotate to align with direction vector
        # First rotate around Y to tilt from vertical
        angle_y = np.arctan2(h, dz) * 180 / np.pi
        # Then rotate around Z to point in correct horizontal direction
        angle_z = np.arctan2(dy, dx) * 180 / np.pi

        strut = strut.rotate([0, angle_y, 0])
        strut = strut.rotate([0, 0, angle_z])

    # Translate to starting position
    return strut.translate([p1[0], p1[1], p1[2]])


def get_cubic_struts(cell_origin: np.ndarray, cell_size: float) -> list[tuple[np.ndarray, np.ndarray]]:
    """
    Get strut endpoints for a cubic unit cell.

    A cubic cell has 8 corner nodes connected by 12 edge struts:
    - 4 struts along X direction
    - 4 struts along Y direction
    - 4 struts along Z direction

    Args:
        cell_origin: Origin point (x, y, z) of the unit cell
        cell_size: Size of the unit cell

    Returns:
        List of (p1, p2) tuples defining strut endpoints
    """
    # 8 corners of the cube
    corners = []
    for i in [0, 1]:
        for j in [0, 1]:
            for k in [0, 1]:
                corners.append(cell_origin + np.array([i, j, k]) * cell_size)

    # 12 edges connecting adjacent corners
    struts = []

    # X-direction edges (4 struts)
    for j in [0, 1]:
        for k in [0, 1]:
            p1 = cell_origin + np.array([0, j, k]) * cell_size
            p2 = cell_origin + np.array([1, j, k]) * cell_size
            struts.append((p1, p2))

    # Y-direction edges (4 struts)
    for i in [0, 1]:
        for k in [0, 1]:
            p1 = cell_origin + np.array([i, 0, k]) * cell_size
            p2 = cell_origin + np.array([i, 1, k]) * cell_size
            struts.append((p1, p2))

    # Z-direction edges (4 struts)
    for i in [0, 1]:
        for j in [0, 1]:
            p1 = cell_origin + np.array([i, j, 0]) * cell_size
            p2 = cell_origin + np.array([i, j, 1]) * cell_size
            struts.append((p1, p2))

    return struts


def get_bcc_struts(cell_origin: np.ndarray, cell_size: float) -> list[tuple[np.ndarray, np.ndarray]]:
    """
    Get strut endpoints for BCC (body-centered cubic) unit cell.

    A BCC cell has all cubic struts plus a center node connected by 8 diagonal struts
    to the corner nodes.

    Args:
        cell_origin: Origin point (x, y, z) of the unit cell
        cell_size: Size of the unit cell

    Returns:
        List of (p1, p2) tuples defining strut endpoints (12 edges + 8 diagonals = 20 struts)
    """
    # Start with cubic edge struts
    struts = get_cubic_struts(cell_origin, cell_size)

    # Add center node and diagonal connections to corners
    center = cell_origin + np.array([0.5, 0.5, 0.5]) * cell_size

    for i in [0, 1]:
        for j in [0, 1]:
            for k in [0, 1]:
                corner = cell_origin + np.array([i, j, k]) * cell_size
                struts.append((center, corner))

    return struts


def generate_lattice(params: LatticeParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a lattice scaffold.

    Args:
        params: LatticeParams specifying geometry and structure

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, relative_density,
                     cell_count, strut_count, scaffold_type

    Raises:
        ValueError: If no struts are generated
    """
    bx, by, bz = params.bounding_box_mm
    cell = params.cell_size_mm
    radius = params.strut_diameter_mm / 2

    # Calculate number of cells in each dimension
    nx = max(1, int(bx / cell))
    ny = max(1, int(by / cell))
    nz = max(1, int(bz / cell))

    # Get strut function based on unit cell type
    get_struts = get_bcc_struts if params.unit_cell == 'bcc' else get_cubic_struts

    # Collect all unique struts (avoid duplicates at cell boundaries)
    all_strut_endpoints = set()

    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                origin = np.array([i, j, k], dtype=float) * cell
                struts = get_struts(origin, cell)
                for p1, p2 in struts:
                    # Normalize order for deduplication (smaller tuple first)
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

    # Union all struts
    if not strut_manifolds:
        raise ValueError("No struts generated")

    result = batch_union(strut_manifolds)

    # Clip to bounding box
    clip_box = m3d.Manifold.cube([bx, by, bz])
    result = result ^ clip_box  # Intersection operator

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
        'scaffold_type': 'lattice'
    }

    return result, stats


def generate_lattice_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate lattice from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching LatticeParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    # Handle bounding box variations
    bbox = params.get('bounding_box_mm', params.get('bounding_box', (10, 10, 10)))
    if isinstance(bbox, dict):
        bbox = (bbox['x'], bbox['y'], bbox['z'])

    return generate_lattice(LatticeParams(
        bounding_box_mm=tuple(bbox),
        unit_cell=params.get('unit_cell', 'cubic'),
        cell_size_mm=params.get('cell_size_mm', 2.0),
        strut_diameter_mm=params.get('strut_diameter_mm', 0.4),
        resolution=params.get('resolution', 8)
    ))
