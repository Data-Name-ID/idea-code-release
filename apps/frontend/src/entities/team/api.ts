import { apiFetch, buildQuery } from '@shared/api/client'
import type {
  TeamResponse,
  TeamListResponse,
  TeamsListParams,
  TeamCreateRequest,
} from '@shared/types/api'

export const teamApi = {
  getList: (params?: TeamsListParams) =>
    apiFetch<TeamListResponse>(`/api/teams/${buildQuery(params ?? {})}`),

  getById: (id: number) => apiFetch<TeamResponse>(`/api/teams/${id}`),

  create: (payload: TeamCreateRequest) =>
    apiFetch<TeamResponse>('/api/teams/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
}
