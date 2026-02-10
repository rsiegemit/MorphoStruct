"""
Surface warp functions for manifold tiling.

Each surface type provides a vectorized warp function that maps
flat (x, y, z) scaffold coordinates to curved surface coordinates.

All warp functions accept and return numpy arrays of shape [n, 3]
for use with manifold3d's warp_batch().
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Tuple


# ---------------------------------------------------------------------------
# Surface parameter dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SphereParams:
    """Sphere surface parameters."""
    radius: float = 10.0


@dataclass(frozen=True)
class EllipsoidParams:
    """Ellipsoid surface parameters (semi-axes a, b, c)."""
    radius_x: float = 10.0
    radius_y: float = 8.0
    radius_z: float = 6.0


@dataclass(frozen=True)
class TorusParams:
    """Torus surface parameters."""
    major_radius: float = 15.0
    minor_radius: float = 5.0


@dataclass(frozen=True)
class CylinderParams:
    """Cylinder surface parameters."""
    radius: float = 10.0
    height: float = 20.0


@dataclass(frozen=True)
class SuperellipsoidParams:
    """
    Superellipsoid surface parameters.

    A superellipsoid generalises the ellipsoid with two exponents
    that control roundness (n) and squareness (e).

    n=e=1  -> standard ellipsoid
    n<1    -> more "pinched" at poles
    n>1    -> more "boxy" vertically
    e<1    -> more "pinched" at meridians
    e>1    -> more "boxy" horizontally

    Useful shapes:
        n=0.5, e=0.5 -> pillow/bean
        n=2, e=2     -> rounded cube
        n=1, e=0.3   -> star-cross section
    """
    radius_x: float = 10.0
    radius_y: float = 8.0
    radius_z: float = 6.0
    exponent_n: float = 1.0  # vertical roundness
    exponent_e: float = 1.0  # horizontal roundness


# ---------------------------------------------------------------------------
# Parametric bounds for each surface type
# Returns ((u_min, u_max), (v_min, v_max))
# ---------------------------------------------------------------------------

def sphere_parametric_bounds(
    num_tiles_v: int = 4,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    Sphere: u = azimuthal [0, 2pi], v = polar [eps, pi-eps].

    Epsilon scales with tile count so that high-tile-count tiling
    covers more of the sphere while low counts stay safe from poles.
    """
    eps = max(0.01, 0.15 / num_tiles_v)
    return ((0.0, 2.0 * np.pi), (eps, np.pi - eps))


