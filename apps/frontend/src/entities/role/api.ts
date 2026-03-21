import { apiFetch } from '@shared/api/client'
import type { RoleResponse } from '@shared/types/api'

export const roleApi = {
  getList: () => apiFetch<RoleResponse[]>('/api/roles/'),
}
