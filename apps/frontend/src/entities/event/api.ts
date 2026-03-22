import { apiFetch, buildQuery } from '@shared/api/client'
import type {
  EventResponse,
  EventListResponse,
  EventRatingResponse,
  EventRatingStatus,
} from '@shared/types/api'

export const eventApi = {
  getList: (params?: { limit?: number; offset?: number }) =>
    apiFetch<EventListResponse>(`/api/events/${buildQuery(params ?? {})}`),

  getById: (id: number) => apiFetch<EventResponse>(`/api/events/${id}`),

  getRatings: (eventId: number, status?: EventRatingStatus) =>
    apiFetch<EventRatingResponse>(
      `/api/events/${eventId}/ratings${buildQuery({ status: status ?? null })}`,
    ),
}
