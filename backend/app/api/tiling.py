"""
Tiling API endpoint.

POST /api/tiling - Tile a scaffold onto a curved surface.

This is a post-processing modifier: the user first generates a scaffold
via /api/generate, then tiles it onto a surface via this endpoint using
the scaffold_id from the generation response.
"""

import asyncio
import time
import uuid
from typing import Dict, Any, Optional, List, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator

from app.config import get_settings
from app.core.logging import get_logger
from app.geometry.stl_export import (
    manifold_to_mesh_dict,
    manifold_to_stl_binary,
    get_bounding_box,
    stl_to_base64,
)
from app.geometry.tiling import (
    tile_scaffold_onto_surface,
    TilingParams,
    TilingMode,
    TargetShape,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["tiling"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class TileRequest(BaseModel):
    """Request to tile a scaffold onto a curved surface."""

    scaffold_id: str = Field(
        description="ID of a previously generated scaffold (from /api/generate response)"
    )

    # Target surface
    target_shape: Literal["sphere", "ellipsoid", "torus", "cylinder", "superellipsoid"] = Field(
        default="sphere",
        description="Target surface shape",
    )

    # Shape dimensions
    radius: float = Field(default=10.0, gt=0, le=500, description="Sphere/cylinder radius (mm)")
    radius_x: float = Field(default=10.0, gt=0, le=500, description="Ellipsoid/superellipsoid X semi-axis (mm)")
    radius_y: float = Field(default=8.0, gt=0, le=500, description="Ellipsoid/superellipsoid Y semi-axis (mm)")
    radius_z: float = Field(default=6.0, gt=0, le=500, description="Ellipsoid/superellipsoid Z semi-axis (mm)")
    major_radius: float = Field(default=15.0, gt=0, le=500, description="Torus major radius (mm)")
    minor_radius: float = Field(default=5.0, gt=0, le=500, description="Torus minor radius (mm)")
    height: float = Field(default=20.0, gt=0, le=500, description="Cylinder height (mm)")
    exponent_n: float = Field(default=1.0, gt=0.05, le=4.0, description="Superellipsoid vertical roundness")
    exponent_e: float = Field(default=1.0, gt=0.05, le=4.0, description="Superellipsoid horizontal roundness")

    # Tiling layout
    mode: Literal["surface", "volume"] = Field(
        default="surface",
        description="surface = shell on surface, volume = fill with layers",
    )
    num_tiles_u: int = Field(default=4, ge=1, le=20, description="Tiles in U direction")
    num_tiles_v: int = Field(default=4, ge=1, le=20, description="Tiles in V direction")

    # Volume mode
    num_layers: int = Field(default=1, ge=1, le=10, description="Radial layers (volume mode)")
    layer_spacing_mm: float = Field(default=1.0, gt=0, le=50, description="Layer spacing (mm)")

    # Mesh quality
    refine_edge_length_mm: float = Field(
        default=0.5, gt=0, le=10,
        description="Target edge length before warping (mm). Smaller = smoother.",
    )

    @model_validator(mode="after")
    def validate_torus_radii(self):
        if self.target_shape == "torus" and self.minor_radius >= self.major_radius:
            raise ValueError("minor_radius must be less than major_radius for a valid torus")
        return self


class TileMeshResponse(BaseModel):
    """Mesh data in tiling response."""
    vertices: List[float]
    indices: List[int]
    normals: List[float]


class TileStatsResponse(BaseModel):
    """Statistics about the tiled scaffold."""
    triangle_count: int
    volume_mm3: float
    generation_time_ms: float
    target_shape: str
    tiling_mode: str
    num_tiles_u: int
    num_tiles_v: int
    total_patches: int


class TileResponse(BaseModel):
    """Response with tiled scaffold."""
    success: bool
    scaffold_id: str = Field(description="New scaffold ID for the tiled result")
    mesh: TileMeshResponse
    stl_base64: str
    stats: TileStatsResponse
    bounding_box: Dict[str, List[float]]


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/tiling", response_model=TileResponse)
async def tile_scaffold(request: TileRequest) -> TileResponse:
    """
    Tile a previously generated scaffold onto a curved surface.

    Workflow:
        1. Retrieve source scaffold from cache by scaffold_id
        2. Build tiling parameters
        3. Run tiling (flat tile -> refine -> UV normalise -> warp)
        4. Return tiled mesh + STL
    """
    settings = get_settings()
    timeout_seconds = settings.generation_timeout_seconds

    from app.cache import cache_scaffold, get_scaffold, has_scaffold

    # 1. Retrieve source scaffold
    if not has_scaffold(request.scaffold_id):
        raise HTTPException(
            status_code=404,
            detail="Scaffold not found. Generate it first with POST /api/generate.",
        )

    source_manifold, _stl_bytes, _metadata = get_scaffold(request.scaffold_id)

    # 2. Build tiling params
    tiling_params = TilingParams(
        target_shape=TargetShape(request.target_shape),
        mode=TilingMode(request.mode),
        radius=request.radius,
        radius_x=request.radius_x,
        radius_y=request.radius_y,
        radius_z=request.radius_z,
        major_radius=request.major_radius,
        minor_radius=request.minor_radius,
        height=request.height,
        exponent_n=request.exponent_n,
        exponent_e=request.exponent_e,
        num_tiles_u=request.num_tiles_u,
        num_tiles_v=request.num_tiles_v,
        num_layers=request.num_layers,
        layer_spacing_mm=request.layer_spacing_mm,
        refine_edge_length_mm=request.refine_edge_length_mm,
    )

    # 3. Run tiling with timeout
    start_time = time.time()
    try:
        tiled_manifold, tiling_stats = await asyncio.wait_for(
            asyncio.to_thread(tile_scaffold_onto_surface, source_manifold, tiling_params),
            timeout=timeout_seconds,
        )
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        logger.error(f"Tiling timed out after {elapsed:.1f}s (limit: {timeout_seconds}s)")
        raise HTTPException(
            status_code=408,
            detail=f"Tiling timed out after {timeout_seconds}s. Try fewer tiles or larger edge length.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Tiling failed: {e}")
        raise HTTPException(status_code=500, detail=f"Tiling failed: {str(e)}")

    generation_time_ms = (time.time() - start_time) * 1000
    logger.info(f"Tiling completed in {generation_time_ms:.0f}ms")

    # 4. Convert to response format
    mesh_dict = manifold_to_mesh_dict(tiled_manifold)
    bbox_min, bbox_max = get_bounding_box(tiled_manifold)
    stl_bytes = manifold_to_stl_binary(tiled_manifold)
    stl_b64 = stl_to_base64(stl_bytes)

    # Cache the tiled result
    tiled_id = str(uuid.uuid4())
    cache_scaffold(
        tiled_id,
        tiled_manifold,
        stl_bytes,
        {
            "type": "tiled_scaffold",
            "source_scaffold_id": request.scaffold_id,
            "tiling_params": {
                "target_shape": request.target_shape,
                "mode": request.mode,
                "num_tiles_u": request.num_tiles_u,
                "num_tiles_v": request.num_tiles_v,
            },
        },
    )

    return TileResponse(
        success=True,
        scaffold_id=tiled_id,
        mesh=TileMeshResponse(
            vertices=mesh_dict["vertices"],
            indices=mesh_dict["indices"],
            normals=mesh_dict["normals"],
        ),
        stl_base64=stl_b64,
        stats=TileStatsResponse(
            triangle_count=mesh_dict["triangle_count"],
            volume_mm3=tiling_stats.get("volume_mm3", 0.0),
            generation_time_ms=generation_time_ms,
            target_shape=tiling_stats.get("target_shape", request.target_shape),
            tiling_mode=tiling_stats.get("tiling_mode", request.mode),
            num_tiles_u=tiling_stats.get("num_tiles_u", request.num_tiles_u),
            num_tiles_v=tiling_stats.get("num_tiles_v", request.num_tiles_v),
            total_patches=tiling_stats.get("total_patches", request.num_tiles_u * request.num_tiles_v),
        ),
        bounding_box={
            "min": list(bbox_min),
            "max": list(bbox_max),
        },
    )
