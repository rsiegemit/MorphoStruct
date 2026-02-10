"""
Primitive shape generation - COMPATIBILITY SHIM.

DEPRECATED: This module is now a compatibility shim. The actual implementation
has been moved to the primitives/ submodule with a registry-based architecture.

New code should import from:
    from backend.app.geometry.primitives import (
        get_primitive,
        list_primitives,
        get_schema,
        evaluate_csg_tree,
    )

This shim maintains backwards compatibility for existing imports.
"""

# Re-export everything from the new module for backwards compatibility
from .primitives import (
    # Registry functions (new API)
    get_primitive,
    list_primitives,
    get_schema,
    get_all_schemas,
    get_defaults,
    PrimitiveDefinition,
    PRIMITIVES,

    # Transform functions
    translate,
    rotate,
    scale,
    mirror,
    apply_transforms,

    # CSG tree evaluation
    evaluate_csg_tree,

    # Legacy API (backwards compatibility)
    PrimitiveParams,
    generate_primitive,
    generate_primitive_from_dict,
    MODIFICATIONS,
    apply_hole,
    apply_shell,
)

# For backwards compatibility, also create SHAPE_CREATORS from registry
def _make_shape_creators():
    """Create SHAPE_CREATORS dict from registry for backwards compatibility."""
    creators = {}
    for name in list_primitives():
        prim = get_primitive(name)
        creators[name] = prim.func
    return creators

# Lazy initialization to avoid import cycle
_shape_creators_cache = None

def _get_shape_creators():
    global _shape_creators_cache
    if _shape_creators_cache is None:
        _shape_creators_cache = _make_shape_creators()
    return _shape_creators_cache

# For imports that expect SHAPE_CREATORS dict
class _ShapeCreatorsProxy:
    """Proxy dict that lazily loads shape creators from registry."""
    def __getitem__(self, key):
        return _get_shape_creators()[key]
    def __contains__(self, key):
        return key in _get_shape_creators()
    def get(self, key, default=None):
        return _get_shape_creators().get(key, default)
    def keys(self):
        return _get_shape_creators().keys()
    def values(self):
        return _get_shape_creators().values()
    def items(self):
        return _get_shape_creators().items()
    def __iter__(self):
        return iter(_get_shape_creators())

SHAPE_CREATORS = _ShapeCreatorsProxy()

# Also export individual shape creators for direct imports
from .primitives.geometric import (
    create_cylinder,
    create_sphere,
    create_box,
    create_cone,
)

__all__ = [
    # New API
    'get_primitive',
    'list_primitives',
    'get_schema',
    'get_all_schemas',
    'get_defaults',
    'PrimitiveDefinition',
    'PRIMITIVES',
    'translate',
    'rotate',
    'scale',
    'mirror',
    'apply_transforms',
    'evaluate_csg_tree',
    # Legacy API
    'PrimitiveParams',
    'generate_primitive',
    'generate_primitive_from_dict',
    'SHAPE_CREATORS',
    'MODIFICATIONS',
    'apply_hole',
    'apply_shell',
    'create_cylinder',
    'create_sphere',
    'create_box',
    'create_cone',
]
