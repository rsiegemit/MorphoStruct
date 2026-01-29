"""
Trabecular bone scaffold generator with interconnected porous network.

Mimics cancellous bone structure with random interconnected struts forming
a network of pores typical of trabecular bone tissue.
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class TrabecularBoneParams:
    """Parameters for trabecular bone scaffold generation."""
    porosity: float = 0.75
    pore_size_um: float = 600.0
    strut_thickness_um: float = 200.0
    anisotropy_ratio: float = 1.5
    bounding_box: tuple[float, float, float] = (5.0, 5.0, 5.0)
    resolution: int = 6
    seed: int = 42


def generate_trabecular_bone(params: TrabecularBoneParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a trabecular bone scaffold with interconnected porous network.

    Uses a randomized Voronoi-like approach to create irregular interconnected
    struts mimicking cancellous bone microarchitecture.

    Args:
        params: TrabecularBoneParams specifying geometry and structure

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, porosity,
                     strut_count, scaffold_type

    Raises:
        ValueError: If no struts are generated
    """
    np.random.seed(params.seed)

    bx, by, bz = params.bounding_box
    pore_size_mm = params.pore_size_um / 1000.0
    strut_radius_mm = params.strut_thickness_um / 2000.0

    # Calculate lattice spacing based on pore size
    spacing = pore_size_mm

    # Generate nodes in a perturbed grid
    nx = max(2, int(bx / spacing) + 1)
    ny = max(2, int(by / spacing) + 1)
    nz = max(2, int(bz / spacing) + 1)

    nodes = []
    node_indices = {}

    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                # Base position
                x = i * spacing
                y = j * spacing
                z = k * spacing

                # Add random perturbation (30% of spacing)
                if 0 < i < nx-1:
                    x += (np.random.random() - 0.5) * spacing * 0.3
                if 0 < j < ny-1:
                    y += (np.random.random() - 0.5) * spacing * 0.3
                if 0 < k < nz-1:
                    z += (np.random.random() - 0.5) * spacing * 0.3

                # Apply anisotropy (stronger in Z direction)
                z *= params.anisotropy_ratio

                nodes.append(np.array([x, y, z]))
                node_indices[(i, j, k)] = len(nodes) - 1

    # Create struts connecting neighboring nodes
    # Use stochastic connectivity based on porosity
    strut_manifolds = []
    strut_count = 0
    connection_probability = 1.0 - (params.porosity * 0.8)  # Higher porosity = fewer connections

    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                idx = node_indices[(i, j, k)]
                p1 = nodes[idx]

                # Connect to neighbors (6-connectivity)
                for di, dj, dk in [(1,0,0), (0,1,0), (0,0,1)]:
                    ni, nj, nk = i + di, j + dj, k + dk
                    if ni < nx and nj < ny and nk < nz:
                        if np.random.random() < connection_probability:
                            neighbor_idx = node_indices[(ni, nj, nk)]
                            p2 = nodes[neighbor_idx]

                            strut = make_strut(p1, p2, strut_radius_mm, params.resolution)
                            if strut.num_vert() > 0:
                                strut_manifolds.append(strut)
                                strut_count += 1

    if not strut_manifolds:
        raise ValueError("No struts generated")

    # Union all struts
    result = batch_union(strut_manifolds)

    # Clip to original bounding box
    clip_box = m3d.Manifold.cube([bx, by, bz * params.anisotropy_ratio])
    result = result ^ clip_box

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0
    solid_volume = bx * by * bz * params.anisotropy_ratio
    actual_porosity = 1.0 - (volume / solid_volume) if solid_volume > 0 else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'porosity': actual_porosity,
        'strut_count': strut_count,
        'node_count': len(nodes),
        'scaffold_type': 'trabecular_bone'
    }

    return result, stats


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


def generate_trabecular_bone_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate trabecular bone from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching TrabecularBoneParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    bbox = params.get('bounding_box', (10, 10, 10))
    if isinstance(bbox, dict):
        bbox = (bbox['x'], bbox['y'], bbox['z'])

    return generate_trabecular_bone(TrabecularBoneParams(
        porosity=params.get('porosity', 0.75),
        pore_size_um=params.get('pore_size_um', 600.0),
        strut_thickness_um=params.get('strut_thickness_um', 200.0),
        anisotropy_ratio=params.get('anisotropy_ratio', 1.5),
        bounding_box=tuple(bbox),
        resolution=params.get('resolution', 6),
        seed=params.get('seed', 42)
    ))
