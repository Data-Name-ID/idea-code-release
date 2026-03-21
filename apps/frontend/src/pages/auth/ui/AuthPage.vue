<script setup lang="ts">
  import { computed, onMounted, onUnmounted, ref } from 'vue'
  import { useRouter } from 'vue-router'

  import { fetchTelegramConfig, telegramLogin } from '@shared/auth/api'
  import { setCurrentUser } from '@shared/auth/session'
  import type { TelegramWidgetUser } from '@shared/auth/types'

  declare global {
    interface Window {
      onTelegramAuth?: (user: TelegramWidgetUser) => void
    }
  }

  const router = useRouter()
  const widgetHost = ref<HTMLElement | null>(null)
  const loading = ref(true)
  const loginPending = ref(false)
  const error = ref<string | null>(null)

  const currentUrl = new URL(window.location.href)
  const expectedHostname =
    (import.meta.env.VITE_TELEGRAM_WIDGET_HOSTNAME as string | undefined)?.trim() ?? ''
  const hostnameMismatch = computed(
    () => expectedHostname.length > 0 && currentUrl.hostname !== expectedHostname,
  )
  const canonicalAuthUrl = computed(() => {
    if (!hostnameMismatch.value) {
      return ''
    }
    const url = new URL(currentUrl.toString())
    url.hostname = expectedHostname
    return url.toString()
  })
  const requiresHttps = currentUrl.hostname !== 'localhost' && currentUrl.protocol !== 'https:'

  let widgetScript: HTMLScriptElement | null = null

  function mountWidget(botUsername: string): void {
    if (!widgetHost.value) {
      return
    }
    widgetHost.value.innerHTML = ''

    widgetScript = document.createElement('script')
    widgetScript.src = 'https://telegram.org/js/telegram-widget.js?22'
    widgetScript.async = true
    widgetScript.setAttribute('data-telegram-login', botUsername)
    widgetScript.setAttribute('data-size', 'large')
    widgetScript.setAttribute('data-radius', '10')
    widgetScript.setAttribute('data-onauth', 'onTelegramAuth(user)')
    widgetHost.value.appendChild(widgetScript)
  }

  async function initWidget(): Promise<void> {
    loading.value = true
    error.value = null
    if (requiresHttps) {
      error.value = 'Telegram Login Widget requires HTTPS for non-localhost domains.'
      loading.value = false
      return
    }
    if (hostnameMismatch.value) {
      error.value = `Open this page via "${expectedHostname}" to match Telegram bot domain.`
      loading.value = false
      return
    }
    try {
      const config = await fetchTelegramConfig()
      mountWidget(config.bot_username)
    } catch {
      error.value = 'Failed to load Telegram Login. Check backend settings.'
    } finally {
      loading.value = false
    }
  }

  async function handleTelegramAuth(user: TelegramWidgetUser): Promise<void> {
    loginPending.value = true
    error.value = null

    try {
      const authUser = await telegramLogin({
        ...user,
        id: Number(user.id),
        auth_date: Number(user.auth_date),
      })
      setCurrentUser(authUser)
      await router.replace({ name: 'profile' })
    } catch {
      error.value = 'Telegram login failed. Please try again.'
    } finally {
      loginPending.value = false
    }
  }

  onMounted(() => {
    window.onTelegramAuth = (user: TelegramWidgetUser) => {
      void handleTelegramAuth(user)
    }
    void initWidget()
  })

  onUnmounted(() => {
    delete window.onTelegramAuth
    widgetScript?.remove()
    widgetScript = null
  })
</script>

<template>
  <section class="auth-page">
    <div class="auth-card">
      <h2>Sign in with Telegram</h2>
      <p>Authentication is available only through Telegram OAuth.</p>

      <p v-if="loading" class="muted">Loading widget...</p>
      <p v-if="loginPending" class="muted">Verifying login...</p>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="hostnameMismatch && canonicalAuthUrl" class="muted">
        Open:
        <a :href="canonicalAuthUrl">{{ canonicalAuthUrl }}</a>
      </p>

      <div ref="widgetHost" class="widget-host" />
    </div>
  </section>
</template>

<style scoped>
  .auth-page {
    min-height: calc(100dvh - 96px);
    display: grid;
    place-items: center;
  }

  .auth-card {
    width: min(560px, 100%);
    padding: 2rem;
    border: 1px solid var(--color-border);
    border-radius: 0.75rem;
    background: #ffffff;
    box-shadow: var(--shadow-md);
    display: grid;
    gap: 1rem;
  }

  h2 {
    margin: 0;
  }

  p {
    margin: 0;
  }

  .muted {
    color: var(--color-text-muted);
  }

  .error {
    color: var(--color-danger);
  }

  .widget-host {
    min-height: 48px;
    display: flex;
    align-items: center;
  }
</style>
