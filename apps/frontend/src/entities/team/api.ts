import { apiFetch, buildQuery } from '@shared/api/client'
import type {
  TeamCreateRequest,
  TeamInviteCreateRequest,
  TeamInviteCreateResponse,
  TeamJoinByInviteRequest,
  TeamListResponse,
  TeamResponse,
  TeamTransferCaptainRequest,
  TeamUpdateRequest,
  TeamsListParams,
} from '@shared/types/api'

export const teamApi = {
  getList: (params?: TeamsListParams) =>
    apiFetch<TeamListResponse>(`/api/teams/${buildQuery(params ?? {})}`),

  getById: (id: number) => apiFetch<TeamResponse>(`/api/teams/${id}`),

  create: (data: TeamCreateRequest) =>
    apiFetch<TeamResponse>('/api/teams/', { method: 'POST', body: JSON.stringify(data) }),

  update: (id: number, data: TeamUpdateRequest) =>
    apiFetch<TeamResponse>(`/api/teams/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  createInvite: (id: number, data?: TeamInviteCreateRequest) =>
    apiFetch<TeamInviteCreateResponse>(`/api/teams/${id}/invites`, {
      method: 'POST',
      body: JSON.stringify(data ?? {}),
    }),

  joinByInvite: (data: TeamJoinByInviteRequest) =>
    apiFetch<TeamResponse>('/api/teams/join-by-invite', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  removeMember: (teamId: number, userId: number) =>
    apiFetch<TeamResponse>(`/api/teams/${teamId}/members/${userId}`, { method: 'DELETE' }),

  transferCaptain: (teamId: number, data: TeamTransferCaptainRequest) =>
    apiFetch<TeamResponse>(`/api/teams/${teamId}/captain/transfer`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  leave: (teamId: number) => apiFetch<void>(`/api/teams/${teamId}/leave`, { method: 'POST' }),
}
