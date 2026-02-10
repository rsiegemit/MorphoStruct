"""CSG (Constructive Solid Geometry) tree evaluation for composing primitives.

This module provides functionality to evaluate CSG trees represented as nested
dictionaries, enabling LLM-generated geometric compositions using boolean operations.

Example Usage:
    >>> from backend.app.geometry.primitives.csg import evaluate_csg_tree
    >>>
    >>> # Create a box with a cylindrical hole
    >>> tree = {
    ...     "op": "difference",
    ...     "children": [
    ...         {
    ...             "primitive": "box",
    ...             "dims": {"x": 10, "y": 10, "z": 10}
    ...         },
    ...         {
    ...             "primitive": "cylinder",
    ...             "dims": {"radius": 3, "height": 12},
    ...             "transforms": [{"type": "translate", "z": -1}]
    ...         }
    ...     ]
    ... }
    >>> result = evaluate_csg_tree(tree, resolution=32)
    >>>
    >>> # Complex nested operations
    >>> complex_tree = {
    ...     "op": "union",
    ...     "children": [
    ...         {"primitive": "sphere", "dims": {"radius": 5}},
    ...         {
    ...             "op": "difference",
    ...             "children": [
    ...                 {"primitive": "box", "dims": {"x": 6, "y": 6, "z": 6}},
    ...                 {"primitive": "sphere", "dims": {"radius": 4}}
    ...             ],
    ...             "transforms": [{"type": "translate", "x": 8}]
    ...         }
    ...     ]
    ... }
    >>> result = evaluate_csg_tree(complex_tree)
"""

from typing import Any, Dict, List, TypedDict, Union, Optional
import manifold3d as m3d

from .registry import get_primitive
from .transforms import apply_transforms


class TransformDict(TypedDict, total=False):
    """Transform specification in CSG tree.

    Attributes:
        type: Transform type ('translate', 'rotate', 'scale')
        x: X-axis parameter (translation/scale)
        y: Y-axis parameter (translation/scale)
        z: Z-axis parameter (translation/scale)
        angle: Rotation angle in degrees
        axis: Rotation axis ('x', 'y', 'z')
    """
    type: str
    x: float
    y: float
    z: float
    angle: float
    axis: str


class PrimitiveNode(TypedDict, total=False):
    """Leaf node representing a primitive geometry.

    Attributes:
        primitive: Name of the primitive (e.g., 'box', 'sphere', 'cylinder')
        dims: Dictionary of dimension parameters for the primitive
        transforms: Optional list of transforms to apply to the primitive
    """
    primitive: str
    dims: Dict[str, Any]
    transforms: List[TransformDict]


class OperationNode(TypedDict, total=False):
    """Internal node representing a CSG operation.

    Attributes:
        op: Boolean operation ('union', 'difference', 'intersection')
        children: List of child nodes (can be primitives or operations)
        transforms: Optional list of transforms to apply after the operation
    """
    op: str
    children: List[Union['PrimitiveNode', 'OperationNode']]
    transforms: List[TransformDict]


CSGNode = Union[PrimitiveNode, OperationNode]


def evaluate_csg_tree(tree: CSGNode, resolution: int = 32) -> m3d.Manifold:
    """Evaluate a CSG tree to produce a Manifold3D mesh.

    Recursively processes a CSG tree structure, creating primitives at leaf nodes
    and applying boolean operations at internal nodes. Supports transforms at any
    level of the tree hierarchy.

    Args:
        tree: CSG tree node (either primitive or operation)
        resolution: Resolution parameter for circular primitives (default: 32)

    Returns:
        Manifold3D mesh representing the evaluated CSG tree

    Raises:
        ValueError: If tree structure is invalid or unsupported operation specified
        KeyError: If required keys are missing from tree nodes

    Example:
        >>> # Simple primitive
        >>> sphere_tree = {
        ...     "primitive": "sphere",
        ...     "dims": {"radius": 5}
        ... }
        >>> mesh = evaluate_csg_tree(sphere_tree)
        >>>
        >>> # Boolean operation
        >>> union_tree = {
        ...     "op": "union",
        ...     "children": [
        ...         {"primitive": "box", "dims": {"x": 10, "y": 10, "z": 10}},
        ...         {"primitive": "sphere", "dims": {"radius": 7}}
        ...     ]
        ... }
        >>> mesh = evaluate_csg_tree(union_tree)
    """
    # Handle primitive (leaf) nodes
    if "primitive" in tree:
        primitive_name = tree["primitive"]
        dims = tree.get("dims", {})

        # Get primitive definition from registry
        primitive_def = get_primitive(primitive_name)

        # Merge defaults with provided dims (provided dims take precedence)
        merged_dims = {**primitive_def.defaults, **dims}

        # Create primitive mesh
        mesh = primitive_def.func(merged_dims, resolution)

        # Apply transforms if specified
        if "transforms" in tree:
            mesh = apply_transforms(mesh, tree["transforms"])

        return mesh

    # Handle operation (internal) nodes
    elif "op" in tree:
        operation = tree["op"]
        children = tree.get("children", [])

        if not children:
            raise ValueError(f"Operation node '{operation}' has no children")

        if len(children) < 2:
            raise ValueError(f"Operation '{operation}' requires at least 2 children, got {len(children)}")

        # Recursively evaluate all children
        child_meshes = [evaluate_csg_tree(child, resolution) for child in children]

        # Apply boolean operation
        result = _apply_operation(operation, child_meshes)

        # Apply transforms if specified
        if "transforms" in tree:
            result = apply_transforms(result, tree["transforms"])

        return result

    else:
        raise ValueError(
            "Invalid CSG tree node: must contain either 'primitive' or 'op' key. "
            f"Got keys: {list(tree.keys())}"
        )


def _apply_operation(operation: str, meshes: List[m3d.Manifold]) -> m3d.Manifold:
    """Apply a boolean operation to a list of meshes.

    Args:
        operation: CSG operation ('union', 'difference', 'intersection')
        meshes: List of Manifold3D meshes (must contain at least 2)

    Returns:
        Result of applying the operation to all meshes

    Raises:
        ValueError: If operation is not supported
    """
    if operation == "union":
        result = meshes[0]
        for mesh in meshes[1:]:
            result = result + mesh
        return result

    elif operation == "difference":
        result = meshes[0]
        for mesh in meshes[1:]:
            result = result - mesh
        return result

    elif operation == "intersection":
        result = meshes[0]
        for mesh in meshes[1:]:
            result = m3d.Manifold.batch_boolean([result, mesh], m3d.OpType.Intersect)
        return result

    else:
        raise ValueError(
            f"Unsupported CSG operation: '{operation}'. "
            f"Supported operations: 'union', 'difference', 'intersection'"
        )
