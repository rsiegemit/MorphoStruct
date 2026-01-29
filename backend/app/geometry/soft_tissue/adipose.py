"""
Adipose tissue scaffold generator with honeycomb structure.

Provides parametric generation of adipose (fat) tissue scaffolds with:
- Hexagonal honeycomb pattern for adipocyte housing
- Configurable cell size (100-200µm)
- Thin walls between cells
- Vertical vascular channels for perfusion
- Cylindrical overall shape
"""

from __future__ import annotations
import manifold3d as m3d
import numpy as np
from dataclasses import dataclass
from ..core import batch_union


@dataclass
class AdiposeTissueParams:
    """Parameters for adipose tissue scaffold generation."""
    cell_size_um: float = 250.0  # micrometers (adipocyte diameter) - larger cells = fewer cells
    wall_thickness_um: float = 40.0  # micrometers
    vascular_channel_spacing_mm: float = 3.0  # spacing between perfusion channels (fewer channels)
    vascular_channel_diameter_mm: float = 0.25
    height_mm: float = 3.0
    diameter_mm: float = 6.0
    resolution: int = 6  # Lower resolution for hexagons


def make_hexagonal_prism(
    side_length: float,
    height: float,
    center_x: float,
    center_y: float,
    resolution: int = 6
) -> m3d.Manifold:
    """
    Create a hexagonal prism (cell chamber).

    Args:
        side_length: Length of hexagon side
        height: Height of prism
        center_x: X position of center
        center_y: Y position of center
        resolution: Must be 6 for hexagon

    Returns:
        Manifold representing the hexagonal prism
    """
    # Create hexagon by using cylinder with 6 segments
    # For a hexagon inscribed in a circle of radius R:
    # side_length = R
    radius = side_length
    hexagon = m3d.Manifold.cylinder(height, radius, radius, 6)

    return hexagon.translate([center_x, center_y, height / 2])


def get_hexagonal_grid_positions(
    diameter: float,
    cell_size: float
) -> list[tuple[float, float]]:
    """
    Get positions for hexagonal grid pattern.

    Uses offset grid to create honeycomb pattern.

    Args:
        diameter: Overall diameter of scaffold
        cell_size: Size of each hexagonal cell

    Returns:
        List of (x, y) positions for cell centers
    """
    positions = []
    radius = diameter / 2

    # Hexagonal grid spacing
    # For hexagons with side length s:
    # Horizontal spacing: 1.5 * s
    # Vertical spacing: sqrt(3) * s
    h_spacing = 1.5 * cell_size
    v_spacing = np.sqrt(3) * cell_size

    # Calculate grid bounds
    n_cols = max(1, int(diameter / h_spacing))
    n_rows = max(1, int(diameter / v_spacing))

    for row in range(n_rows):
        for col in range(n_cols):
            # Offset every other row for honeycomb pattern
            x_offset = (cell_size * 0.75) if row % 2 == 1 else 0
            x = (col - n_cols / 2 + 0.5) * h_spacing + x_offset
            y = (row - n_rows / 2 + 0.5) * v_spacing

            # Check if within circular boundary
            if np.sqrt(x*x + y*y) < radius - cell_size:
                positions.append((x, y))

    return positions


def make_vascular_channel(
    height: float,
    channel_diameter: float,
    x_pos: float,
    y_pos: float,
    resolution: int
) -> m3d.Manifold:
    """
    Create a vertical vascular channel.

    Args:
        height: Height of scaffold
        channel_diameter: Diameter of channel
        x_pos: X position
        y_pos: Y position
        resolution: Circular resolution

    Returns:
        Manifold representing the channel
    """
    channel_radius = channel_diameter / 2
    channel = m3d.Manifold.cylinder(
        height * 1.1,
        channel_radius,
        channel_radius,
        resolution
    )
    return channel.translate([x_pos, y_pos, height / 2])


