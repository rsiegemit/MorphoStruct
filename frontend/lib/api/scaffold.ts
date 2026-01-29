import { apiRequest, apiBlobRequest } from './client';
import { ScaffoldType } from '../types/scaffold';

interface GenerateRequest {
  type: ScaffoldType;
  params: Record<string, any>;
  preview_only?: boolean;
}

interface MeshData {
  vertices: number[];
  indices: number[];
  normals?: number[];
}

interface ValidationResult {
  is_valid: boolean;
  is_printable: boolean;
  checks: Record<string, any>;
  warnings: string[];
  errors: string[];
}

interface GenerateResponse {
  success: boolean;
  scaffold_id: string;
  mesh: MeshData;
  stl_base64: string;
  stats: {
    triangle_count: number;
    volume_mm3: number;
    generation_time_ms: number;
  };
  validation: ValidationResult;
}

interface Preset {
  id: string;
  name: string;
  type: ScaffoldType;
  description: string;
  params: Record<string, any>;
}

interface PresetsResponse {
  presets: Preset[];
}

export async function generateScaffold(
  type: ScaffoldType,
  params: Record<string, any>,
  previewOnly = false
): Promise<GenerateResponse> {
  const endpoint = previewOnly ? '/api/preview' : '/api/generate';
  return apiRequest<GenerateResponse>(endpoint, {
    method: 'POST',
    body: JSON.stringify({ type, params, preview_only: previewOnly }),
  });
}

export async function previewScaffold(
  type: ScaffoldType,
  params: Record<string, any>
): Promise<GenerateResponse> {
  return generateScaffold(type, params, true);
}

export async function validateParams(
  type: ScaffoldType,
  params: Record<string, any>
): Promise<{ valid: boolean; errors: string[]; warnings: string[] }> {
  return apiRequest('/api/validate', {
    method: 'POST',
    body: JSON.stringify({ type, params }),
  });
}

export async function exportSTL(
  scaffoldId: string,
  format: 'binary' | 'ascii' = 'binary'
): Promise<Blob> {
  return apiBlobRequest(`/api/export/${scaffoldId}?format=${format}`);
}

export async function getPresets(): Promise<PresetsResponse> {
  return apiRequest<PresetsResponse>('/api/presets');
}

export async function getPreset(presetId: string): Promise<Preset> {
  return apiRequest<Preset>(`/api/presets/${presetId}`);
}

// Helper to trigger download
export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
