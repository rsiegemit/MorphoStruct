/**
 * Types for the manifold tiling system.
 *
 * Tiling maps scaffold patches onto curved 3D surfaces
 * (sphere, ellipsoid, torus, cylinder).
 */

export type TargetShape = 'sphere' | 'ellipsoid' | 'torus' | 'cylinder' | 'superellipsoid';

export type TilingMode = 'surface' | 'volume';

export interface TileRequest {
  scaffold_id: string;

  // Target surface
  target_shape: TargetShape;

  // Shape dimensions
  radius?: number;
  radius_x?: number;
  radius_y?: number;
  radius_z?: number;
  major_radius?: number;
  minor_radius?: number;
  height?: number;
  exponent_n?: number;
  exponent_e?: number;

  // Tiling layout
  mode?: TilingMode;
  num_tiles_u?: number;
  num_tiles_v?: number;

  // Volume mode
  num_layers?: number;
  layer_spacing_mm?: number;

  // Mesh quality
  refine_edge_length_mm?: number;
}

export interface TileMeshData {
  vertices: number[];
  indices: number[];
  normals: number[];
}

export interface TileStats {
  triangle_count: number;
  volume_mm3: number;
  generation_time_ms: number;
  target_shape: string;
  tiling_mode: string;
  num_tiles_u: number;
  num_tiles_v: number;
  total_patches: number;
}

export interface TileResponse {
  success: boolean;
  scaffold_id: string;
  mesh: TileMeshData;
  stl_base64: string;
  stats: TileStats;
  bounding_box: {
    min: number[];
    max: number[];
  };
}
