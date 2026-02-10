import { authFetch } from '../store/authStore';
import { ScaffoldType } from '../types/scaffolds';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface SavedScaffold {
  uuid: string;
  name: string;
  type: ScaffoldType;
  parameters: Record<string, any>;
  thumbnail_url?: string;
  created_at: string;
  updated_at: string;
  user_id: number;
}

// Raw response from backend may use scaffold_type instead of type (Pydantic alias)
interface RawSavedScaffold {
  uuid: string;
  name: string;
  type?: string;
  scaffold_type?: string;
  parameters: Record<string, any>;
  thumbnail_url?: string;
  created_at: string;
  updated_at: string;
  user_id: number;
}

export interface ListScaffoldsResponse {
  scaffolds: SavedScaffold[];
  total: number;
}

async function authApiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await authFetch(`${API_BASE}${endpoint}`, options);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const detail = errorData.detail;
    const message = typeof detail === 'string' ? detail : `HTTP error ${response.status}`;
    throw new Error(message);
  }

  return response.json();
}

/** Normalize backend scaffold response: backend may send scaffold_type or type */
function normalizeScaffold(raw: RawSavedScaffold): SavedScaffold {
  return {
    ...raw,
    type: (raw.type || raw.scaffold_type || 'unknown') as ScaffoldType,
  };
}

export async function listScaffolds(): Promise<ListScaffoldsResponse> {
  const result = await authApiRequest<{ scaffolds: RawSavedScaffold[]; total: number }>('/api/scaffolds');
  return {
    ...result,
    scaffolds: result.scaffolds.map(normalizeScaffold),
  };
}

export async function getScaffold(uuid: string): Promise<SavedScaffold> {
  const raw = await authApiRequest<RawSavedScaffold>(`/api/scaffolds/${uuid}`);
  return normalizeScaffold(raw);
}

export async function deleteScaffold(uuid: string): Promise<{ success: boolean }> {
  return authApiRequest<{ success: boolean }>(`/api/scaffolds/${uuid}`, {
    method: 'DELETE',
  });
}

export async function saveScaffold(
  name: string,
  scaffoldType: string,
  parameters: Record<string, any>
): Promise<SavedScaffold> {
  const raw = await authApiRequest<RawSavedScaffold>('/api/scaffolds', {
    method: 'POST',
    body: JSON.stringify({
      name,
      scaffold_type: scaffoldType,
      parameters,
    }),
  });
  return normalizeScaffold(raw);
}

export async function duplicateScaffold(uuid: string): Promise<SavedScaffold> {
  const raw = await authApiRequest<RawSavedScaffold>(`/api/scaffolds/${uuid}/duplicate`, {
    method: 'POST',
  });
  return normalizeScaffold(raw);
}
