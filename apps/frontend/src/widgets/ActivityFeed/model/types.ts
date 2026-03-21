import type { EventResponse, EventRatingStatus } from '@shared/types/api'

export interface ActivityItem {
  event: EventResponse
  status: EventRatingStatus | null
  teamName: string | null
}

export type ActivityFilter = 'all' | 'hackathon' | 'win'