def ellipsoid_parametric_bounds(
    num_tiles_v: int = 4,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Same parametrization as sphere with adaptive pole avoidance."""
    eps = max(0.01, 0.15 / num_tiles_v)
    return ((0.0, 2.0 * np.pi), (eps, np.pi - eps))


def torus_parametric_bounds() -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Torus: u = major circle [0, 2pi], v = minor circle [0, 2pi]."""
    return ((0.0, 2.0 * np.pi), (0.0, 2.0 * np.pi))


def cylinder_parametric_bounds(height: float) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Cylinder: u = angle [0, 2pi], v = height [0, h]."""
    return ((0.0, 2.0 * np.pi), (0.0, height))


def superellipsoid_parametric_bounds(
    num_tiles_v: int = 4,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Superellipsoid: same parametric range as sphere/ellipsoid."""
    eps = max(0.01, 0.15 / num_tiles_v)
    return ((0.0, 2.0 * np.pi), (eps, np.pi - eps))


# ---------------------------------------------------------------------------
# Surface normal functions (vectorized)
# Each returns normals array [n, 3] given parametric coords u, v
# ---------------------------------------------------------------------------

def sphere_normals(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Outward unit normals on a sphere."""
    nx = np.sin(v) * np.cos(u)
    ny = np.sin(v) * np.sin(u)
    nz = np.cos(v)
    return np.column_stack([nx, ny, nz])


def ellipsoid_normals(
    u: np.ndarray, v: np.ndarray,
    rx: float, ry: float, rz: float
) -> np.ndarray:
    """Outward unit normals on an ellipsoid (gradient of implicit surface)."""
    nx = np.sin(v) * np.cos(u) / (rx * rx)
    ny = np.sin(v) * np.sin(u) / (ry * ry)
    nz = np.cos(v) / (rz * rz)
    norm = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    norm = np.where(norm < 1e-12, 1.0, norm)
    return np.column_stack([nx / norm, ny / norm, nz / norm])


def torus_normals(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Outward unit normals on a torus."""
    nx = np.cos(v) * np.cos(u)
    ny = np.cos(v) * np.sin(u)
    nz = np.sin(v)
    return np.column_stack([nx, ny, nz])


def cylinder_normals(u: np.ndarray, _v: np.ndarray) -> np.ndarray:
    """Outward unit normals on a cylinder (radial direction)."""
    nx = np.cos(u)
    ny = np.sin(u)
    nz = np.zeros_like(u)
    return np.column_stack([nx, ny, nz])


def _signed_power(base: np.ndarray, exp: float) -> np.ndarray:
    """Compute sign(base) * |base|^exp, safe for zero values."""
    return np.sign(base) * np.power(np.abs(base) + 1e-30, exp)


def superellipsoid_normals(
    u: np.ndarray, v: np.ndarray,
    rx: float, ry: float, rz: float,
    n: float, e: float,
) -> np.ndarray:
    """
    Outward unit normals on a superellipsoid.

    Derived from the gradient of the implicit surface equation.
    """
    nx = _signed_power(np.sin(v), 2.0 - n) * _signed_power(np.cos(u), 2.0 - e) / rx
    ny = _signed_power(np.sin(v), 2.0 - n) * _signed_power(np.sin(u), 2.0 - e) / ry
    nz = _signed_power(np.cos(v), 2.0 - n) / rz
    norm = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    norm = np.where(norm < 1e-12, 1.0, norm)
    return np.column_stack([nx / norm, ny / norm, nz / norm])


# ---------------------------------------------------------------------------
# Warp function builders
# Each returns a callable (verts: ndarray[n,3]) -> ndarray[n,3]
# that maps flat scaffold coordinates to the curved surface.
#
# The flat scaffold is expected to be in normalised UV space:
#   x -> u parameter
#   y -> v parameter
#   z -> thickness (offset along surface normal)
# ---------------------------------------------------------------------------

def make_sphere_warp(params: SphereParams):
    """
    Build warp function for sphere surface.

    Mapping:
        x -> u (azimuthal angle)
        y -> v (polar angle)
        z -> radial offset along surface normal
    """
    r = params.radius

    def warp(verts: np.ndarray) -> np.ndarray:
        u = verts[:, 0]
        v = verts[:, 1]
        z = verts[:, 2]

        # Surface point at radius r
        sx = r * np.sin(v) * np.cos(u)
        sy = r * np.sin(v) * np.sin(u)
        sz = r * np.cos(v)

        # Offset along normal (normal = radial direction on sphere)
        normals = sphere_normals(u, v)
        x_out = sx + normals[:, 0] * z
        y_out = sy + normals[:, 1] * z
        z_out = sz + normals[:, 2] * z

        return np.column_stack([x_out, y_out, z_out])

    return warp


def make_ellipsoid_warp(params: EllipsoidParams):
    """
    Build warp function for ellipsoid surface.

    Same parametrization as sphere but with non-uniform radii.
    """
    rx, ry, rz = params.radius_x, params.radius_y, params.radius_z

    def warp(verts: np.ndarray) -> np.ndarray:
        u = verts[:, 0]
        v = verts[:, 1]
        z = verts[:, 2]

        # Surface point on ellipsoid
        sx = rx * np.sin(v) * np.cos(u)
        sy = ry * np.sin(v) * np.sin(u)
        sz = rz * np.cos(v)

        # Offset along ellipsoid normal
        normals = ellipsoid_normals(u, v, rx, ry, rz)
        x_out = sx + normals[:, 0] * z
        y_out = sy + normals[:, 1] * z
        z_out = sz + normals[:, 2] * z

        return np.column_stack([x_out, y_out, z_out])

    return warp


def make_torus_warp(params: TorusParams):
    """
    Build warp function for torus surface.

    Mapping:
        x -> u (major circle angle)
        y -> v (minor circle angle)
        z -> offset along torus normal
    """
    R = params.major_radius
    r = params.minor_radius

    def warp(verts: np.ndarray) -> np.ndarray:
        u = verts[:, 0]
        v = verts[:, 1]
        z = verts[:, 2]

        # Surface point on torus
        sx = (R + r * np.cos(v)) * np.cos(u)
        sy = (R + r * np.cos(v)) * np.sin(u)
        sz = r * np.sin(v)

        # Offset along normal
        normals = torus_normals(u, v)
        x_out = sx + normals[:, 0] * z
        y_out = sy + normals[:, 1] * z
        z_out = sz + normals[:, 2] * z

        return np.column_stack([x_out, y_out, z_out])

    return warp


def make_cylinder_warp(params: CylinderParams):
    """
    Build warp function for cylinder surface.

    Mapping:
        x -> u (angle around circumference)
        y -> v (height along axis)
        z -> radial offset from surface
    """
    r = params.radius

    def warp(verts: np.ndarray) -> np.ndarray:
        u = verts[:, 0]
        v = verts[:, 1]
        z = verts[:, 2]

        # Surface point on cylinder
        sx = r * np.cos(u)
        sy = r * np.sin(u)
        sz = v  # height maps directly

        # Offset along radial normal
        normals = cylinder_normals(u, v)
        x_out = sx + normals[:, 0] * z
        y_out = sy + normals[:, 1] * z
        z_out = sz + normals[:, 2] * z

        return np.column_stack([x_out, y_out, z_out])

    return warp


def make_superellipsoid_warp(params: SuperellipsoidParams):
    """
    Build warp function for superellipsoid surface.

    Generalises the ellipsoid with exponents n (vertical) and e (horizontal).
    Uses the same spherical parametrization (u=azimuthal, v=polar).
    """
    rx, ry, rz = params.radius_x, params.radius_y, params.radius_z
    n, e = params.exponent_n, params.exponent_e

    def warp(verts: np.ndarray) -> np.ndarray:
        u = verts[:, 0]
        v = verts[:, 1]
        z = verts[:, 2]

        # Surface point on superellipsoid
        sx = rx * _signed_power(np.sin(v), n) * _signed_power(np.cos(u), e)
        sy = ry * _signed_power(np.sin(v), n) * _signed_power(np.sin(u), e)
        sz = rz * _signed_power(np.cos(v), n)

        # Offset along surface normal
        normals = superellipsoid_normals(u, v, rx, ry, rz, n, e)
        x_out = sx + normals[:, 0] * z
        y_out = sy + normals[:, 1] * z
        z_out = sz + normals[:, 2] * z

        return np.column_stack([x_out, y_out, z_out])

    return warp
