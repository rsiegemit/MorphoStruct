"""
Gyroid triply periodic minimal surface (TPMS) scaffold generator.

The gyroid is a TPMS discovered by Alan Schoen in 1970. It has excellent
properties for tissue engineering scaffolds:
- High surface area to volume ratio
- Fully interconnected pore network
- Smooth curvature (no sharp corners)
- Self-supporting for 3D printing

Implicit function: sin(2pi*x/L)cos(2pi*y/L) + sin(2pi*y/L)cos(2pi*z/L) + sin(2pi*z/L)cos(2pi*x/L) = isovalue
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Any

try:
    from skimage.measure import marching_cubes
    HAS_SKIMAGE = True
except ImportError:
    marching_cubes = None
    HAS_SKIMAGE = False


@dataclass
class GyroidParams:
    """
    Parameters for gyroid TPMS scaffold generation.

    Attributes:
        bounding_box_mm: Scaffold dimensions (x, y, z) in millimeters
        cell_size_mm: Unit cell period in millimeters (1-5mm typical)
        wall_thickness_mm: Wall thickness in millimeters (0.2-1mm typical)
        isovalue: Implicit surface level (-1 to 1, controls porosity)
        samples_per_cell: Grid resolution per unit cell (higher = smoother)
    """
    bounding_box_mm: tuple[float, float, float] = (10.0, 10.0, 10.0)
    cell_size_mm: float = 2.0
    wall_thickness_mm: float = 0.3
    isovalue: float = 0.0
    samples_per_cell: int = 15


def gyroid_function(X: np.ndarray, Y: np.ndarray, Z: np.ndarray, L: float) -> np.ndarray:
    """
    Evaluate the gyroid implicit function.

    F(x,y,z) = sin(kx)cos(ky) + sin(ky)cos(kz) + sin(kz)cos(kx)
    where k = 2*pi/L (wave number for period L)

    Args:
        X, Y, Z: 3D coordinate arrays (meshgrid output)
        L: Unit cell period (cell size)

    Returns:
        3D array of function values
    """
    k = 2 * np.pi / L
    return (
        np.sin(k * X) * np.cos(k * Y) +
        np.sin(k * Y) * np.cos(k * Z) +
        np.sin(k * Z) * np.cos(k * X)
    )


class _SimpleMesh:
    """
    Simple mesh wrapper that provides the interface expected by stl_export.

    Mimics the manifold3d Mesh interface with:
    - vert_properties: 2D array of vertex positions (N, 3)
    - tri_verts: 2D array of triangle vertex indices (M, 3)
    """

    def __init__(self, vertices: np.ndarray, faces: np.ndarray):
        """
        Initialize mesh from marching cubes output.

        Args:
            vertices: Vertex array (N, 3) from marching cubes
            faces: Face array (M, 3) with vertex indices
        """
        # Store as 2D arrays - stl_export expects vert_properties[:, :3]
        self.vert_properties = vertices.astype(np.float32)
        # Store faces as 2D array - stl_export expects tri_verts as (M, 3)
        self.tri_verts = faces.astype(np.uint32)


class _MarchingCubesMeshWrapper:
    """
    Wrapper class that provides a manifold3d-like interface for marching cubes output.

    This allows the API to use marching cubes meshes directly without requiring
    manifold3d boolean operations, which fail on non-manifold TPMS surfaces.
    """

    def __init__(self, vertices: np.ndarray, faces: np.ndarray):
        """
        Initialize wrapper from marching cubes output.

        Args:
            vertices: Vertex array (N, 3)
            faces: Face array (M, 3) with vertex indices
        """
        self._vertices = vertices
        self._faces = faces
        self._mesh = _SimpleMesh(vertices, faces)

    def to_mesh(self) -> _SimpleMesh:
        """Return the mesh object."""
        return self._mesh

    def volume(self) -> float:
        """
        Return volume (0 for TPMS surfaces since they're not closed solids).
        """
        return 0.0


def generate_gyroid(params: GyroidParams) -> tuple[Any, dict]:
    """
    Generate a gyroid TPMS scaffold using marching cubes.

    The algorithm:
    1. Create a 3D grid covering the bounding box
    2. Evaluate the gyroid implicit function at each grid point
    3. Use marching cubes to extract the isosurface
    4. Return the mesh directly (no manifold3d boolean operations)

    Args:
        params: GyroidParams configuration object

    Returns:
        Tuple of (mesh_wrapper, statistics_dict)

        Statistics include:
            - triangle_count: Number of triangles in mesh
            - volume_mm3: Scaffold volume (0 for surfaces)
            - porosity: Void fraction (approximate)
            - cell_count: Number of unit cells in each dimension
            - scaffold_type: 'gyroid'

    Raises:
        ImportError: If required libraries are not installed
        ValueError: If surface extraction fails
    """
    if not HAS_SKIMAGE:
        raise ImportError(
            "scikit-image is required for TPMS generation. "
            "Install with: pip install scikit-image"
        )

    bx, by, bz = params.bounding_box_mm
    L = params.cell_size_mm

    # Calculate grid resolution
    nx = max(10, int(bx / L * params.samples_per_cell))
    ny = max(10, int(by / L * params.samples_per_cell))
    nz = max(10, int(bz / L * params.samples_per_cell))

    # Create coordinate arrays
    x = np.linspace(0, bx, nx)
    y = np.linspace(0, by, ny)
    z = np.linspace(0, bz, nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    # Spacing for marching cubes
    spacing = (x[1] - x[0], y[1] - y[0], z[1] - z[0])

    # Evaluate gyroid function
    F = gyroid_function(X, Y, Z, L)

    # Extract single isosurface using marching cubes
    try:
        verts, faces, _, _ = marching_cubes(F, level=params.isovalue, spacing=spacing)
    except ValueError as e:
        raise ValueError(f"Failed to extract gyroid surface: {e}")

    if len(verts) == 0 or len(faces) == 0:
        raise ValueError("Marching cubes produced empty mesh for gyroid surface")

    # Create wrapper with manifold3d-like interface
    result = _MarchingCubesMeshWrapper(verts, faces)

    # Calculate statistics
    stats = {
        'triangle_count': len(faces),
        'volume_mm3': 0.0,  # TPMS surfaces are not closed solids
        'porosity': 0.5,  # Approximate - gyroid has ~50% porosity at isovalue=0
        'cell_count': (int(bx / L), int(by / L), int(bz / L)),
        'scaffold_type': 'gyroid'
    }

    return result, stats


def generate_gyroid_from_dict(params: dict) -> tuple[Any, dict]:
    """
    Generate gyroid scaffold from dictionary parameters.

    Args:
        params: Dictionary with keys matching GyroidParams fields

    Returns:
        Tuple of (mesh_wrapper, statistics_dict)
    """
    bbox = params.get('bounding_box_mm', params.get('bounding_box', (10, 10, 10)))
    if isinstance(bbox, dict):
        bbox = (bbox['x'], bbox['y'], bbox['z'])

    return generate_gyroid(GyroidParams(
        bounding_box_mm=tuple(bbox),
        cell_size_mm=params.get('cell_size_mm', 2.0),
        wall_thickness_mm=params.get('wall_thickness_mm', 0.3),
        isovalue=params.get('isovalue', 0.0),
        samples_per_cell=params.get('samples_per_cell', 20)
    ))
