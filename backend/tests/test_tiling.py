"""
Tests for the manifold tiling module.

Verifies that scaffolds can be tiled onto curved surfaces
(sphere, ellipsoid, torus, cylinder) with correct geometry.
"""

import sys
import os
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import manifold3d as m3d

from app.geometry.tiling import (
    tile_scaffold_onto_surface,
    TilingParams,
    TilingMode,
    TargetShape,
)
from app.geometry.tiling.surfaces import (
    SphereParams,
    EllipsoidParams,
    TorusParams,
    CylinderParams,
    SuperellipsoidParams,
    make_sphere_warp,
    make_ellipsoid_warp,
    make_torus_warp,
    make_cylinder_warp,
    make_superellipsoid_warp,
    sphere_normals,
)
from app.geometry.stl_export import manifold_to_stl_binary, manifold_to_mesh_dict


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def box_scaffold():
    """Simple box scaffold for testing."""
    return m3d.Manifold.cube([2, 2, 0.5], True)


@pytest.fixture
def tube_scaffold():
    """Hollow tube scaffold."""
    outer = m3d.Manifold.cylinder(3.0, 1.5, 1.5, circular_segments=12)
    inner = m3d.Manifold.cylinder(3.2, 1.0, 1.0, circular_segments=12).translate([0, 0, -0.1])
    return outer - inner


# ---------------------------------------------------------------------------
# Surface warp function tests
# ---------------------------------------------------------------------------

class TestSphereWarp:
    def test_maps_equator(self):
        """Points at v=pi/2 should be at the equator (z~0)."""
        warp = make_sphere_warp(SphereParams(radius=10.0))
        verts = np.array([[0.0, np.pi / 2, 0.0]])
        result = warp(verts)
        assert abs(result[0, 2]) < 0.01  # z should be near 0 at equator

    def test_radius_preserved(self):
        """Surface points should be at distance radius from origin."""
        warp = make_sphere_warp(SphereParams(radius=10.0))
        verts = np.array([
            [0.0, np.pi / 2, 0.0],
            [np.pi, np.pi / 4, 0.0],
            [np.pi / 2, np.pi / 3, 0.0],
        ])
        result = warp(verts)
        distances = np.linalg.norm(result, axis=1)
        np.testing.assert_allclose(distances, 10.0, atol=0.01)

    def test_thickness_offset(self):
        """Points with z > 0 should be further from origin."""
        warp = make_sphere_warp(SphereParams(radius=10.0))
        on_surface = np.array([[1.0, 1.5, 0.0]])
        offset = np.array([[1.0, 1.5, 2.0]])
        r_surface = np.linalg.norm(warp(on_surface))
        r_offset = np.linalg.norm(warp(offset))
        assert r_offset > r_surface


class TestEllipsoidWarp:
    def test_non_uniform_radii(self):
        """Ellipsoid should have different extents along each axis."""
        warp = make_ellipsoid_warp(EllipsoidParams(radius_x=10.0, radius_y=5.0, radius_z=3.0))
        # Point along x-axis (u=0, v=pi/2, z=0)
        verts_x = np.array([[0.0, np.pi / 2, 0.0]])
        # Point along y-axis (u=pi/2, v=pi/2, z=0)
        verts_y = np.array([[np.pi / 2, np.pi / 2, 0.0]])
        result_x = warp(verts_x)
        result_y = warp(verts_y)
        assert abs(result_x[0, 0]) > abs(result_y[0, 1])  # x extent > y extent


class TestTorusWarp:
    def test_center_hole(self):
        """Torus should have a hole in the center."""
        warp = make_torus_warp(TorusParams(major_radius=15.0, minor_radius=5.0))
        verts = np.array([[0.0, 0.0, 0.0]])
        result = warp(verts)
        distance_from_z = np.sqrt(result[0, 0] ** 2 + result[0, 1] ** 2)
        assert distance_from_z > 10.0  # should be at R + r = 20


class TestCylinderWarp:
    def test_height_maps_linearly(self):
        """v parameter should map linearly to z coordinate."""
        warp = make_cylinder_warp(CylinderParams(radius=10.0, height=20.0))
        verts = np.array([
            [0.0, 0.0, 0.0],
            [0.0, 10.0, 0.0],
            [0.0, 20.0, 0.0],
        ])
        result = warp(verts)
        np.testing.assert_allclose(result[:, 2], [0.0, 10.0, 20.0], atol=0.01)


class TestSphereNormals:
    def test_unit_length(self):
        """Surface normals should have unit length."""
        u = np.array([0.0, np.pi / 2, np.pi, 3 * np.pi / 2])
        v = np.array([np.pi / 4, np.pi / 2, 3 * np.pi / 4, np.pi / 4])
        normals = sphere_normals(u, v)
        lengths = np.linalg.norm(normals, axis=1)
        np.testing.assert_allclose(lengths, 1.0, atol=1e-10)


