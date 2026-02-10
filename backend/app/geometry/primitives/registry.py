"""
Primitive registration system using decorator pattern.

This module provides a registry for geometric primitives, allowing them to be
registered with schemas and defaults, and retrieved by name.
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Any
import manifold3d as m3d


@dataclass
class PrimitiveDefinition:
    """Definition of a registered primitive.

    Attributes:
        name: The unique name of the primitive
        func: The function that creates the primitive geometry
        schema: JSON schema defining valid parameters
        defaults: Default parameter values
    """
    name: str
    func: Callable[[Dict[str, Any], int], m3d.Manifold]
    schema: Dict[str, Any]
    defaults: Dict[str, Any]


# Module-level registry
_PRIMITIVES: Dict[str, PrimitiveDefinition] = {}


def primitive(
    name: str,
    schema: Dict[str, Any],
    defaults: Optional[Dict[str, Any]] = None
) -> Callable:
    """Decorator to register a primitive function.

    Args:
        name: Unique name for the primitive
        schema: JSON schema defining valid parameters
        defaults: Optional default parameter values

    Returns:
        Decorator function that registers the primitive

    Example:
        @primitive("torus", TORUS_SCHEMA, TORUS_DEFAULTS)
        def create_torus(dims: dict, resolution: int) -> m3d.Manifold:
            ...
    """
    def decorator(func: Callable[[Dict[str, Any], int], m3d.Manifold]) -> Callable:
        """Inner decorator that performs the registration."""
        _PRIMITIVES[name] = PrimitiveDefinition(
            name=name,
            func=func,
            schema=schema,
            defaults=defaults or {}
        )
        return func
    return decorator


def get_primitive(name: str) -> PrimitiveDefinition:
    """Get a primitive definition by name.

    Args:
        name: The name of the primitive

    Returns:
        The PrimitiveDefinition for the requested primitive

    Raises:
        KeyError: If the primitive name is not registered
    """
    if name not in _PRIMITIVES:
        raise KeyError(
            f"Primitive '{name}' not found. "
            f"Available primitives: {', '.join(list_primitives())}"
        )
    return _PRIMITIVES[name]


def list_primitives() -> List[str]:
    """Get a list of all registered primitive names.

    Returns:
        Sorted list of primitive names
    """
    return sorted(_PRIMITIVES.keys())


def get_schema(name: str) -> Dict[str, Any]:
    """Get the JSON schema for a specific primitive.

    Args:
        name: The name of the primitive

    Returns:
        The JSON schema dict for the primitive

    Raises:
        KeyError: If the primitive name is not registered
    """
    return get_primitive(name).schema


def get_all_schemas() -> Dict[str, Dict[str, Any]]:
    """Get all primitive schemas indexed by name.

    Returns:
        Dictionary mapping primitive names to their schemas
    """
    return {name: defn.schema for name, defn in _PRIMITIVES.items()}


def get_defaults(name: str) -> Dict[str, Any]:
    """Get the default parameters for a specific primitive.

    Args:
        name: The name of the primitive

    Returns:
        The default parameters dict for the primitive

    Raises:
        KeyError: If the primitive name is not registered
    """
    return get_primitive(name).defaults


def clear_registry() -> None:
    """Clear all registered primitives.

    This is primarily useful for testing purposes.
    """
    _PRIMITIVES.clear()
