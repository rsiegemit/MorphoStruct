"""
Gradient scaffold generator with continuous porosity/stiffness gradients.

Creates scaffolds with varying pore size and density along a specified axis.
Useful for tissue engineering applications requiring mechanical or biological gradients.

Features:
- Linear, exponential, or sigmoid gradient functions
- Configurable gradient direction (x, y, or z axis)
- Continuous variation in pore size
- Grid-based pore arrangement
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from typing import Literal
from ..core import batch_union


@dataclass
class GradientScaffoldParams:
    """Parameters for gradient scaffold generation."""
    dimensions_mm: tuple[float, float, float] = (5.0, 5.0, 5.0)  # Reduced from 10.0, 10.0, 10.0
    gradient_direction: Literal['x', 'y', 'z'] = 'z'
    start_porosity: float = 0.2  # Porosity at start (0.0 = solid, 1.0 = empty)
    end_porosity: float = 0.8
    gradient_type: Literal['linear', 'exponential', 'sigmoid'] = 'linear'
    pore_base_size_mm: float = 0.5  # Base pore diameter
    grid_spacing_mm: float = 2.0  # Distance between pore centers (increased from 1.5)
    resolution: int = 8  # Reduced from 12


def calculate_pore_size(
    position: float,
    length: float,
    start_porosity: float,
    end_porosity: float,
    pore_base_size: float,
    gradient_type: Literal['linear', 'exponential', 'sigmoid']
) -> float:
    """
    Calculate pore size at a given position based on gradient function.

    Porosity controls the pore size: higher porosity = larger pores.
    The relationship between porosity and pore size is:
    pore_size = base_size * sqrt(porosity / 0.5)

    Args:
        position: Position along gradient axis (0 to length)
        length: Total length of gradient axis
        start_porosity: Porosity at position 0
        end_porosity: Porosity at position length
        pore_base_size: Base pore size at porosity 0.5
        gradient_type: Type of gradient function

    Returns:
        Pore size at the given position
    """
    # Normalized position [0, 1]
    t = position / length if length > 0 else 0

    # Calculate porosity based on gradient type
    if gradient_type == 'linear':
        porosity = start_porosity + (end_porosity - start_porosity) * t

    elif gradient_type == 'exponential':
        # Exponential interpolation
        if start_porosity > 0 and end_porosity > 0:
            log_start = np.log(start_porosity)
            log_end = np.log(end_porosity)
            porosity = np.exp(log_start + (log_end - log_start) * t)
        else:
            # Fallback to linear if zero values
            porosity = start_porosity + (end_porosity - start_porosity) * t

    elif gradient_type == 'sigmoid':
        # Sigmoid interpolation (smooth S-curve)
        # Maps [0, 1] to smooth transition
        sigmoid_t = 1 / (1 + np.exp(-10 * (t - 0.5)))
        porosity = start_porosity + (end_porosity - start_porosity) * sigmoid_t

    else:
        # Default to linear
        porosity = start_porosity + (end_porosity - start_porosity) * t

    # Clamp porosity to valid range
    porosity = np.clip(porosity, 0.01, 0.95)

    # Convert porosity to pore size
    # At porosity 0.5, pore size = base size
    # Scale by sqrt to maintain reasonable relationship
    pore_size = pore_base_size * np.sqrt(porosity / 0.5)

    return pore_size


def generate_gradient_scaffold(params: GradientScaffoldParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate a gradient scaffold with varying porosity.

    Creates a grid of spherical pores with sizes varying along the specified
    gradient direction according to the chosen gradient function.

    Args:
        params: GradientScaffoldParams specifying geometry and gradient

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, relative_density,
                     pore_count, gradient_type, scaffold_type

    Raises:
        ValueError: If no pores are generated
    """
    dx, dy, dz = params.dimensions_mm
    spacing = params.grid_spacing_mm

    # Determine gradient axis and perpendicular axes
    if params.gradient_direction == 'x':
        gradient_length = dx
        axis_idx = 0
    elif params.gradient_direction == 'y':
        gradient_length = dy
        axis_idx = 1
    else:  # 'z'
        gradient_length = dz
        axis_idx = 2

    # Calculate number of pores in each dimension
    nx = max(1, int(dx / spacing))
    ny = max(1, int(dy / spacing))
    nz = max(1, int(dz / spacing))

    # Generate pore positions and sizes
    pores = []
    pore_count = 0

    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                # Calculate position
                x = -dx/2 + (i + 0.5) * dx / nx
                y = -dy/2 + (j + 0.5) * dy / ny
                z = -dz/2 + (k + 0.5) * dz / nz

                position = np.array([x, y, z])

                # Get position along gradient axis
                if params.gradient_direction == 'x':
                    gradient_pos = x + dx/2  # 0 to dx
                elif params.gradient_direction == 'y':
                    gradient_pos = y + dy/2  # 0 to dy
                else:  # 'z'
                    gradient_pos = z + dz/2  # 0 to dz

                # Calculate pore size at this position
                pore_size = calculate_pore_size(
                    gradient_pos,
                    gradient_length,
                    params.start_porosity,
                    params.end_porosity,
                    params.pore_base_size_mm,
                    params.gradient_type
                )

                # Create pore (sphere)
                pore = m3d.Manifold.sphere(pore_size / 2, params.resolution)
                pore = pore.translate([x, y, z])
                pores.append(pore)
                pore_count += 1

    if not pores:
        raise ValueError("No pores generated")

    # Union all pores
    pores_combined = batch_union(pores)

    # Create bounding box
    bbox = m3d.Manifold.cube([dx, dy, dz], center=True)

    # Subtract pores from solid block
    result = bbox - pores_combined

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0
    solid_volume = dx * dy * dz
    relative_density = volume / solid_volume if solid_volume > 0 else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'relative_density': relative_density,
        'pore_count': pore_count,
        'gradient_type': params.gradient_type,
        'gradient_direction': params.gradient_direction,
        'scaffold_type': 'gradient_scaffold'
    }

    return result, stats


def generate_gradient_scaffold_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate gradient scaffold from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching GradientScaffoldParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    # Handle dimensions variations
    dimensions = params.get('dimensions_mm', params.get('dimensions', (10.0, 10.0, 10.0)))
    if isinstance(dimensions, dict):
        dimensions = (dimensions['x'], dimensions['y'], dimensions['z'])

    return generate_gradient_scaffold(GradientScaffoldParams(
        dimensions_mm=tuple(dimensions) if dimensions != (10.0, 10.0, 10.0) else (5.0, 5.0, 5.0),
        gradient_direction=params.get('gradient_direction', 'z'),
        start_porosity=params.get('start_porosity', 0.2),
        end_porosity=params.get('end_porosity', 0.8),
        gradient_type=params.get('gradient_type', 'linear'),
        pore_base_size_mm=params.get('pore_base_size_mm', params.get('pore_base_size', 0.5)),
        grid_spacing_mm=params.get('grid_spacing_mm', params.get('grid_spacing', 2.0)),
        resolution=params.get('resolution', 8)
    ))
