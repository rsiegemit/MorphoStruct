"""
Kidney tubule scaffold generator.

Creates convoluted proximal tubule structures with perfusable lumen:
- Sinusoidal tube path mimicking nephron convolution
- Hollow interior for fluid flow
- Controlled tubule diameter and wall thickness
- Adjustable convolution parameters
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass


@dataclass
class KidneyTubuleParams:
    """Parameters for kidney tubule scaffold generation."""
    tubule_diameter: float = 100.0  # µm (50-200µm)
    wall_thickness: float = 15.0  # µm
    convolution_amplitude: float = 300.0  # µm (reduced from 500)
    convolution_frequency: float = 2.0  # oscillations per length unit (reduced from 3)
    length: float = 5.0  # mm (reduced from 10)
    resolution: int = 8  # reduced from 16


def create_convoluted_path(length: float, amplitude: float, frequency: float, num_points: int = 100) -> np.ndarray:
    """
    Generate a sinusoidal convoluted path in 3D.

    Args:
        length: Total path length
        amplitude: Amplitude of convolution
        frequency: Oscillation frequency
        num_points: Number of points along path

    Returns:
        Array of (x, y, z) positions along path
    """
    t = np.linspace(0, length, num_points)

    # Create 3D sinusoidal path (convoluted in XY plane, progressing in Z)
    x = amplitude * np.sin(2 * np.pi * frequency * t / length)
    y = amplitude * np.cos(2 * np.pi * frequency * t / length) * 0.7  # Elliptical
    z = t

    return np.column_stack([x, y, z])


def create_hollow_tube_segment(p1: np.ndarray, p2: np.ndarray, outer_radius: float,
                               inner_radius: float, resolution: int) -> m3d.Manifold:
    """
    Create a hollow cylindrical segment between two points.

    Args:
        p1: Start point (x, y, z)
        p2: End point (x, y, z)
        outer_radius: Outer radius
        inner_radius: Inner radius (for hollow lumen)
        resolution: Number of segments around cylinder

    Returns:
        Hollow cylinder manifold
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    length = np.sqrt(dx*dx + dy*dy + dz*dz)

    if length < 1e-6:
        return m3d.Manifold()

    # Create outer and inner cylinders
    outer = m3d.Manifold.cylinder(length, outer_radius, outer_radius, resolution)
    inner = m3d.Manifold.cylinder(length + 0.02, inner_radius, inner_radius, resolution)
    inner = inner.translate([0, 0, -0.01])

    hollow = outer - inner

    # Rotate to align with direction
    h = np.sqrt(dx*dx + dy*dy)
    if h > 0.001 or abs(dz) > 0.001:
        tilt = np.arctan2(h, dz) * 180 / np.pi
        azim = np.arctan2(dy, dx) * 180 / np.pi
        hollow = hollow.rotate([0, tilt, 0]).rotate([0, 0, azim])

    return hollow.translate([p1[0], p1[1], p1[2]])


def generate_kidney_tubule(params: KidneyTubuleParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a kidney tubule scaffold with convoluted path.

    Args:
        params: KidneyTubuleParams specifying geometry

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, path_length, scaffold_type

    Raises:
        ValueError: If no segments are generated
    """
    # Convert µm to mm
    outer_radius = params.tubule_diameter / 2000.0
    inner_radius = outer_radius - (params.wall_thickness / 1000.0)
    amplitude_mm = params.convolution_amplitude / 1000.0

    if inner_radius <= 0:
        inner_radius = outer_radius * 0.5

    # Generate convoluted path (reduced points for faster generation)
    num_points = max(30, int(params.length * 5))  # reduced from max(50, length*10)
    path = create_convoluted_path(params.length, amplitude_mm, params.convolution_frequency, num_points)

    # Create tubule segments along path
    segments = []
    for i in range(len(path) - 1):
        seg = create_hollow_tube_segment(
            path[i], path[i+1],
            outer_radius, inner_radius,
            params.resolution
        )
        if seg.num_vert() > 0:
            segments.append(seg)

    if not segments:
        raise ValueError("No tubule segments generated")

    # Union all segments
    result = segments[0]
    for seg in segments[1:]:
        result = result + seg

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0

    # Calculate actual path length
    path_length = 0
    for i in range(len(path) - 1):
        dx = path[i+1] - path[i]
        path_length += np.linalg.norm(dx)

    stats = {
        'triangle_count': len(mesh.tri_verts) if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'path_length_mm': path_length,
        'scaffold_type': 'kidney_tubule'
    }

    return result, stats


def generate_kidney_tubule_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate kidney tubule from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching KidneyTubuleParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_kidney_tubule(KidneyTubuleParams(
        tubule_diameter=params.get('tubule_diameter', 100.0),
        wall_thickness=params.get('wall_thickness', 15.0),
        convolution_amplitude=params.get('convolution_amplitude', 300.0),
        convolution_frequency=params.get('convolution_frequency', 2.0),
        length=params.get('length', 5.0),
        resolution=params.get('resolution', 8)
    ))
