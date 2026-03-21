export interface AuthUser {
  id: number
  telegram_user_id: number
  username: string | null
  first_name: string
  last_name: string | null
  photo_url: string | null
}

export interface TelegramWidgetUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}
