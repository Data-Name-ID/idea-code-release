import { apiFetch, buildQuery } from '@shared/api/client'
import type {
  UserResponse,
  UserListResponse,
  UserCreateRequest,
  UserUpdateRequest,
  UsersListParams,
} from '@shared/types/api'

export const userApi = {
  getList: (params?: UsersListParams) =>
    apiFetch<UserListResponse>(`/api/users/${buildQuery(params ?? {})}`),

  getById: (id: number) => apiFetch<UserResponse>(`/api/users/${id}`),

  create: (data: UserCreateRequest) =>
    apiFetch<UserResponse>('/api/users/', { method: 'POST', body: JSON.stringify(data) }),

  update: (id: number, data: UserUpdateRequest) =>
    apiFetch<UserResponse>(`/api/users/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  remove: (id: number) => apiFetch<void>(`/api/users/${id}`, { method: 'DELETE' }),

  getMe: () => apiFetch<UserResponse>('/api/auth/me'),

  uploadAvatar: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return apiFetch<UserResponse>('/api/users/me/avatar', { method: 'POST', body: form })
  },
}