def generate_adipose_tissue(params: AdiposeTissueParams) -> tuple[m3d.Manifold, dict]:
    """
    Generate an adipose tissue scaffold.

    Args:
        params: AdiposeTissueParams specifying geometry and structure

    Returns:
        Tuple of (manifold, stats_dict)
        - manifold: The 3D geometry
        - stats_dict: Dictionary with triangle_count, volume_mm3, cell_count,
                     cell_size_um, porosity, scaffold_type

    Raises:
        ValueError: If parameters are invalid
    """
    if params.cell_size_um <= 0 or params.wall_thickness_um <= 0:
        raise ValueError("Cell size and wall thickness must be positive")
    if params.wall_thickness_um >= params.cell_size_um:
        raise ValueError("Wall thickness must be less than cell size")

    # Convert micrometers to millimeters
    cell_size_mm = params.cell_size_um / 1000.0
    wall_thickness_mm = params.wall_thickness_um / 1000.0

    # Create outer cylinder
    outer_radius = params.diameter_mm / 2
    outer_cylinder = m3d.Manifold.cylinder(
        params.height_mm,
        outer_radius,
        outer_radius,
        params.resolution * 4  # Higher resolution for outer wall
    )
    outer_cylinder = outer_cylinder.translate([0, 0, params.height_mm / 2])

    # Get hexagonal cell positions
    cell_positions = get_hexagonal_grid_positions(
        params.diameter_mm - wall_thickness_mm * 2,  # Leave room for outer wall
        cell_size_mm
    )

    # Create hexagonal cell chambers
    cells = []
    for x, y in cell_positions:
        cell = make_hexagonal_prism(
            cell_size_mm / 2,  # Hexagon radius
            params.height_mm,
            x, y,
            6  # Hexagon has 6 sides
        )
        cells.append(cell)

    if not cells:
        raise ValueError("No cells generated")

    # Union all cells
    cells_union = batch_union(cells)

    # Create honeycomb by subtracting cells from outer cylinder
    # This leaves the walls between cells
    honeycomb = outer_cylinder - cells_union

    # Add vascular channels if requested
    if params.vascular_channel_spacing_mm > 0 and params.vascular_channel_diameter_mm > 0:
        channels = []
        n_channels = max(1, int(params.diameter_mm / params.vascular_channel_spacing_mm))

        for i in range(n_channels):
            for j in range(n_channels):
                x = (i - n_channels / 2 + 0.5) * params.vascular_channel_spacing_mm
                y = (j - n_channels / 2 + 0.5) * params.vascular_channel_spacing_mm

                # Check if channel is within boundary
                if np.sqrt(x*x + y*y) < outer_radius - params.vascular_channel_diameter_mm:
                    channel = make_vascular_channel(
                        params.height_mm,
                        params.vascular_channel_diameter_mm,
                        x, y,
                        params.resolution * 2
                    )
                    channels.append(channel)

        if channels:
            channels_union = batch_union(channels)
            result = honeycomb - channels_union
        else:
            result = honeycomb
    else:
        result = honeycomb

    # Calculate statistics
    mesh = result.to_mesh()
    volume = result.volume() if hasattr(result, 'volume') else 0
    solid_volume = np.pi * outer_radius * outer_radius * params.height_mm
    porosity = 1 - (volume / solid_volume) if solid_volume > 0 else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'porosity': porosity,
        'cell_count': len(cells),
        'cell_size_um': params.cell_size_um,
        'wall_thickness_um': params.wall_thickness_um,
        'vascular_channels': len(channels) if params.vascular_channel_spacing_mm > 0 else 0,
        'scaffold_type': 'adipose_tissue'
    }

    return result, stats


def generate_adipose_tissue_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """
    Generate adipose tissue scaffold from dictionary parameters (for API compatibility).

    Args:
        params: Dictionary with keys matching AdiposeTissueParams fields

    Returns:
        Tuple of (manifold, stats_dict)
    """
    return generate_adipose_tissue(AdiposeTissueParams(
        cell_size_um=params.get('cell_size_um', 250.0),
        wall_thickness_um=params.get('wall_thickness_um', 40.0),
        vascular_channel_spacing_mm=params.get('vascular_channel_spacing_mm', 3.0),
        vascular_channel_diameter_mm=params.get('vascular_channel_diameter_mm', 0.25),
        height_mm=params.get('height_mm', 3.0),
        diameter_mm=params.get('diameter_mm', 6.0),
        resolution=params.get('resolution', 6)
    ))
