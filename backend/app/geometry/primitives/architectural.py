"""Architectural geometric primitives for mechanical design features.

This module provides architectural primitives commonly used in CAD and manufacturing,
such as fillets, chamfers, slots, counterbores, countersinks, bosses, and ribs.
Each primitive is registered using the @primitive decorator from registry.py.

Example Usage:
    >>> from backend.app.geometry.primitives.architectural import create_fillet
    >>> from backend.app.geometry.primitives.registry import get_primitive
    >>>
    >>> # Direct function call
    >>> fillet = create_fillet({"radius_mm": 2, "length_mm": 10}, resolution=32)
    >>>
    >>> # Via registry
    >>> prim = get_primitive("fillet")
    >>> fillet = prim.func({"radius_mm": 2, "length_mm": 10}, resolution=32)
"""

import manifold3d as m3d
import numpy as np
from .registry import primitive


# ============================================================================
# FILLET - Quarter-cylinder for rounding edges
# ============================================================================

FILLET_SCHEMA = {
    "radius_mm": {"type": "number", "min": 0.1, "max": 100, "default": 1.0},
    "length_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 10.0}
}

FILLET_DEFAULTS = {
    "radius_mm": 1.0,
    "length_mm": 10.0
}

@primitive("fillet", FILLET_SCHEMA, FILLET_DEFAULTS)
def create_fillet(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a quarter-cylinder fillet for rounding edges.

    Args:
        dims: Dictionary with 'radius_mm' and 'length_mm'
        resolution: Number of segments for circular arc

    Returns:
        Manifold3D mesh of fillet positioned at origin corner (90° arc in XY plane)
    """
    radius = dims.get("radius_mm", FILLET_DEFAULTS["radius_mm"])
    length = dims.get("length_mm", FILLET_DEFAULTS["length_mm"])

    # Create quarter-circle cross-section profile
    angles = np.linspace(0, np.pi / 2, resolution // 4 + 1)
    profile_points = []

    # Add origin point
    profile_points.append([0, 0])

    # Add arc points
    for angle in angles:
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        profile_points.append([x, y])

    # Close the profile back to origin
    profile_points.append([0, 0])

    # Create 2D cross-section and extrude
    cross_section = m3d.CrossSection([np.array(profile_points)])
    fillet = m3d.Manifold.extrude(cross_section, length)

    return fillet


# ============================================================================
# CHAMFER - 45° bevel for cutting corners
# ============================================================================

CHAMFER_SCHEMA = {
    "size_mm": {"type": "number", "min": 0.1, "max": 100, "default": 1.0},
    "length_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 10.0}
}

CHAMFER_DEFAULTS = {
    "size_mm": 1.0,
    "length_mm": 10.0
}

@primitive("chamfer", CHAMFER_SCHEMA, CHAMFER_DEFAULTS)
def create_chamfer(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a 45° chamfer bevel for cutting corners.

    Args:
        dims: Dictionary with 'size_mm' (leg length) and 'length_mm' (extrusion)
        resolution: Not used for chamfer (planar faces)

    Returns:
        Manifold3D mesh of triangular chamfer profile extruded
    """
    size = dims.get("size_mm", CHAMFER_DEFAULTS["size_mm"])
    length = dims.get("length_mm", CHAMFER_DEFAULTS["length_mm"])

    # Create right triangle cross-section
    profile_points = [
        [0, 0],
        [size, 0],
        [0, size],
        [0, 0]
    ]

    cross_section = m3d.CrossSection([np.array(profile_points)])
    chamfer = m3d.Manifold.extrude(cross_section, length)

    return chamfer


# ============================================================================
# SLOT - Rounded rectangle (stadium/obround) for milled slots
# ============================================================================

SLOT_SCHEMA = {
    "width_mm": {"type": "number", "min": 0.1, "max": 100, "default": 5.0},
    "length_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 20.0},
    "depth_mm": {"type": "number", "min": 0.1, "max": 100, "default": 5.0}
}

SLOT_DEFAULTS = {
    "width_mm": 5.0,
    "length_mm": 20.0,
    "depth_mm": 5.0
}

@primitive("slot", SLOT_SCHEMA, SLOT_DEFAULTS)
def create_slot(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a rounded slot (stadium/obround shape) for milled features.

    Args:
        dims: Dictionary with 'width_mm', 'length_mm', 'depth_mm'
        resolution: Number of segments for semicircular ends

    Returns:
        Manifold3D mesh of slot centered at origin
    """
    width = dims.get("width_mm", SLOT_DEFAULTS["width_mm"])
    length = dims.get("length_mm", SLOT_DEFAULTS["length_mm"])
    depth = dims.get("depth_mm", SLOT_DEFAULTS["depth_mm"])

    radius = width / 2
    straight_length = length - width  # Length of straight section

    if straight_length < 0:
        # If length < width, just make a circle
        circle = m3d.CrossSection.circle(radius, resolution)
        slot = m3d.Manifold.extrude(circle, depth)
    else:
        # Create stadium shape: rectangle + two semicircles
        half_res = resolution // 2

        # Left semicircle
        angles_left = np.linspace(np.pi / 2, 3 * np.pi / 2, half_res)
        points = []
        for angle in angles_left:
            x = -straight_length / 2 + radius * np.cos(angle)
            y = radius * np.sin(angle)
            points.append([x, y])

        # Right semicircle
        angles_right = np.linspace(-np.pi / 2, np.pi / 2, half_res)
        for angle in angles_right:
            x = straight_length / 2 + radius * np.cos(angle)
            y = radius * np.sin(angle)
            points.append([x, y])

        # Close the loop
        points.append(points[0])

        cross_section = m3d.CrossSection([np.array(points)])
        slot = m3d.Manifold.extrude(cross_section, depth)

    return slot


# ============================================================================
# COUNTERBORE - Stacked cylinders for recessed bolt heads
# ============================================================================

COUNTERBORE_SCHEMA = {
    "hole_diameter_mm": {"type": "number", "min": 0.1, "max": 50, "default": 3.0},
    "bore_diameter_mm": {"type": "number", "min": 0.1, "max": 100, "default": 6.0},
    "bore_depth_mm": {"type": "number", "min": 0.1, "max": 50, "default": 3.0},
    "total_depth_mm": {"type": "number", "min": 0.1, "max": 100, "default": 10.0}
}

COUNTERBORE_DEFAULTS = {
    "hole_diameter_mm": 3.0,
    "bore_diameter_mm": 6.0,
    "bore_depth_mm": 3.0,
    "total_depth_mm": 10.0
}

@primitive("counterbore", COUNTERBORE_SCHEMA, COUNTERBORE_DEFAULTS)
def create_counterbore(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a counterbored hole (stacked cylinders) for recessed fasteners.

    Args:
        dims: Dictionary with hole/bore diameters and depths
        resolution: Number of segments for circular cross-sections

    Returns:
        Manifold3D mesh of counterbore centered at origin, extending upward
    """
    hole_dia = dims.get("hole_diameter_mm", COUNTERBORE_DEFAULTS["hole_diameter_mm"])
    bore_dia = dims.get("bore_diameter_mm", COUNTERBORE_DEFAULTS["bore_diameter_mm"])
    bore_depth = dims.get("bore_depth_mm", COUNTERBORE_DEFAULTS["bore_depth_mm"])
    total_depth = dims.get("total_depth_mm", COUNTERBORE_DEFAULTS["total_depth_mm"])

    hole_radius = hole_dia / 2
    bore_radius = bore_dia / 2

    # Create through hole (full depth)
    hole = m3d.Manifold.cylinder(total_depth, hole_radius, hole_radius, resolution)

    # Create counterbore (only bore_depth)
    bore = m3d.Manifold.cylinder(bore_depth, bore_radius, bore_radius, resolution)

    # Position bore at top of hole
    bore = bore.translate([0, 0, total_depth - bore_depth])

    # Union the two cylinders
    counterbore = hole + bore

    return counterbore


# ============================================================================
# COUNTERSINK - Cone + cylinder for flat-head screws
# ============================================================================

COUNTERSINK_SCHEMA = {
    "hole_diameter_mm": {"type": "number", "min": 0.1, "max": 50, "default": 3.0},
    "sink_diameter_mm": {"type": "number", "min": 0.1, "max": 100, "default": 6.0},
    "sink_angle_degrees": {"type": "number", "min": 45, "max": 120, "default": 82},
    "total_depth_mm": {"type": "number", "min": 0.1, "max": 100, "default": 10.0}
}

COUNTERSINK_DEFAULTS = {
    "hole_diameter_mm": 3.0,
    "sink_diameter_mm": 6.0,
    "sink_angle_degrees": 82,
    "total_depth_mm": 10.0
}

@primitive("countersink", COUNTERSINK_SCHEMA, COUNTERSINK_DEFAULTS)
def create_countersink(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a countersunk hole (cone + cylinder) for flat-head fasteners.

    Args:
        dims: Dictionary with hole/sink diameters, angle, and depth
        resolution: Number of segments for circular cross-sections

    Returns:
        Manifold3D mesh of countersink centered at origin, extending upward
    """
    hole_dia = dims.get("hole_diameter_mm", COUNTERSINK_DEFAULTS["hole_diameter_mm"])
    sink_dia = dims.get("sink_diameter_mm", COUNTERSINK_DEFAULTS["sink_diameter_mm"])
    sink_angle = dims.get("sink_angle_degrees", COUNTERSINK_DEFAULTS["sink_angle_degrees"])
    total_depth = dims.get("total_depth_mm", COUNTERSINK_DEFAULTS["total_depth_mm"])

    hole_radius = hole_dia / 2
    sink_radius = sink_dia / 2

    # Calculate countersink depth based on angle
    # For a cone, depth = (radius_diff) / tan(half_angle)
    half_angle_rad = np.radians(sink_angle / 2)
    radius_diff = sink_radius - hole_radius
    sink_depth = radius_diff / np.tan(half_angle_rad)

    # Create through hole (full depth)
    hole = m3d.Manifold.cylinder(total_depth, hole_radius, hole_radius, resolution)

    # Create cone for countersink
    cone = m3d.Manifold.cylinder(sink_depth, sink_radius, hole_radius, resolution)

    # Position cone at top
    cone = cone.translate([0, 0, total_depth - sink_depth])

    # Union hole and cone
    countersink = hole + cone

    return countersink


# ============================================================================
# BOSS - Cylinder with optional filleted base
# ============================================================================

BOSS_SCHEMA = {
    "diameter_mm": {"type": "number", "min": 0.1, "max": 100, "default": 10.0},
    "height_mm": {"type": "number", "min": 0.1, "max": 100, "default": 5.0},
    "fillet_radius_mm": {"type": "number", "min": 0, "max": 50, "default": 0.5}
}

BOSS_DEFAULTS = {
    "diameter_mm": 10.0,
    "height_mm": 5.0,
    "fillet_radius_mm": 0.5
}

@primitive("boss", BOSS_SCHEMA, BOSS_DEFAULTS)
def create_boss(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a cylindrical boss with optional filleted base.

    Args:
        dims: Dictionary with 'diameter_mm', 'height_mm', 'fillet_radius_mm'
        resolution: Number of segments for circular cross-sections

    Returns:
        Manifold3D mesh of boss centered at origin, extending upward
    """
    diameter = dims.get("diameter_mm", BOSS_DEFAULTS["diameter_mm"])
    height = dims.get("height_mm", BOSS_DEFAULTS["height_mm"])
    fillet_radius = dims.get("fillet_radius_mm", BOSS_DEFAULTS["fillet_radius_mm"])

    radius = diameter / 2

    # Create main cylinder
    boss = m3d.Manifold.cylinder(height, radius, radius, resolution)

    # Add fillet at base if requested
    if fillet_radius > 0 and fillet_radius < radius:
        # Create torus segment for fillet
        # Torus major radius = boss radius - fillet radius
        # Torus minor radius = fillet radius
        major_radius = radius - fillet_radius
        minor_radius = fillet_radius

        # Create full torus
        torus = m3d.Manifold.revolve(
            m3d.CrossSection.circle(minor_radius, resolution // 4)
            .translate([major_radius, 0]),
            resolution
        )

        # Cut torus to keep only bottom quarter (fillet shape)
        # Keep the part below z=0
        cutter_box = m3d.Manifold.cube([diameter * 2, diameter * 2, fillet_radius * 2], True)
        cutter_box = cutter_box.translate([0, 0, -fillet_radius])

        fillet_ring = m3d.Manifold.batch_boolean([torus, cutter_box], m3d.OpType.Intersect)

        # Position fillet at base of boss
        fillet_ring = fillet_ring.translate([0, 0, fillet_radius])

        # Union with boss
        boss = boss + fillet_ring

    return boss


# ============================================================================
# RIB - Thin vertical wall for structural reinforcement
# ============================================================================

RIB_SCHEMA = {
    "height_mm": {"type": "number", "min": 0.1, "max": 100, "default": 10.0},
    "thickness_mm": {"type": "number", "min": 0.1, "max": 10, "default": 1.0},
    "length_mm": {"type": "number", "min": 0.1, "max": 1000, "default": 20.0}
}

RIB_DEFAULTS = {
    "height_mm": 10.0,
    "thickness_mm": 1.0,
    "length_mm": 20.0
}

@primitive("rib", RIB_SCHEMA, RIB_DEFAULTS)
def create_rib(dims: dict, resolution: int) -> m3d.Manifold:
    """Create a thin vertical rib for structural reinforcement.

    Args:
        dims: Dictionary with 'height_mm', 'thickness_mm', 'length_mm'
        resolution: Not used for rib (planar faces)

    Returns:
        Manifold3D mesh of rib centered at origin, oriented along X-axis
    """
    height = dims.get("height_mm", RIB_DEFAULTS["height_mm"])
    thickness = dims.get("thickness_mm", RIB_DEFAULTS["thickness_mm"])
    length = dims.get("length_mm", RIB_DEFAULTS["length_mm"])

    # Create thin vertical box
    # X = length, Y = thickness, Z = height
    rib = m3d.Manifold.cube([length, thickness, height], True)

    # Move so base is at z=0
    rib = rib.translate([0, 0, height / 2])

    return rib
