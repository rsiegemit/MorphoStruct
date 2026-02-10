/**
 * API client for the manifold tiling endpoint.
 *
 * Tiles a previously generated scaffold onto a curved surface.
 */

import { apiRequest } from './client';
import { TileRequest, TileResponse } from '../types/tiling';

const DEFAULT_TILING_TIMEOUT_MS = 120000; // 2 minutes (tiling can be slow)

/**
 * Tile a scaffold onto a curved surface.
 *
 * @param request - Tiling parameters including scaffold_id from /api/generate
 * @param timeoutSeconds - Optional timeout override in seconds
 * @returns Tiled scaffold with mesh data and STL
 */
export async function tileScaffold(
  request: TileRequest,
  timeoutSeconds?: number,
): Promise<TileResponse> {
  const timeoutMs = timeoutSeconds
    ? timeoutSeconds * 1000
    : DEFAULT_TILING_TIMEOUT_MS;

  return apiRequest<TileResponse>('/api/tiling', {
    method: 'POST',
    body: JSON.stringify(request),
  }, timeoutMs);
}
