import { computed, ref } from 'vue'

import { fetchCurrentUser } from './api'
import type { AuthUser } from './types'

const currentUser = ref<AuthUser | null>(null)
const initialized = ref(false)
let bootstrapPromise: Promise<void> | null = null

async function bootstrapSessionInternal(): Promise<void> {
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
