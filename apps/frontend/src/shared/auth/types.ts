import type { UserResponse } from '@shared/types/api'

// Full user profile stored in the session after any successful auth
export type AuthUser = UserResponse

export interface TelegramWidgetUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}
