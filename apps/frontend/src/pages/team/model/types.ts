import type { EventRatingStatus } from '@shared/types/api'

export interface EventResult {
  id: number
  title: string
  date: string
  cover: string | null
  isVerified: boolean
  status: EventRatingStatus | null
}
