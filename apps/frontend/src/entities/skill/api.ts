import { apiFetch } from '@shared/api/client'
import type { SkillResponse } from '@shared/types/api'

export const skillApi = {
  getList: () => apiFetch<SkillResponse[]>('/api/skills/'),
}
