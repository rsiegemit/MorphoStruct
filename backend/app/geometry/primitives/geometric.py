"""
Geometric primitive shapes using manifold3d.

This module defines 12 fundamental geometric primitives, each registered
with the primitive decorator for automatic schema validation and discovery.
"""

import manifold3d as m3d
import numpy as np
from .registry import primitive


# ============================================================================
# 1. CYLINDER
# ============================================================================

CYLINDER_SCHEMA = {
    "radius_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 10},
    "height_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 20}
}

CYLINDER_DEFAULTS = {
    "radius_mm": 10,
    "height_mm": 20
}

@primitive("cylinder", CYLINDER_SCHEMA, CYLINDER_DEFAULTS)
def create_cylinder(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a cylinder centered on the origin.

    Args:
        dims: Dictionary containing radius_mm and height_mm
        resolution: Number of circular segments

    Returns:
        Manifold cylinder
    """
    radius = dims["radius_mm"]
    height = dims["height_mm"]

    return m3d.Manifold.cylinder(
        height=height,
        radius_low=radius,
        radius_high=radius,
        circular_segments=resolution
    ).translate([0, 0, -height / 2])


# ============================================================================
# 2. SPHERE
# ============================================================================

SPHERE_SCHEMA = {
    "radius_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 10}
}

SPHERE_DEFAULTS = {
    "radius_mm": 10
}

@primitive("sphere", SPHERE_SCHEMA, SPHERE_DEFAULTS)
def create_sphere(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a sphere centered on the origin.

    Args:
        dims: Dictionary containing radius_mm
        resolution: Number of circular segments

    Returns:
        Manifold sphere
    """
    radius = dims["radius_mm"]
    return m3d.Manifold.sphere(radius=radius, circular_segments=resolution)


# ============================================================================
# 3. BOX
# ============================================================================

BOX_SCHEMA = {
    "x_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 10},
    "y_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 10},
    "z_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 10}
}

BOX_DEFAULTS = {
    "x_mm": 10,
    "y_mm": 10,
    "z_mm": 10
}

@primitive("box", BOX_SCHEMA, BOX_DEFAULTS)
def create_box(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a box centered on the origin.

    Args:
        dims: Dictionary containing x_mm, y_mm, z_mm
        resolution: Not used for box (kept for API consistency)

    Returns:
        Manifold box
    """
    x = dims["x_mm"]
    y = dims["y_mm"]
    z = dims["z_mm"]

    return m3d.Manifold.cube([x, y, z], center=True)


# ============================================================================
# 4. CONE (FRUSTUM)
# ============================================================================

CONE_SCHEMA = {
    "bottom_radius_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 10},
    "top_radius_mm": {"type": "number", "min": 0, "max": 1000, "default": 5},
    "height_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 20}
}

CONE_DEFAULTS = {
    "bottom_radius_mm": 10,
    "top_radius_mm": 5,
    "height_mm": 20
}

@primitive("cone", CONE_SCHEMA, CONE_DEFAULTS)
def create_cone(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a cone (or frustum) centered on the origin.

    Args:
        dims: Dictionary containing bottom_radius_mm, top_radius_mm, height_mm
        resolution: Number of circular segments

    Returns:
        Manifold cone/frustum
    """
    bottom_radius = dims["bottom_radius_mm"]
    top_radius = dims["top_radius_mm"]
    height = dims["height_mm"]

    return m3d.Manifold.cylinder(
        height=height,
        radius_low=bottom_radius,
        radius_high=top_radius,
        circular_segments=resolution
    ).translate([0, 0, -height / 2])


# ============================================================================
# 5. TORUS
# ============================================================================

TORUS_SCHEMA = {
    "major_radius_mm": {"type": "number", "min": 1, "max": 1000, "default": 20},
    "minor_radius_mm": {"type": "number", "min": 0.1, "max": 500, "default": 5},
    "arc_degrees": {"type": "number", "min": 1, "max": 360, "default": 360}
}

TORUS_DEFAULTS = {
    "major_radius_mm": 20,
    "minor_radius_mm": 5,
    "arc_degrees": 360
}

@primitive("torus", TORUS_SCHEMA, TORUS_DEFAULTS)
def create_torus(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a torus (or partial torus arc) centered on the origin.

    Args:
        dims: Dictionary containing major_radius_mm, minor_radius_mm, arc_degrees
        resolution: Number of circular segments

    Returns:
        Manifold torus
    """
    major_r = dims["major_radius_mm"]
    minor_r = dims["minor_radius_mm"]
    arc = dims["arc_degrees"]

    # Create circular cross-section at distance major_r from origin
    # Cross-section in XZ plane, offset in X direction
    angles = np.linspace(0, 2 * np.pi, resolution, endpoint=False)
    points = []
    for angle in angles:
        x = major_r + minor_r * np.cos(angle)
        z = minor_r * np.sin(angle)
        points.append([x, z])

    cross_section = m3d.CrossSection([np.array(points)])

    # Revolve around Z axis
    return m3d.Manifold.revolve(cross_section, circular_segments=resolution, revolve_degrees=arc)


# ============================================================================
# 6. CAPSULE
# ============================================================================

CAPSULE_SCHEMA = {
    "radius_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 5},
    "length_mm": {"type": "number", "min": 0, "max": 1000, "default": 20}
}

CAPSULE_DEFAULTS = {
    "radius_mm": 5,
    "length_mm": 20
}

@primitive("capsule", CAPSULE_SCHEMA, CAPSULE_DEFAULTS)
def create_capsule(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a capsule (cylinder with hemisphere caps) centered on the origin.

    Total length = length_mm + 2*radius_mm

    Args:
        dims: Dictionary containing radius_mm, length_mm
        resolution: Number of circular segments

    Returns:
        Manifold capsule
    """
    radius = dims["radius_mm"]
    length = dims["length_mm"]

    # Create cylinder in middle
    cylinder = m3d.Manifold.cylinder(
        height=length,
        radius_low=radius,
        radius_high=radius,
        circular_segments=resolution
    ).translate([0, 0, -length / 2])

    # Create sphere and split in half for hemispheres
    sphere = m3d.Manifold.sphere(radius=radius, circular_segments=resolution)

    # Large box for intersection (to create hemispheres)
    large = radius * 10
    top_box = m3d.Manifold.cube([large, large, large], center=True).translate([0, 0, large / 2])
    bottom_box = m3d.Manifold.cube([large, large, large], center=True).translate([0, 0, -large / 2])

    top_hemisphere = m3d.Manifold.batch_boolean([sphere, top_box], m3d.OpType.Intersect)
    top_hemisphere = top_hemisphere.translate([0, 0, length / 2])

    bottom_hemisphere = m3d.Manifold.batch_boolean([sphere, bottom_box], m3d.OpType.Intersect)
    bottom_hemisphere = bottom_hemisphere.translate([0, 0, -length / 2])

    return cylinder + top_hemisphere + bottom_hemisphere


# ============================================================================
# 7. PYRAMID
# ============================================================================

PYRAMID_SCHEMA = {
    "base_x_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 20},
    "base_y_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 20},
    "height_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 15}
}

PYRAMID_DEFAULTS = {
    "base_x_mm": 20,
    "base_y_mm": 20,
    "height_mm": 15
}

@primitive("pyramid", PYRAMID_SCHEMA, PYRAMID_DEFAULTS)
def create_pyramid(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a pyramid with rectangular base centered on the origin.

    Args:
        dims: Dictionary containing base_x_mm, base_y_mm, height_mm
        resolution: Not used for pyramid (kept for API consistency)

    Returns:
        Manifold pyramid
    """
    base_x = dims["base_x_mm"]
    base_y = dims["base_y_mm"]
    height = dims["height_mm"]

    # Create rectangular base as cross-section
    base_points = [
        [-base_x / 2, -base_y / 2],
        [base_x / 2, -base_y / 2],
        [base_x / 2, base_y / 2],
        [-base_x / 2, base_y / 2],
    ]

    # Create cross-section and extrude with scale_top=(0,0) to create cone/pyramid
    cross_section = m3d.CrossSection([np.array(base_points)])
    pyramid = m3d.Manifold.extrude(cross_section, height, scale_top=(0, 0))

    # Center vertically
    return pyramid.translate([0, 0, -height / 2])


# ============================================================================
# 8. WEDGE
# ============================================================================

WEDGE_SCHEMA = {
    "length_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 20},
    "width_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 20},
    "height_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 10},
    "angle_degrees": {"type": "number", "min": 1, "max": 89, "default": 45}
}

WEDGE_DEFAULTS = {
    "length_mm": 20,
    "width_mm": 20,
    "height_mm": 10,
    "angle_degrees": 45
}

@primitive("wedge", WEDGE_SCHEMA, WEDGE_DEFAULTS)
def create_wedge(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a wedge (triangular prism) centered on the origin.

    The wedge is oriented with the right-angle corner at the origin,
    sloping upward in the +X direction at the specified angle.

    Args:
        dims: Dictionary containing length_mm, width_mm, height_mm, angle_degrees
        resolution: Not used for wedge (kept for API consistency)

    Returns:
        Manifold wedge
    """
    length = dims["length_mm"]
    width = dims["width_mm"]
    height = dims["height_mm"]
    angle = dims["angle_degrees"]

    # Calculate horizontal distance for the slope based on angle
    # tan(angle) = height / base_length
    base_length = height / np.tan(np.radians(angle))

    # Create triangular cross-section in XZ plane
    # Right angle at origin, sloping from (0,0) to (base_length, height)
    triangle_points = [
        [0, 0],
        [base_length, 0],
        [0, height],
    ]

    # Create cross-section and extrude along Y to create wedge
    cross_section = m3d.CrossSection([np.array(triangle_points)])
    wedge = m3d.Manifold.extrude(cross_section, width)

    # Rotate to orient properly and center
    wedge = wedge.rotate([0, 0, 90])  # Rotate to align extrusion with X axis
    wedge = wedge.translate([-width/2, -base_length/2, -height/2])

    return wedge


# ============================================================================
# 9. PRISM
# ============================================================================

PRISM_SCHEMA = {
    "sides": {"type": "integer", "min": 3, "max": 100, "default": 6},
    "radius_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 10},
    "height_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 20}
}

PRISM_DEFAULTS = {
    "sides": 6,
    "radius_mm": 10,
    "height_mm": 20
}

@primitive("prism", PRISM_SCHEMA, PRISM_DEFAULTS)
def create_prism(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a regular prism (n-sided polygon extruded) centered on the origin.

    Args:
        dims: Dictionary containing sides, radius_mm, height_mm
        resolution: Not used (sides parameter controls polygon complexity)

    Returns:
        Manifold prism
    """
    sides = dims["sides"]
    radius = dims["radius_mm"]
    height = dims["height_mm"]

    # Create n-sided polygon cross-section
    angles = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    points = []
    for angle in angles:
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        points.append([x, y])

    cross_section = m3d.CrossSection([np.array(points)])

    # Extrude to height
    return m3d.Manifold.extrude(cross_section, height, n_divisions=1).translate([0, 0, -height / 2])


# ============================================================================
# 10. TUBE
# ============================================================================

TUBE_SCHEMA = {
    "outer_radius_mm": {"type": "number", "min": 0.2, "max": 1000, "default": 10},
    "inner_radius_mm": {"type": "number", "min": 0.1, "max": 999, "default": 7},
    "length_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 20}
}

TUBE_DEFAULTS = {
    "outer_radius_mm": 10,
    "inner_radius_mm": 7,
    "length_mm": 20
}

@primitive("tube", TUBE_SCHEMA, TUBE_DEFAULTS)
def create_tube(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a hollow tube (cylinder with hole) centered on the origin.

    Args:
        dims: Dictionary containing outer_radius_mm, inner_radius_mm, length_mm
        resolution: Number of circular segments

    Returns:
        Manifold tube
    """
    outer_r = dims["outer_radius_mm"]
    inner_r = dims["inner_radius_mm"]
    length = dims["length_mm"]

    # Ensure inner < outer
    if inner_r >= outer_r:
        inner_r = outer_r * 0.7

    outer_cyl = m3d.Manifold.cylinder(
        height=length,
        radius_low=outer_r,
        radius_high=outer_r,
        circular_segments=resolution
    ).translate([0, 0, -length / 2])

    inner_cyl = m3d.Manifold.cylinder(
        height=length + 1,  # Slightly longer to ensure clean boolean
        radius_low=inner_r,
        radius_high=inner_r,
        circular_segments=resolution
    ).translate([0, 0, -length / 2])

    return outer_cyl - inner_cyl


# ============================================================================
# 11. ELLIPSOID
# ============================================================================

ELLIPSOID_SCHEMA = {
    "radius_x_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 10},
    "radius_y_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 8},
    "radius_z_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 6}
}

ELLIPSOID_DEFAULTS = {
    "radius_x_mm": 10,
    "radius_y_mm": 8,
    "radius_z_mm": 6
}

@primitive("ellipsoid", ELLIPSOID_SCHEMA, ELLIPSOID_DEFAULTS)
def create_ellipsoid(dims: dict, resolution: int) -> m3d.Manifold:
    """Create an ellipsoid centered on the origin.

    Args:
        dims: Dictionary containing radius_x_mm, radius_y_mm, radius_z_mm
        resolution: Number of circular segments for base sphere

    Returns:
        Manifold ellipsoid
    """
    rx = dims["radius_x_mm"]
    ry = dims["radius_y_mm"]
    rz = dims["radius_z_mm"]

    # Create unit sphere and scale
    sphere = m3d.Manifold.sphere(radius=1.0, circular_segments=resolution)
    return sphere.scale([rx, ry, rz])


# ============================================================================
# 12. HEMISPHERE
# ============================================================================

HEMISPHERE_SCHEMA = {
    "radius_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 10}
}

HEMISPHERE_DEFAULTS = {
    "radius_mm": 10
}

@primitive("hemisphere", HEMISPHERE_SCHEMA, HEMISPHERE_DEFAULTS)
def create_hemisphere(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a hemisphere (half sphere, z >= 0) centered on the origin.

    Args:
        dims: Dictionary containing radius_mm
        resolution: Number of circular segments

    Returns:
        Manifold hemisphere
    """
    radius = dims["radius_mm"]

    # Create sphere
    sphere = m3d.Manifold.sphere(radius=radius, circular_segments=resolution)

    # Create large box in positive z half-space
    large = radius * 10
    half_space = m3d.Manifold.cube([large, large, large], center=True).translate([0, 0, large / 2])

    return sphere ^ half_space
