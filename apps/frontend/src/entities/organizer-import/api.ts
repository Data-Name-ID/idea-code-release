import { apiFetch } from '@shared/api/client'
import type { OrganizerImportRequest, OrganizerImportResponse } from '@shared/types/api'

export const organizerImportApi = {
  importData: (payload: OrganizerImportRequest, apiKey: string) =>
    apiFetch<OrganizerImportResponse>('/api/public/organizer/import', {
      method: 'POST',
      headers: {
        'X-API-Key': apiKey,
      },
      body: JSON.stringify(payload),
    }),
}
