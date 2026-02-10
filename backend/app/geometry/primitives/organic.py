"""Organic and bio-inspired geometric primitives.

This module provides primitives for creating organic structures like branches,
bifurcations, pores, channels, fibers, membranes, and lattice cells commonly
found in biological tissue engineering and biomedical applications.
"""

import manifold3d as m3d
import numpy as np
from .registry import primitive


# Branch primitive - tapered cylinder for organic branching structures
BRANCH_SCHEMA = {
    "start_radius_mm": {"type": "number", "min": 0.1, "max": 100, "default": 2.0},
    "end_radius_mm": {"type": "number", "min": 0.1, "max": 100, "default": 1.0},
    "length_mm": {"type": "number", "min": 0.5, "max": 500, "default": 10.0}
}
BRANCH_DEFAULTS = {
    "start_radius_mm": 2.0,
    "end_radius_mm": 1.0,
    "length_mm": 10.0
}


@primitive("branch", BRANCH_SCHEMA, BRANCH_DEFAULTS)
def create_branch(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a tapered cylinder (frustum) for organic branching structures.

    Args:
        dims: Dictionary with start_radius_mm, end_radius_mm, length_mm
        resolution: Number of segments for circular resolution

    Returns:
        Manifold object representing a tapered branch
    """
    start_radius = dims["start_radius_mm"]
    end_radius = dims["end_radius_mm"]
    length = dims["length_mm"]

    return m3d.Manifold.cylinder(
        height=length,
        radius_low=start_radius,
        radius_high=end_radius,
        circular_segments=resolution
    )


# Bifurcation primitive - Y-junction where one tube splits into two
BIFURCATION_SCHEMA = {
    "parent_radius_mm": {"type": "number", "min": 0.1, "max": 100, "default": 2.0},
    "child_radius_mm": {"type": "number", "min": 0.1, "max": 100, "default": 1.5},
    "angle_degrees": {"type": "number", "min": 10, "max": 120, "default": 45},
    "length_mm": {"type": "number", "min": 0.5, "max": 500, "default": 5.0}
}
BIFURCATION_DEFAULTS = {
    "parent_radius_mm": 2.0,
    "child_radius_mm": 1.5,
    "angle_degrees": 45,
    "length_mm": 5.0
}


@primitive("bifurcation", BIFURCATION_SCHEMA, BIFURCATION_DEFAULTS)
def create_bifurcation(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a Y-junction where one tube splits into two.

    Args:
        dims: Dictionary with parent_radius_mm, child_radius_mm, angle_degrees, length_mm
        resolution: Number of segments for circular resolution

    Returns:
        Manifold object representing a bifurcation junction
    """
    parent_radius = dims["parent_radius_mm"]
    child_radius = dims["child_radius_mm"]
    angle = dims["angle_degrees"]
    length = dims["length_mm"]

    # Parent cylinder (along Z-axis)
    parent = m3d.Manifold.cylinder(
        height=length,
        radius_low=parent_radius,
        radius_high=parent_radius,
        circular_segments=resolution
    )

    # Junction sphere at split point for smooth connection
    junction = m3d.Manifold.sphere(
        radius=parent_radius * 1.1,
        circular_segments=resolution
    ).translate([0, 0, length])

    # Calculate child branch angles
    half_angle = np.radians(angle / 2)

    # Create two child branches
    child_base = m3d.Manifold.cylinder(
        height=length,
        radius_low=child_radius,
        radius_high=child_radius,
        circular_segments=resolution
    )

    # Left child - rotate around Y-axis by +half_angle
    child_left = child_base.rotate([0, np.degrees(half_angle), 0]).translate([0, 0, length])

    # Right child - rotate around Y-axis by -half_angle
    child_right = child_base.rotate([0, -np.degrees(half_angle), 0]).translate([0, 0, length])

    # Union all components
    result = parent + junction + child_left + child_right

    return result


# Pore primitive - simple cylinder for CSG subtraction (creating holes)
PORE_SCHEMA = {
    "diameter_mm": {"type": "number", "min": 0.1, "max": 50, "default": 1.0},
    "depth_mm": {"type": "number", "min": 0.1, "max": 100, "default": 2.0}
}
PORE_DEFAULTS = {
    "diameter_mm": 1.0,
    "depth_mm": 2.0
}


@primitive("pore", PORE_SCHEMA, PORE_DEFAULTS)
def create_pore(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a simple cylinder for CSG subtraction (creating holes).

    Args:
        dims: Dictionary with diameter_mm, depth_mm
        resolution: Number of segments for circular resolution

    Returns:
        Manifold object representing a pore (oriented along Z-axis)
    """
    diameter = dims["diameter_mm"]
    depth = dims["depth_mm"]
    radius = diameter / 2.0

    return m3d.Manifold.cylinder(
        height=depth,
        radius_low=radius,
        radius_high=radius,
        circular_segments=resolution
    )


# Channel primitive - cylinder for CSG subtraction (through-holes/channels)
CHANNEL_SCHEMA = {
    "diameter_mm": {"type": "number", "min": 0.1, "max": 50, "default": 1.0},
    "length_mm": {"type": "number", "min": 0.1, "max": 500, "default": 10.0}
}
CHANNEL_DEFAULTS = {
    "diameter_mm": 1.0,
    "length_mm": 10.0
}


@primitive("channel", CHANNEL_SCHEMA, CHANNEL_DEFAULTS)
def create_channel(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a cylinder for CSG subtraction (through-holes/channels).

    Args:
        dims: Dictionary with diameter_mm, length_mm
        resolution: Number of segments for circular resolution

    Returns:
        Manifold object representing a channel (oriented along Z-axis)
    """
    diameter = dims["diameter_mm"]
    length = dims["length_mm"]
    radius = diameter / 2.0

    return m3d.Manifold.cylinder(
        height=length,
        radius_low=radius,
        radius_high=radius,
        circular_segments=resolution
    )


# Fiber primitive - straight or sinusoidal fiber
FIBER_SCHEMA = {
    "diameter_mm": {"type": "number", "min": 0.01, "max": 10, "default": 0.5},
    "length_mm": {"type": "number", "min": 0.5, "max": 500, "default": 20.0},
    "crimp_amplitude_mm": {"type": "number", "min": 0, "max": 10, "default": 0.0},
    "crimp_wavelength_mm": {"type": "number", "min": 0.1, "max": 50, "default": 5.0}
}
FIBER_DEFAULTS = {
    "diameter_mm": 0.5,
    "length_mm": 20.0,
    "crimp_amplitude_mm": 0.0,
    "crimp_wavelength_mm": 5.0
}


@primitive("fiber", FIBER_SCHEMA, FIBER_DEFAULTS)
def create_fiber(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a fiber with optional sinusoidal crimp.

    If crimp_amplitude == 0, creates a straight cylinder.
    If crimp_amplitude > 0, creates a fiber following a sinusoidal path.

    Args:
        dims: Dictionary with diameter_mm, length_mm, crimp_amplitude_mm, crimp_wavelength_mm
        resolution: Number of segments for circular resolution

    Returns:
        Manifold object representing a fiber
    """
    diameter = dims["diameter_mm"]
    length = dims["length_mm"]
    amplitude = dims["crimp_amplitude_mm"]
    wavelength = dims["crimp_wavelength_mm"]
    radius = diameter / 2.0

    # Straight fiber case
    if amplitude == 0:
        return m3d.Manifold.cylinder(
            height=length,
            radius_low=radius,
            radius_high=radius,
            circular_segments=resolution
        )

    # Crimped fiber - create using hull of spheres along sinusoidal path
    num_segments = max(20, int(length / (wavelength / 4)))
    z_positions = np.linspace(0, length, num_segments)

    # Create spheres along sinusoidal path
    spheres = []
    for z in z_positions:
        x = amplitude * np.sin(2 * np.pi * z / wavelength)
        sphere = m3d.Manifold.sphere(radius=radius, circular_segments=resolution)
        sphere = sphere.translate([x, 0, z])
        spheres.append(sphere)

    # Hull between consecutive spheres to create smooth fiber
    if len(spheres) < 2:
        return spheres[0] if spheres else m3d.Manifold()

    segments = []
    for i in range(len(spheres) - 1):
        segment = spheres[i] + spheres[i + 1]
        segment = segment.hull()
        segments.append(segment)

    # Union all segments
    result = segments[0]
    for seg in segments[1:]:
        result = result + seg

    return result


# Membrane primitive - thin curved sheet (like cell membrane or dome)
MEMBRANE_SCHEMA = {
    "thickness_mm": {"type": "number", "min": 0.01, "max": 5, "default": 0.1},
    "radius_mm": {"type": "number", "min": 0.5, "max": 100, "default": 10.0},
    "curvature": {"type": "number", "min": 0, "max": 1, "default": 0.5}
}
MEMBRANE_DEFAULTS = {
    "thickness_mm": 0.1,
    "radius_mm": 10.0,
    "curvature": 0.5
}


@primitive("membrane", MEMBRANE_SCHEMA, MEMBRANE_DEFAULTS)
def create_membrane(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a thin curved sheet (like a cell membrane or dome).

    If curvature == 0, creates a flat disc.
    If curvature > 0, creates a spherical cap shape.

    Args:
        dims: Dictionary with thickness_mm, radius_mm, curvature (0-1)
        resolution: Number of segments for circular resolution

    Returns:
        Manifold object representing a membrane
    """
    thickness = dims["thickness_mm"]
    radius = dims["radius_mm"]
    curvature = dims["curvature"]

    # Flat membrane case
    if curvature == 0:
        return m3d.Manifold.cylinder(
            height=thickness,
            radius_low=radius,
            radius_high=radius,
            circular_segments=resolution
        )

    # Curved membrane - create spherical cap shell
    # Sphere radius based on curvature (higher curvature = smaller sphere radius)
    sphere_radius = radius / curvature

    # Create outer and inner spheres
    outer_sphere = m3d.Manifold.sphere(
        radius=sphere_radius,
        circular_segments=resolution
    )
    inner_sphere = m3d.Manifold.sphere(
        radius=sphere_radius - thickness,
        circular_segments=resolution
    )

    # Create cutting plane to get cap (halfspace at appropriate height)
    # Cap height based on desired base radius
    cap_height = sphere_radius - np.sqrt(sphere_radius**2 - radius**2)

    # Create a large box to subtract everything below the cutting plane
    cutting_box = m3d.Manifold.cube([sphere_radius * 4, sphere_radius * 4, sphere_radius * 2], True)
    cutting_box = cutting_box.translate([0, 0, -sphere_radius + cap_height - sphere_radius])

    # Create shell and cut to cap
    shell = outer_sphere - inner_sphere
    result = shell - cutting_box

    return result


# Lattice cell primitive - single cubic unit cell with struts
LATTICE_CELL_SCHEMA = {
    "cell_size_mm": {"type": "number", "min": 0.5, "max": 50, "default": 5.0},
    "strut_diameter_mm": {"type": "number", "min": 0.1, "max": 10, "default": 0.5}
}
LATTICE_CELL_DEFAULTS = {
    "cell_size_mm": 5.0,
    "strut_diameter_mm": 0.5
}


@primitive("lattice_cell", LATTICE_CELL_SCHEMA, LATTICE_CELL_DEFAULTS)
def create_lattice_cell(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a single unit cell of a cubic lattice.

    Creates 12 struts forming the edges of a cube.

    Args:
        dims: Dictionary with cell_size_mm, strut_diameter_mm
        resolution: Number of segments for circular resolution

    Returns:
        Manifold object representing a lattice unit cell
    """
    cell_size = dims["cell_size_mm"]
    strut_diameter = dims["strut_diameter_mm"]
    radius = strut_diameter / 2.0

    # Create a base strut (cylinder)
    strut = m3d.Manifold.cylinder(
        height=cell_size,
        radius_low=radius,
        radius_high=radius,
        circular_segments=resolution
    )

    half = cell_size / 2.0
    struts = []

    # 4 vertical struts (parallel to Z-axis)
    for x in [-half, half]:
        for y in [-half, half]:
            s = strut.translate([x, y, 0])
            struts.append(s)

    # 4 struts parallel to X-axis (bottom)
    strut_x = strut.rotate([0, 90, 0])
    for y in [-half, half]:
        for z in [-half, half]:
            s = strut_x.translate([0, y, z])
            struts.append(s)

    # 4 struts parallel to Y-axis
    strut_y = strut.rotate([90, 0, 0])
    for x in [-half, half]:
        for z in [-half, half]:
            s = strut_y.translate([x, 0, z])
            struts.append(s)

    # Union all struts
    result = struts[0]
    for s in struts[1:]:
        result = result + s

    return result


# Pore array primitive - grid of cylinders for CSG subtraction
PORE_ARRAY_SCHEMA = {
    "pore_size_mm": {"type": "number", "min": 0.1, "max": 20, "default": 1.0},
    "spacing_mm": {"type": "number", "min": 0.5, "max": 50, "default": 3.0},
    "count_x": {"type": "integer", "min": 1, "max": 100, "default": 5},
    "count_y": {"type": "integer", "min": 1, "max": 100, "default": 5},
    "depth_mm": {"type": "number", "min": 0.1, "max": 100, "default": 2.0}
}
PORE_ARRAY_DEFAULTS = {
    "pore_size_mm": 1.0,
    "spacing_mm": 3.0,
    "count_x": 5,
    "count_y": 5,
    "depth_mm": 2.0
}


@primitive("pore_array", PORE_ARRAY_SCHEMA, PORE_ARRAY_DEFAULTS)
def create_pore_array(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a grid of cylinders for CSG subtraction.

    Creates count_x * count_y pores arranged in a regular grid.
    Spacing is center-to-center distance.

    Args:
        dims: Dictionary with pore_size_mm, spacing_mm, count_x, count_y, depth_mm
        resolution: Number of segments for circular resolution

    Returns:
        Manifold object representing a union of all pore cylinders
    """
    pore_size = dims["pore_size_mm"]
    spacing = dims["spacing_mm"]
    count_x = int(dims["count_x"])
    count_y = int(dims["count_y"])
    depth = dims["depth_mm"]
    radius = pore_size / 2.0

    # Create base pore cylinder
    pore = m3d.Manifold.cylinder(
        height=depth,
        radius_low=radius,
        radius_high=radius,
        circular_segments=resolution
    )

    # Create grid of pores
    pores = []
    for i in range(count_x):
        for j in range(count_y):
            x = (i - (count_x - 1) / 2.0) * spacing
            y = (j - (count_y - 1) / 2.0) * spacing
            p = pore.translate([x, y, 0])
            pores.append(p)

    # Union all pores
    if not pores:
        return pore

    result = pores[0]
    for p in pores[1:]:
        result = result + p

    return result