# ---------------------------------------------------------------------------
# Core tiling tests
# ---------------------------------------------------------------------------

class TestTileOntoSphere:
    def test_basic_sphere_tiling(self, box_scaffold):
        """Box scaffold should tile onto a sphere."""
        params = TilingParams(
            target_shape=TargetShape.SPHERE,
            radius=10.0,
            num_tiles_u=3,
            num_tiles_v=3,
            refine_edge_length_mm=1.0,
        )
        result, stats = tile_scaffold_onto_surface(box_scaffold, params)
        assert stats["triangle_count"] > 0
        assert stats["volume_mm3"] > 0
        assert stats["target_shape"] == "sphere"
        assert stats["total_patches"] == 9

    def test_result_is_roughly_spherical(self, box_scaffold):
        """Tiled result should be bounded within sphere radius + scaffold thickness."""
        params = TilingParams(
            target_shape=TargetShape.SPHERE,
            radius=10.0,
            num_tiles_u=4,
            num_tiles_v=4,
            refine_edge_length_mm=1.0,
        )
        result, _ = tile_scaffold_onto_surface(box_scaffold, params)
        mesh = result.to_mesh()
        verts = np.array(mesh.vert_properties)[:, :3]
        distances = np.linalg.norm(verts, axis=1)
        # All vertices should be within radius + scaffold height
        assert distances.max() < 12.0  # 10 + some tolerance


class TestTileOntoEllipsoid:
    def test_basic_ellipsoid_tiling(self, box_scaffold):
        params = TilingParams(
            target_shape=TargetShape.ELLIPSOID,
            radius_x=12.0,
            radius_y=8.0,
            radius_z=6.0,
            num_tiles_u=3,
            num_tiles_v=3,
            refine_edge_length_mm=1.0,
        )
        result, stats = tile_scaffold_onto_surface(box_scaffold, params)
        assert stats["triangle_count"] > 0
        assert stats["target_shape"] == "ellipsoid"


class TestTileOntoTorus:
    def test_basic_torus_tiling(self, box_scaffold):
        params = TilingParams(
            target_shape=TargetShape.TORUS,
            major_radius=15.0,
            minor_radius=5.0,
            num_tiles_u=3,
            num_tiles_v=3,
            refine_edge_length_mm=1.0,
        )
        result, stats = tile_scaffold_onto_surface(box_scaffold, params)
        assert stats["triangle_count"] > 0
        assert stats["target_shape"] == "torus"


class TestTileOntoCylinder:
    def test_basic_cylinder_tiling(self, box_scaffold):
        params = TilingParams(
            target_shape=TargetShape.CYLINDER,
            radius=10.0,
            height=20.0,
            num_tiles_u=3,
            num_tiles_v=3,
            refine_edge_length_mm=1.0,
        )
        result, stats = tile_scaffold_onto_surface(box_scaffold, params)
        assert stats["triangle_count"] > 0
        assert stats["target_shape"] == "cylinder"


class TestVolumeFilling:
    def test_volume_mode_creates_more_geometry(self, box_scaffold):
        """Volume mode with multiple layers should produce more triangles."""
        surface_params = TilingParams(
            target_shape=TargetShape.SPHERE,
            radius=10.0,
            mode=TilingMode.SURFACE,
            num_tiles_u=3,
            num_tiles_v=3,
            refine_edge_length_mm=1.0,
        )
        volume_params = TilingParams(
            target_shape=TargetShape.SPHERE,
            radius=10.0,
            mode=TilingMode.VOLUME,
            num_tiles_u=3,
            num_tiles_v=3,
            num_layers=2,
            layer_spacing_mm=1.0,
            refine_edge_length_mm=1.0,
        )

        _, surface_stats = tile_scaffold_onto_surface(box_scaffold, surface_params)
        _, volume_stats = tile_scaffold_onto_surface(box_scaffold, volume_params)

        assert volume_stats["triangle_count"] > surface_stats["triangle_count"]
        assert volume_stats["num_layers"] == 2


class TestSTLExport:
    def test_stl_export_produces_valid_binary(self, box_scaffold):
        """Tiled result should export to valid binary STL."""
        params = TilingParams(
            target_shape=TargetShape.SPHERE,
            radius=10.0,
            num_tiles_u=2,
            num_tiles_v=2,
            refine_edge_length_mm=1.0,
        )
        result, _ = tile_scaffold_onto_surface(box_scaffold, params)
        stl_bytes = manifold_to_stl_binary(result)
        assert len(stl_bytes) > 84  # header (80) + count (4) + at least 1 triangle

    def test_mesh_dict_has_valid_structure(self, box_scaffold):
        """Mesh dict should have vertices, indices, normals."""
        params = TilingParams(
            target_shape=TargetShape.SPHERE,
            radius=10.0,
            num_tiles_u=2,
            num_tiles_v=2,
            refine_edge_length_mm=1.0,
        )
        result, _ = tile_scaffold_onto_surface(box_scaffold, params)
        mesh_dict = manifold_to_mesh_dict(result)
        assert len(mesh_dict["vertices"]) > 0
        assert len(mesh_dict["indices"]) > 0
        assert len(mesh_dict["normals"]) > 0
        assert mesh_dict["triangle_count"] > 0
        assert mesh_dict["vertex_count"] == mesh_dict["triangle_count"] * 3


