"""Transform utilities for manifold3d geometries."""

import manifold3d as m3d
import numpy as np


def translate(manifold: m3d.Manifold, x: float, y: float, z: float) -> m3d.Manifold:
    """
    Translate a manifold by the specified offsets.

    Args:
        manifold: The input manifold to translate
        x: Translation along x-axis
        y: Translation along y-axis
        z: Translation along z-axis

    Returns:
        Translated manifold
    """
    return manifold.translate([x, y, z])


def rotate(manifold: m3d.Manifold, angle: float, axis: str = 'z') -> m3d.Manifold:
    """
    Rotate a manifold around a specified axis.

    Args:
        manifold: The input manifold to rotate
        angle: Rotation angle in degrees
        axis: Rotation axis ('x', 'y', or 'z')

    Returns:
        Rotated manifold

    Raises:
        ValueError: If axis is not 'x', 'y', or 'z'
    """
    axis = axis.lower()
    if axis not in ['x', 'y', 'z']:
        raise ValueError(f"Invalid axis '{axis}'. Must be 'x', 'y', or 'z'")

    # Convert degrees to radians for rotation vector
    angle_rad = np.deg2rad(angle)

    # Create rotation vector [rx, ry, rz]
    rotation = [0.0, 0.0, 0.0]
    if axis == 'x':
        rotation[0] = angle_rad
    elif axis == 'y':
        rotation[1] = angle_rad
    else:  # axis == 'z'
        rotation[2] = angle_rad

    return manifold.rotate(rotation)


def scale(manifold: m3d.Manifold, sx: float, sy: float = None, sz: float = None) -> m3d.Manifold:
    """
    Scale a manifold along each axis.

    Args:
        manifold: The input manifold to scale
        sx: Scale factor along x-axis (or uniform scale if sy and sz are None)
        sy: Scale factor along y-axis (defaults to sx for uniform scaling)
        sz: Scale factor along z-axis (defaults to sx for uniform scaling)

    Returns:
        Scaled manifold
    """
    # Use uniform scaling if sy or sz not provided
    if sy is None:
        sy = sx
    if sz is None:
        sz = sx

    return manifold.scale([sx, sy, sz])


def mirror(manifold: m3d.Manifold, axis: str) -> m3d.Manifold:
    """
    Mirror a manifold across a plane perpendicular to the specified axis.

    Args:
        manifold: The input manifold to mirror
        axis: Axis perpendicular to mirror plane ('x', 'y', or 'z')

    Returns:
        Mirrored manifold

    Raises:
        ValueError: If axis is not 'x', 'y', or 'z'
    """
    axis = axis.lower()
    if axis not in ['x', 'y', 'z']:
        raise ValueError(f"Invalid axis '{axis}'. Must be 'x', 'y', or 'z'")

    # Create normal vector for mirror plane
    normal = [0.0, 0.0, 0.0]
    if axis == 'x':
        normal[0] = 1.0
    elif axis == 'y':
        normal[1] = 1.0
    else:  # axis == 'z'
        normal[2] = 1.0

    return manifold.mirror(normal)


def apply_transforms(manifold: m3d.Manifold, transforms: list[dict]) -> m3d.Manifold:
    """
    Apply a sequence of transforms to a manifold.

    Args:
        manifold: The input manifold to transform
        transforms: List of transform dictionaries, each with a 'type' key and relevant parameters
                   Supported types:
                   - {'type': 'translate', 'x': float, 'y': float, 'z': float}
                   - {'type': 'rotate', 'angle': float, 'axis': str}
                   - {'type': 'scale', 'sx': float, 'sy': float (optional), 'sz': float (optional)}
                   - {'type': 'mirror', 'axis': str}

    Returns:
        Transformed manifold

    Raises:
        ValueError: If transform type is unknown or required parameters are missing

    Example:
        >>> transforms = [
        ...     {'type': 'translate', 'x': 1, 'y': 2, 'z': 3},
        ...     {'type': 'rotate', 'angle': 45, 'axis': 'z'},
        ...     {'type': 'scale', 'sx': 2.0}
        ... ]
        >>> result = apply_transforms(manifold, transforms)
    """
    result = manifold

    for i, transform in enumerate(transforms):
        if not isinstance(transform, dict) or 'type' not in transform:
            raise ValueError(f"Transform at index {i} must be a dict with a 'type' key")

        transform_type = transform['type'].lower()

        if transform_type == 'translate':
            x = transform.get('x', 0.0)
            y = transform.get('y', 0.0)
            z = transform.get('z', 0.0)
            result = translate(result, x, y, z)

        elif transform_type == 'rotate':
            if 'angle' not in transform:
                raise ValueError(f"Rotate transform at index {i} requires 'angle' parameter")
            angle = transform['angle']
            axis = transform.get('axis', 'z')
            result = rotate(result, angle, axis)

        elif transform_type == 'scale':
            if 'sx' not in transform:
                raise ValueError(f"Scale transform at index {i} requires 'sx' parameter")
            sx = transform['sx']
            sy = transform.get('sy')
            sz = transform.get('sz')
            result = scale(result, sx, sy, sz)

        elif transform_type == 'mirror':
            if 'axis' not in transform:
                raise ValueError(f"Mirror transform at index {i} requires 'axis' parameter")
            axis = transform['axis']
            result = mirror(result, axis)

        else:
            raise ValueError(f"Unknown transform type '{transform_type}' at index {i}")

    return result
