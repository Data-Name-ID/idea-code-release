<script setup lang="ts">
  import { computed, ref } from 'vue'
  import { useRouter } from 'vue-router'

  import { logout } from '@shared/auth/api'
  import { authState, clearCurrentUser } from '@shared/auth/session'

  const router = useRouter()
  const logoutPending = ref(false)

  const displayName = computed(() => {
    const user = authState.currentUser.value
    if (!user) {
      return null
    }
    if (user.username) {
      return `@${user.username}`
    }
    return [user.first_name, user.last_name].filter(Boolean).join(' ')
  })

  async function handleLogout(): Promise<void> {
    logoutPending.value = true
    try {
      await logout()
    } finally {
      clearCurrentUser()
      logoutPending.value = false
      await router.replace({ name: 'auth' })
    }
  }
</script>

<template>
  <div class="layout">
    <header class="header">
      <h1>Team Monorepo</h1>
      <nav class="header-nav">
        <RouterLink to="/"> Home </RouterLink>
        <RouterLink v-if="!authState.isAuthenticated.value" to="/auth"> Sign in </RouterLink>
        <span v-else-if="displayName" class="profile">{{ displayName }}</span>
        <button
          v-if="authState.isAuthenticated.value"
          type="button"
          class="logout-btn"
          :disabled="logoutPending"
          @click="handleLogout"
        >
          {{ logoutPending ? 'Signing out...' : 'Logout' }}
        </button>
      </nav>
    </header>

    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
  .layout {
    min-height: 100dvh;
    display: grid;
    grid-template-rows: auto 1fr;
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--color-border);
    background: var(--color-surface);
  }

  .header h1 {
    margin: 0;
    font-size: 1.1rem;
  }

  .header-nav {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .profile {
    color: var(--color-text-muted);
    font-size: 0.95rem;
  }

  .logout-btn {
    border: 1px solid var(--color-border);
    background: #ffffff;
    color: var(--color-text);
    border-radius: 0.5rem;
    padding: 0.35rem 0.7rem;
    cursor: pointer;
  }

  .logout-btn:disabled {
    opacity: 0.65;
    cursor: wait;
  }

  .content {
    padding: 1.5rem;
  }
</style>
