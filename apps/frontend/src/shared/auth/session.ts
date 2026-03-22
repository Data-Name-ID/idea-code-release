import { computed, ref } from 'vue'

import { fetchCurrentUser } from './api'
import { MOCK_AUTH_USER } from './mock'
import type { AuthUser } from './types'

const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true'

const currentUser = ref<AuthUser | null>(null)
const initialized = ref(false)
let bootstrapPromise: Promise<void> | null = null

async function bootstrapSessionInternal(): Promise<void> {
  if (USE_MOCKS) {
    currentUser.value = MOCK_AUTH_USER
    initialized.value = true
    return
  }
  try {
    currentUser.value = await fetchCurrentUser()
  } catch {
    currentUser.value = null
  } finally {
    initialized.value = true
  }
}

export function ensureSessionInitialized(): Promise<void> {
  if (initialized.value) {
    return Promise.resolve()
  }
  if (bootstrapPromise === null) {
    bootstrapPromise = bootstrapSessionInternal().finally(() => {
      bootstrapPromise = null
    })
  }
  return bootstrapPromise
}

export function setCurrentUser(user: AuthUser | null): void {
  currentUser.value = user
  initialized.value = true
}

export function clearCurrentUser(): void {
  currentUser.value = null
  initialized.value = true
}

export const authState = {
  currentUser,
  initialized: computed(() => initialized.value),
  isAuthenticated: computed(() => currentUser.value !== null),
}
