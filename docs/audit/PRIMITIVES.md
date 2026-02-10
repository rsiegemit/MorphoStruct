# PRIMITIVES Module Audit

**Category**: Geometric Primitives (Expanded)
**Total Primitives**: 27
**Status**: ✅ NEW - Registry-based architecture

## Overview

The primitives module has been expanded from 4 basic shapes to 27 primitives organized into 4 categories. The implementation uses a decorator-based registry pattern for easy extensibility and includes a CSG tree evaluator for future LLM-based composition.

## Primitive Categories

### Basic (4 primitives)
| Shape | Parameters | Description |
|-------|------------|-------------|
| `cylinder` | radius_mm, height_mm | Standard cylinder |
| `sphere` | radius_mm | Standard sphere |
| `box` | x_mm, y_mm, z_mm | Rectangular box |
| `cone` | bottom_radius_mm, top_radius_mm, height_mm | Cone/frustum |

### Geometric (8 primitives)
| Shape | Parameters | Description |
|-------|------------|-------------|
| `torus` | major_radius_mm, minor_radius_mm, arc_degrees | Donut shape via revolve |
| `capsule` | radius_mm, length_mm | Cylinder + 2 hemispheres |
| `pyramid` | base_x_mm, base_y_mm, height_mm | Four-sided pyramid |
| `wedge` | length_mm, width_mm, height_mm, angle_degrees | Angled wedge shape |
| `prism` | sides, radius_mm, height_mm | N-sided prism |
| `tube` | outer_radius_mm, inner_radius_mm, length_mm | Hollow cylinder |
| `ellipsoid` | radius_x_mm, radius_y_mm, radius_z_mm | Scaled sphere |
| `hemisphere` | radius_mm | Half sphere |

### Architectural (7 primitives)
| Shape | Parameters | Description |
|-------|------------|-------------|
| `fillet` | radius_mm, length_mm | Quarter-cylinder for edge rounding |
| `chamfer` | size_mm, length_mm | 45° bevel for corners |
| `slot` | width_mm, length_mm, depth_mm | Rounded rectangle (stadium) |
| `counterbore` | hole_diameter_mm, bore_diameter_mm, bore_depth_mm, total_depth_mm | Recessed bolt hole |
| `countersink` | hole_diameter_mm, sink_diameter_mm, sink_angle_degrees, total_depth_mm | Conical recess |
| `boss` | diameter_mm, height_mm, fillet_radius_mm | Raised cylinder with optional fillet |
| `rib` | height_mm, thickness_mm, length_mm | Thin structural wall |

### Organic/Bio (8 primitives)
| Shape | Parameters | Description |
|-------|------------|-------------|
| `branch` | start_radius_mm, end_radius_mm, length_mm | Tapered cylinder |
| `bifurcation` | parent_radius_mm, child_radius_mm, angle_degrees, length_mm | Y-junction |
| `pore` | diameter_mm, depth_mm | Cylinder for CSG subtract |
| `channel` | diameter_mm, length_mm | Through-hole cylinder |
| `fiber` | diameter_mm, length_mm, crimp_amplitude_mm, crimp_wavelength_mm | Sinusoidal fiber |
| `membrane` | thickness_mm, radius_mm, curvature | Thin curved sheet |
| `lattice_cell` | cell_size_mm, strut_diameter_mm | Cubic unit cell |
| `pore_array` | pore_size_mm, spacing_mm, count_x, count_y, depth_mm | Grid of pores |

## Backend Architecture

| File | Purpose |
|------|---------|
| `backend/app/geometry/primitives/registry.py` | `@primitive` decorator and registry functions |
| `backend/app/geometry/primitives/transforms.py` | translate, rotate, scale, mirror |
| `backend/app/geometry/primitives/csg.py` | CSG tree evaluation for LLM composition |
| `backend/app/geometry/primitives/geometric.py` | 12 geometric primitives |
| `backend/app/geometry/primitives/architectural.py` | 7 architectural primitives |
| `backend/app/geometry/primitives/organic.py` | 8 organic/bio primitives |
| `backend/app/geometry/primitives/__init__.py` | Module exports + backwards compatibility |
| `backend/app/geometry/primitives.py` | Compatibility shim (delegates to new module) |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/primitives/list` | GET | List all 27 primitive names |
| `/api/primitives/schema` | GET | Get all schemas with categories |
| `/api/primitives/schema/{name}` | GET | Get schema for specific primitive |

## Frontend Integration

| File | Purpose |
|------|---------|
| `frontend/lib/types/scaffolds/base.ts` | `PrimitiveShape` enum (27 values) |
| `frontend/lib/parameterMeta/primitives.ts` | Dimension metadata for all 27 shapes |
| `frontend/lib/parameterMeta/legacy.ts` | PRIMITIVE_META with 27-shape dropdown |

## CSG Tree Structure

The CSG evaluator supports JSON trees for LLM-based composition:

```json
{
  "op": "difference",
  "children": [
    {"primitive": "box", "dims": {"x_mm": 10, "y_mm": 10, "z_mm": 10}},
    {"primitive": "cylinder", "dims": {"radius_mm": 3, "height_mm": 12},
     "transforms": [{"type": "translate", "z": -1}]}
  ]
}
```

**Supported Operations**: `union`, `difference`, `intersection`

**Supported Transforms**: `translate`, `rotate`, `scale`, `mirror`

## Modification Operations

| Operation | Parameters | Effect |
|-----------|------------|--------|
| `hole` | diameter_mm, axis | Through-hole |
| `shell` | wall_thickness_mm | Hollow out |
| `fillet_edges` | radius_mm | Round edges (NEW) |
| `chamfer_edges` | size_mm | Bevel edges (NEW) |
| `taper` | factor | Linear scale along axis (NEW) |
| `twist` | angle_degrees | Rotation along axis (NEW) |

## Test Coverage

Unit tests in `backend/tests/test_primitives.py`:
- Registry functions (get_primitive, list_primitives, get_schema)
- All 27 primitives generate valid manifold with volume > 0
- Transform functions work correctly
- CSG tree evaluation (union, difference, intersection)
- Legacy API backwards compatibility

## Statistics

| Metric | Value |
|--------|-------|
| Total Primitives | 27 |
| New Primitives | 23 |
| Backend Files | 8 |
| API Endpoints | 3 |
| Test Count | 48 |
