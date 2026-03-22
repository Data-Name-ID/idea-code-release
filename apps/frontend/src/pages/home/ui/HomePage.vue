<script setup lang="ts">
  import { computed } from 'vue'

  import { authState } from '@shared/auth/session'

  const apiBaseUrl =
    import.meta.env.VITE_API_BASE_URL ??
    import.meta.env.VITE_API_BASE_URL ??
    'http://localhost:8000'
  const currentUser = computed(() => authState.currentUser.value)
</script>

<template>
  <section class="home">
    <h2>Authenticated Session</h2>
    <p v-if="currentUser">
      Telegram ID:
      <code>{{ currentUser.telegram_user_id }}</code>
    </p>
    <p v-if="currentUser">
      Account:
      <code>{{ currentUser.username ? '@' + currentUser.username : currentUser.first_name }}</code>
    </p>
    <p>
      API base URL:
      <code>{{ apiBaseUrl }}</code>
    </p>
  </section>
</template>

<style scoped lang="scss">
  .home {
    @include page-root;
    max-width: 720px;
    display: grid;
    gap: 0.75rem;
    margin: 0 auto;
    padding: 24px 16px;
  }

  h2 {
    margin: 0;
  }

  code {
    padding: 0.125rem 0.375rem;
    border-radius: 0.375rem;
    background: $color-surface;
    border: 1px solid $color-border;
  }
</style>