class TestInputValidation:
    def test_rejects_zero_tiles(self, box_scaffold):
        params = TilingParams(num_tiles_u=0, num_tiles_v=3)
        with pytest.raises(ValueError, match="num_tiles"):
            tile_scaffold_onto_surface(box_scaffold, params)

    def test_rejects_zero_layers_in_volume_mode(self, box_scaffold):
        params = TilingParams(
            mode=TilingMode.VOLUME,
            num_layers=0,
        )
        with pytest.raises(ValueError, match="num_layers"):
            tile_scaffold_onto_surface(box_scaffold, params)


class TestSuperellipsoidWarp:
    def test_reduces_to_ellipsoid(self):
        """With n=e=1, superellipsoid should match ellipsoid."""
        se_warp = make_superellipsoid_warp(SuperellipsoidParams(
            radius_x=10.0, radius_y=8.0, radius_z=6.0,
            exponent_n=1.0, exponent_e=1.0,
        ))
        e_warp = make_ellipsoid_warp(EllipsoidParams(
            radius_x=10.0, radius_y=8.0, radius_z=6.0,
        ))
        verts = np.array([
            [0.5, np.pi / 2, 0.0],
            [np.pi, np.pi / 3, 0.0],
        ])
        se_result = se_warp(verts)
        e_result = e_warp(verts)
        np.testing.assert_allclose(se_result, e_result, atol=0.1)

    def test_exponents_change_shape(self):
        """Different exponents should produce different shapes."""
        round_warp = make_superellipsoid_warp(SuperellipsoidParams(
            radius_x=10.0, radius_y=10.0, radius_z=10.0,
            exponent_n=1.0, exponent_e=1.0,
        ))
        boxy_warp = make_superellipsoid_warp(SuperellipsoidParams(
            radius_x=10.0, radius_y=10.0, radius_z=10.0,
            exponent_n=0.3, exponent_e=0.3,
        ))
        verts = np.array([[np.pi / 4, np.pi / 4, 0.0]])
        round_result = round_warp(verts)
        boxy_result = boxy_warp(verts)
        # Boxy shape should have larger coordinates at 45 degrees
        round_dist = np.linalg.norm(round_result)
        boxy_dist = np.linalg.norm(boxy_result)
        assert boxy_dist > round_dist


class TestTileOntoSuperellipsoid:
    def test_basic_superellipsoid_tiling(self, box_scaffold):
        params = TilingParams(
            target_shape=TargetShape.SUPERELLIPSOID,
            radius_x=10.0,
            radius_y=8.0,
            radius_z=6.0,
            exponent_n=0.5,
            exponent_e=0.5,
            num_tiles_u=3,
            num_tiles_v=3,
            refine_edge_length_mm=1.0,
        )
        result, stats = tile_scaffold_onto_surface(box_scaffold, params)
        assert stats["triangle_count"] > 0
        assert stats["target_shape"] == "superellipsoid"


class TestSharedCache:
    def test_cache_and_retrieve(self):
        """Cache module should store and retrieve scaffolds."""
        from app.cache import cache_scaffold, get_scaffold, has_scaffold
        test_id = "test-cache-id"
        manifold = m3d.Manifold.cube([1, 1, 1])
        cache_scaffold(test_id, manifold, b"stl-data", {"type": "test"})
        assert has_scaffold(test_id)
        result = get_scaffold(test_id)
        assert result is not None
        assert result[1] == b"stl-data"
        assert result[2]["type"] == "test"

    def test_cache_miss_returns_none(self):
        from app.cache import get_scaffold, has_scaffold
        assert not has_scaffold("nonexistent-id")
        assert get_scaffold("nonexistent-id") is None


class TestComplexScaffold:
    def test_tube_on_ellipsoid(self, tube_scaffold):
        """Hollow tube should tile cleanly onto an ellipsoid."""
        params = TilingParams(
            target_shape=TargetShape.ELLIPSOID,
            radius_x=15.0,
            radius_y=10.0,
            radius_z=8.0,
            num_tiles_u=4,
            num_tiles_v=3,
            refine_edge_length_mm=1.0,
        )
        result, stats = tile_scaffold_onto_surface(tube_scaffold, params)
        assert stats["triangle_count"] > 0
        assert stats["volume_mm3"] > 0
