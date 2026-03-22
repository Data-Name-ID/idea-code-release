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
  const isLoading = ref(true)
  const isLoginPending = ref(false)
  const error = ref<string | null>(null)

  const currentUrl = new URL(window.location.href)
  const expectedHostname =
    (import.meta.env.VITE_TELEGRAM_WIDGET_HOSTNAME as string | undefined)?.trim() ?? ''
  const hostnameMismatch = computed(
    () => expectedHostname.length > 0 && currentUrl.hostname !== expectedHostname,
  )
  const canonicalAuthUrl = computed(() => {
    if (!hostnameMismatch.value) return ''
    const url = new URL(currentUrl.toString())
    url.hostname = expectedHostname
    return url.toString()
  })
  const requiresHttps = currentUrl.hostname !== 'localhost' && currentUrl.protocol !== 'https:'

  let widgetScript: HTMLScriptElement | null = null

  function mountWidget(botUsername: string): void {
    if (!widgetHost.value) return
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
    isLoading.value = true
    error.value = null

    if (requiresHttps) {
      error.value = 'Telegram Login Widget requires HTTPS for non-localhost domains.'
      isLoading.value = false
      return
    }

    if (hostnameMismatch.value) {
      error.value = `Open this page via "${expectedHostname}" to match Telegram bot domain.`
      isLoading.value = false
      return
    }

    try {
      const config = await fetchTelegramConfig()
      mountWidget(config.bot_username)
    } catch {
      error.value = 'Failed to load Telegram Login. Check backend settings.'
    } finally {
      isLoading.value = false
    }
  }

  async function handleTelegramAuth(user: TelegramWidgetUser): Promise<void> {
    isLoginPending.value = true
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
      isLoginPending.value = false
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
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-card__icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="32" height="32">
          <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
        </svg>
      </div>

      <h1 class="auth-card__title">Пицца хаб</h1>
      <p class="auth-card__subtitle">Войдите через Telegram, чтобы продолжить</p>

      <div class="auth-card__widget">
        <div v-if="isLoading" class="auth-card__state">
          <div class="spinner" />
          <span>Загрузка...</span>
        </div>
        <div v-else-if="isLoginPending" class="auth-card__state">
          <div class="spinner" />
          <span>Проверка...</span>
        </div>
        <p v-if="error" class="auth-card__error">{{ error }}</p>
        <p v-if="hostnameMismatch && canonicalAuthUrl" class="auth-card__hint">
          Откройте страницу через:
          <a :href="canonicalAuthUrl" class="auth-card__link">{{ canonicalAuthUrl }}</a>
        </p>
        <div ref="widgetHost" class="widget-host" />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
  .auth-page {
    min-height: 100dvh;
    background: $color-bg;
    @include flex-center;
    padding: 24px 16px;
    font-family: $font-family-base;
  }

  .auth-card {
    width: 100%;
    max-width: 380px;
    background: $color-surface;
    border: 1px solid $color-border;
    border-radius: $radius-3xl;
    padding: 40px 32px;
    @include flex-column(12px);
    align-items: center;

    &__icon {
      width: 72px;
      height: 72px;
      border-radius: 20px;
      background: rgba($color-accent, 0.12);
      border: 1px solid rgba($color-accent, 0.3);
      @include flex-center;
      color: $color-accent;
      margin-bottom: 4px;
    }

    &__title {
      margin: 0;
      font-size: 22px;
      font-weight: 800;
      text-align: center;
    }

    &__subtitle {
      margin: 0;
      font-size: 14px;
      color: $color-text-secondary;
      text-align: center;
      line-height: 1.5;
    }

    &__widget {
      margin-top: 12px;
      width: 100%;
      @include flex-column(12px);
      align-items: center;
    }

    &__state {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      color: $color-text-secondary;
    }

    &__error {
      margin: 0;
      font-size: 13px;
      color: $color-danger;
      text-align: center;
      background: rgba($color-danger, 0.08);
      border: 1px solid rgba($color-danger, 0.2);
      border-radius: $radius-md;
      padding: 10px 14px;
      width: 100%;
      box-sizing: border-box;
    }

    &__hint {
      margin: 0;
      font-size: 13px;
      color: $color-text-secondary;
      text-align: center;
    }

    &__link {
      color: $color-accent;
      text-decoration: none;
      &:hover { text-decoration: underline; }
    }
  }

  .widget-host {
    min-height: 48px;
    @include flex-center;
  }

  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-top-color: $color-accent;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    flex-shrink: 0;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
