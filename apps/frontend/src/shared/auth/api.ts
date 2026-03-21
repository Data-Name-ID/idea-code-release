import type { AuthUser, TelegramWidgetUser } from './types'
import type { AuthResponse } from '@shared/types/api'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

// Fetch wrapper for endpoints returning raw JSON (no OkResponse envelope)
async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options?.headers ?? {}) },
    ...options,
  })
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }
  return response.json() as Promise<T>
}

// Fetch wrapper for endpoints returning OkResponse<T> envelope (Telegram login/config)
interface OkEnvelope<T> {
  status: string
  data: T | null
}

async function fetchOk<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options?.headers ?? {}) },
    ...options,
  })
  const body = (await response.json()) as OkEnvelope<T>
  if (!response.ok || body.status !== 'ok' || body.data === null) {
    throw new Error(`Request failed with status ${response.status}`)
  }
  return body.data
}

// ── Telegram ─────────────────────────────────────────────

interface TelegramConfig {
  bot_username: string
}

export async function fetchTelegramConfig(): Promise<TelegramConfig> {
  return fetchOk<TelegramConfig>('/api/auth/telegram/config')
}

export async function telegramLogin(payload: TelegramWidgetUser): Promise<AuthUser> {
  // Sets the JWT cookie; then fetch full profile from /api/auth/me
  await fetchOk('/api/auth/telegram/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  const user = await fetchCurrentUser()
  if (!user) throw new Error('Failed to load user after Telegram login')
  return user
}

// ── Email / password ──────────────────────────────────────

export async function loginWithPassword(email: string, password: string): Promise<AuthUser> {
  const { user } = await fetchJson<AuthResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
  return user
}

export async function registerWithPassword(
  username: string,
  name: string,
  email: string,
  password: string,
): Promise<AuthUser> {
  const { user } = await fetchJson<AuthResponse>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, name, email, password }),
  })
  return user
}

// ── Common ────────────────────────────────────────────────

// /api/auth/me returns UserResponse directly (no OkResponse wrapper)
export async function fetchCurrentUser(): Promise<AuthUser | null> {
  const response = await fetch(`${apiBaseUrl}/api/auth/me`, {
    method: 'GET',
    credentials: 'include',
  })
  if (response.status === 401) return null
  if (!response.ok) return null
  return response.json() as Promise<AuthUser>
}

export async function logout(): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/api/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }
}
