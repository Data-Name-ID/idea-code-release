import { apiFetch } from '@shared/api/client'
import type { PaginatedResponse, RoleResponse } from '@shared/types/api'

export const roleApi = {
  getList: async (): Promise<RoleResponse[]> => {
    const response = await apiFetch<PaginatedResponse<RoleResponse> | RoleResponse[]>('/api/roles/')
    return Array.isArray(response) ? response : response.data
  },
}
