import { resolveMock } from '@shared/mocks/handler'
import type { OkResponse } from '@shared/types/api'
import { USE_MOCKS } from '@shared/config/env'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  if (USE_MOCKS) {
    return Promise.resolve(resolveMock<T>(path, options))
  }

  const isFormDataBody = options?.body instanceof FormData
  const headers = isFormDataBody
    ? { ...(options?.headers ?? {}) }
    : {
        'Content-Type': 'application/json',
        ...(options?.headers ?? {}),
      }

  const response = await fetch(`${apiBaseUrl}${path}`, {
    credentials: 'include',
    headers,
    ...options,
  })

  if (!response.ok) {
    let detail = ''
    try {
      const errBody = (await response.json()) as Record<string, unknown>
      if (typeof errBody.detail === 'string' && errBody.detail) detail = `: ${errBody.detail}`
    } catch {
      // ignore parse errors
    }
    throw new Error(`API ${response.status}${detail}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  const body = (await response.json()) as T | OkResponse<T>
  if (
    typeof body === 'object' &&
    body !== null &&
    'status' in body &&
    'data' in body &&
    typeof body.status === 'string'
  ) {
    const data = body.data
    if (data === null) {
      throw new Error('API response has empty data payload')
    }
    return data
  }

  return body as T
}

export function buildQuery(
  params: Record<string, string | number | boolean | undefined | null>,
): string {
  const entries = Object.entries(params).filter(([, v]) => v != null) as [
    string,
    string | number | boolean,
  ][]
  if (entries.length === 0) return ''
  return '?' + new URLSearchParams(entries.map(([k, v]) => [k, String(v)])).toString()
}
