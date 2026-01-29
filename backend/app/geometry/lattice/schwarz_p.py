"""
Schwarz P (Primitive) triply periodic minimal surface scaffold generator.

The Schwarz P surface is one of the simplest TPMS, discovered by Hermann Schwarz
in 1865. It has cubic symmetry with circular openings along each axis.

Properties:
- Simpler topology than gyroid
- Higher connectivity in orthogonal directions
- Good for applications requiring directional flow
- Self-supporting for 3D printing

Implicit function: cos(2pi*x/L) + cos(2pi*y/L) + cos(2pi*z/L) = isovalue
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
class SchwarzPParams:
    """
    Parameters for Schwarz P TPMS scaffold generation.

    Attributes:
        bounding_box_mm: Scaffold dimensions (x, y, z) in millimeters
        cell_size_mm: Unit cell period in millimeters (1-5mm typical)
        wall_thickness_mm: Wall thickness in millimeters (0.2-1mm typical)
        isovalue: Implicit surface level (-3 to 3, controls porosity)
        samples_per_cell: Grid resolution per unit cell (higher = smoother)
    """
    bounding_box_mm: tuple[float, float, float] = (10.0, 10.0, 10.0)
    cell_size_mm: float = 2.0
    wall_thickness_mm: float = 0.3
    isovalue: float = 0.0
    samples_per_cell: int = 15


def schwarz_p_function(X: np.ndarray, Y: np.ndarray, Z: np.ndarray, L: float) -> np.ndarray:
    """
    Evaluate the Schwarz P implicit function.

    F(x,y,z) = cos(kx) + cos(ky) + cos(kz)
    where k = 2*pi/L (wave number for period L)

    The function ranges from -3 to +3:
    - At corners of unit cell (0,0,0): cos(0)+cos(0)+cos(0) = 3
    - At center of unit cell (L/2,L/2,L/2): cos(pi)+cos(pi)+cos(pi) = -3

    Args:
        X, Y, Z: 3D coordinate arrays (meshgrid output)
        L: Unit cell period (cell size)

    Returns:
        3D array of function values
    """
    k = 2 * np.pi / L
    return np.cos(k * X) + np.cos(k * Y) + np.cos(k * Z)


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


def generate_schwarz_p(params: SchwarzPParams) -> tuple[Any, dict]:
    """
    Generate a Schwarz P TPMS scaffold using marching cubes.

    The algorithm:
    1. Create a 3D grid covering the bounding box
    2. Evaluate the Schwarz P implicit function at each grid point
    3. Use marching cubes to extract the isosurface
    4. Return the mesh directly (no manifold3d boolean operations)

    Args:
        params: SchwarzPParams configuration object

    Returns:
        Tuple of (mesh_wrapper, statistics_dict)

        Statistics include:
            - triangle_count: Number of triangles in mesh
            - volume_mm3: Scaffold volume (0 for surfaces)
            - porosity: Void fraction (approximate)
            - cell_count: Number of unit cells in each dimension
            - scaffold_type: 'schwarz_p'

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

    # Evaluate Schwarz P function
    F = schwarz_p_function(X, Y, Z, L)

    # Extract single isosurface using marching cubes
    try:
        verts, faces, _, _ = marching_cubes(F, level=params.isovalue, spacing=spacing)
    except ValueError as e:
        raise ValueError(f"Failed to extract Schwarz P surface: {e}")

    if len(verts) == 0 or len(faces) == 0:
        raise ValueError("Marching cubes produced empty mesh for Schwarz P surface")

    # Create wrapper with manifold3d-like interface
    result = _MarchingCubesMeshWrapper(verts, faces)

    # Calculate statistics
    stats = {
        'triangle_count': len(faces),
        'volume_mm3': 0.0,  # TPMS surfaces are not closed solids
        'porosity': 0.5,  # Approximate - Schwarz P has ~50% porosity at isovalue=0
        'cell_count': (int(bx / L), int(by / L), int(bz / L)),
        'scaffold_type': 'schwarz_p'
    }

    return result, stats


def generate_schwarz_p_from_dict(params: dict) -> tuple[Any, dict]:
    """
    Generate Schwarz P scaffold from dictionary parameters.

    Args:
        params: Dictionary with keys matching SchwarzPParams fields

    Returns:
        Tuple of (mesh_wrapper, statistics_dict)
    """
    bbox = params.get('bounding_box_mm', params.get('bounding_box', (10, 10, 10)))
    if isinstance(bbox, dict):
        bbox = (bbox['x'], bbox['y'], bbox['z'])

    return generate_schwarz_p(SchwarzPParams(
        bounding_box_mm=tuple(bbox),
        cell_size_mm=params.get('cell_size_mm', 2.0),
        wall_thickness_mm=params.get('wall_thickness_mm', 0.3),
        isovalue=params.get('isovalue', 0.0),
        samples_per_cell=params.get('samples_per_cell', 20)
    ))
