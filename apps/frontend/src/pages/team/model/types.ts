import type { EventRatingStatus } from '@shared/types/api'

export interface EventResult {
  id: number
  title: string
  date: string
  cover: string | null
  status: EventRatingStatus | null
}
