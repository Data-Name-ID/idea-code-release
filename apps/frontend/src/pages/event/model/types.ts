import type { EventRatingStatus } from '@shared/types/api'

export interface TeamRatingEntry {
  kind: 'team'
  id: number
  status: EventRatingStatus
  name: string
  memberCount: number
  members: Array<{ name: string; avatar: string | null; roles: string }>
}

export interface SoloRatingEntry {
  kind: 'solo'
  id: number
  status: EventRatingStatus
  name: string
  avatar: string | null
  roles: string
}

export type RatingEntry = TeamRatingEntry | SoloRatingEntry
