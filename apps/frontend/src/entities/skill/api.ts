import { apiFetch } from '@shared/api/client'
import type { PaginatedResponse, SkillResponse } from '@shared/types/api'

export const skillApi = {
  getList: async (): Promise<SkillResponse[]> => {
    const response = await apiFetch<PaginatedResponse<SkillResponse> | SkillResponse[]>('/api/skills/')
    return Array.isArray(response) ? response : response.data
  },
}
