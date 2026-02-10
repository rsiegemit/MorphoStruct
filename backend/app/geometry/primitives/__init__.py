"""
Primitives module for geometric primitive generation.

This module provides a registry-based system for creating geometric primitives
that can be used standalone or composed via CSG trees.

Usage:
    from backend.app.geometry.primitives import (
        get_primitive,
        list_primitives,
        get_schema,
        get_all_schemas,
        evaluate_csg_tree,
        apply_transforms,
    )

    # Create a primitive
    torus_def = get_primitive("torus")
    manifold = torus_def.func({"major_radius_mm": 10, "minor_radius_mm": 2}, resolution=32)

    # Or use CSG tree
    tree = {
        "op": "difference",
        "children": [
            {"primitive": "box", "dims": {"x_mm": 10, "y_mm": 10, "z_mm": 10}},
            {"primitive": "cylinder", "dims": {"radius_mm": 3, "height_mm": 12}}
        ]
    }
    result = evaluate_csg_tree(tree)
"""

# Import submodules to register all primitives
from . import geometric
from . import architectural
from . import organic

# Import and re-export registry functions
from .registry import (
    get_primitive,
    list_primitives,
    get_schema,
    get_all_schemas,
    get_defaults,
    PrimitiveDefinition,
    _PRIMITIVES as PRIMITIVES,
)

# Import and re-export transform functions
from .transforms import (
    translate,
    rotate,
    scale,
    mirror,
    apply_transforms,
)

# Import and re-export CSG tree evaluation
from .csg import evaluate_csg_tree

# Backwards compatibility functions
import manifold3d as m3d
from dataclasses import dataclass, field
from typing import Literal, Optional

@dataclass
class PrimitiveParams:
    """Legacy dataclass for backwards compatibility."""
    shape: str = 'cylinder'
    dimensions: dict = field(default_factory=lambda: {'radius_mm': 5.0, 'height_mm': 10.0})
    modifications: list[dict] = field(default_factory=list)
    resolution: int = 32

# Legacy modifications (hole, shell) - keep for backwards compatibility
def apply_hole(manifold: m3d.Manifold, params: dict, resolution: int) -> m3d.Manifold:
    """Create a cylindrical hole through the manifold."""
    import numpy as np
    diameter = params.get('diameter_mm', 2.0)
    axis = params.get('axis', 'z')
    radius = diameter / 2

    mesh = manifold.to_mesh()
    verts = np.array(mesh.vert_properties)[:, :3]
    min_bounds = verts.min(axis=0)
    max_bounds = verts.max(axis=0)
    center = (min_bounds + max_bounds) / 2

    if axis == 'z':
        depth = (max_bounds[2] - min_bounds[2]) + 0.2
        hole = m3d.Manifold.cylinder(depth, radius, radius, resolution)
        hole = hole.translate([center[0], center[1], min_bounds[2] - 0.1])
    elif axis == 'y':
        depth = (max_bounds[1] - min_bounds[1]) + 0.2
        hole = m3d.Manifold.cylinder(depth, radius, radius, resolution)
        hole = hole.rotate([90, 0, 0]).translate([center[0], min_bounds[1] - 0.1, center[2]])
    else:  # x
        depth = (max_bounds[0] - min_bounds[0]) + 0.2
        hole = m3d.Manifold.cylinder(depth, radius, radius, resolution)
        hole = hole.rotate([0, 90, 0]).translate([min_bounds[0] - 0.1, center[1], center[2]])

    return manifold - hole

def apply_shell(manifold: m3d.Manifold, params: dict, resolution: int) -> m3d.Manifold:
    """Hollow out the manifold with given wall thickness."""
    import numpy as np
    thickness = params.get('wall_thickness_mm', 1.0)

    mesh = manifold.to_mesh()
    verts = np.array(mesh.vert_properties)[:, :3]
    min_bounds = verts.min(axis=0)
    max_bounds = verts.max(axis=0)
    size = max_bounds - min_bounds
    center = (min_bounds + max_bounds) / 2

    scale_factors = []
    for i, s in enumerate(size):
        if s > 2 * thickness:
            scale_factors.append((s - 2 * thickness) / s)
        else:
            scale_factors.append(0.5)

    inner = manifold.translate([-center[0], -center[1], -center[2]])
    inner = inner.scale([scale_factors[0], scale_factors[1], scale_factors[2]])
    inner = inner.translate([center[0], center[1], center[2]])

    return manifold - inner

MODIFICATIONS = {
    'hole': apply_hole,
    'shell': apply_shell
}

# Legacy shape creator functions (for backwards compatibility)
def create_cylinder(dims: dict, resolution: int) -> m3d.Manifold:
    """Create cylinder using registry."""
    return get_primitive('cylinder').func(dims, resolution)

def create_sphere(dims: dict, resolution: int) -> m3d.Manifold:
    """Create sphere using registry."""
    return get_primitive('sphere').func(dims, resolution)

def create_box(dims: dict, resolution: int) -> m3d.Manifold:
    """Create box using registry."""
    return get_primitive('box').func(dims, resolution)

def create_cone(dims: dict, resolution: int) -> m3d.Manifold:
    """Create cone using registry."""
    return get_primitive('cone').func(dims, resolution)

SHAPE_CREATORS = {
    'cylinder': create_cylinder,
    'sphere': create_sphere,
    'box': create_box,
    'cone': create_cone,
}

def generate_primitive(params: PrimitiveParams) -> tuple[m3d.Manifold, dict]:
    """Generate a primitive shape with optional modifications (legacy API)."""
    primitive_def = get_primitive(params.shape)
    manifold = primitive_def.func(params.dimensions, params.resolution)

    for mod in params.modifications:
        operation = mod.get('operation')
        mod_params = mod.get('params', {})
        if operation in MODIFICATIONS:
            manifold = MODIFICATIONS[operation](manifold, mod_params, params.resolution)
        else:
            raise ValueError(f"Unknown modification: {operation}")

    mesh = manifold.to_mesh()
    volume = manifold.volume() if hasattr(manifold, 'volume') else 0

    stats = {
        'triangle_count': len(mesh.tri_verts) // 3 if hasattr(mesh, 'tri_verts') else 0,
        'volume_mm3': volume,
        'shape': params.shape,
        'modification_count': len(params.modifications),
        'scaffold_type': 'primitive'
    }

    return manifold, stats

def generate_primitive_from_dict(params: dict) -> tuple[m3d.Manifold, dict]:
    """Generate a primitive from dict params (legacy API)."""
    return generate_primitive(PrimitiveParams(
        shape=params.get('shape', 'cylinder'),
        dimensions=params.get('dimensions', {}),
        modifications=params.get('modifications', []),
        resolution=params.get('resolution', 32)
    ))

# Export all public names
__all__ = [
    # Registry
    'get_primitive',
    'list_primitives',
    'get_schema',
    'get_all_schemas',
    'get_defaults',
    'PrimitiveDefinition',
    'PRIMITIVES',
    # Transforms
    'translate',
    'rotate',
    'scale',
    'mirror',
    'apply_transforms',
    # CSG
    'evaluate_csg_tree',
    # Legacy compatibility
    'PrimitiveParams',
    'generate_primitive',
    'generate_primitive_from_dict',
    'MODIFICATIONS',
    'apply_hole',
    'apply_shell',
    'create_cylinder',
    'create_sphere',
    'create_box',
    'create_cone',
    'SHAPE_CREATORS',
]
