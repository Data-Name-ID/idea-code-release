import { apiFetch, buildQuery } from '@shared/api/client'
import type {
  ParticipationApplicationCreateRequest,
  ParticipationApplicationListParams,
  ParticipationApplicationListResponse,
  ParticipationApplicationResponse,
  ParticipationApplicationStatusUpdateRequest,
} from '@shared/types/api'

export const participationApplicationApi = {
  getList: (params?: ParticipationApplicationListParams) =>
    apiFetch<ParticipationApplicationListResponse>(
      `/api/participation-applications/${buildQuery(params ?? {})}`,
    ),

  create: (payload: ParticipationApplicationCreateRequest) =>
    apiFetch<ParticipationApplicationResponse>('/api/participation-applications/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updateStatus: (id: number, payload: ParticipationApplicationStatusUpdateRequest) =>
    apiFetch<ParticipationApplicationResponse>(`/api/participation-applications/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
}
