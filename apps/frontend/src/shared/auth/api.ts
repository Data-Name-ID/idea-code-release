import type { AuthUser, TelegramWidgetUser } from './types'

interface OkResponse<T> {
  status: string
  data: T | null
}

interface TelegramConfig {
  bot_username: string
}

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL ??
  import.meta.env.VITE_API_BASE_URL ??
  'http://localhost:8000'

async function parseResponse<T>(response: Response): Promise<T> {
  const body = (await response.json()) as OkResponse<T>
  if (!response.ok || body.status !== 'ok' || body.data === null) {
    const errorText = `Request failed with status ${response.status}`
    throw new Error(errorText)
  }
  return body.data
}

export async function fetchTelegramConfig(): Promise<TelegramConfig> {
  const response = await fetch(`${apiBaseUrl}/api/auth/telegram/config`, {
    method: 'GET',
    credentials: 'include',
  })
  return parseResponse<TelegramConfig>(response)
}

export async function telegramLogin(payload: TelegramWidgetUser): Promise<AuthUser> {
  const response = await fetch(`${apiBaseUrl}/api/auth/telegram/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(payload),
  })
  return parseResponse<AuthUser>(response)
}

export async function fetchCurrentUser(): Promise<AuthUser | null> {
  const response = await fetch(`${apiBaseUrl}/api/auth/me`, {
    method: 'GET',
    credentials: 'include',
  })
  if (response.status === 401) {
    return null
  }
  return parseResponse<AuthUser>(response)
}

export async function logout(): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/api/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!response.ok) {
    const errorText = `Request failed with status ${response.status}`
    throw new Error(errorText)
  }
}
