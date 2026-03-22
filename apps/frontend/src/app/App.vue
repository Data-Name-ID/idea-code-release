<script setup lang="ts">
  import { computed } from 'vue'
  import { RouterLink, RouterView, useRoute } from 'vue-router'

  import { authState } from '@shared/auth/session'

  const route = useRoute()

  const navItems = [
    { name: 'profile', label: 'Профиль' },
    { name: 'teammates', label: 'Участники' },
    { name: 'applications', label: 'Заявки' },
    { name: 'organizer-import', label: 'Импорт' },
  ] as const

  const isNavVisible = computed(() => authState.isAuthenticated.value && route.name !== 'auth')
</script>

<template>
  <div class="app-shell">
    <main class="app-main">
      <RouterView />
    </main>

    <nav v-if="isNavVisible" class="site-nav" aria-label="Основная навигация">
      <RouterLink
        v-for="item in navItems"
        :key="item.name"
        :to="{ name: item.name }"
        class="site-nav__link"
        :class="{ 'site-nav__link--active': route.name === item.name }"
      >
        {{ item.label }}
      </RouterLink>
    </nav>
  </div>
</template>

<style scoped lang="scss">
  .app-shell {
    min-height: 100dvh;
    display: flex;
    flex-direction: column;
  }

  .app-main {
    flex: 1;
    min-height: 0;
  }

  .site-nav {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 120;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
    padding: 10px 12px calc(10px + env(safe-area-inset-bottom));
    border-top: 1px solid $color-border;
    background: rgba(18, 18, 20, 0.96);
    backdrop-filter: blur(12px);
  }

  .site-nav__link {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 38px;
    border-radius: $radius-md;
    color: $color-text-secondary;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none;
    transition: color $transition-fast, background-color $transition-fast;

    &:hover {
      color: $color-text-primary;
      background: rgba(255, 255, 255, 0.05);
    }

    &--active {
      color: #fff;
      background: rgba($color-accent, 0.28);
    }
  }

  @media (min-width: 1024px) {
    .site-nav {
      left: 50%;
      max-width: 760px;
      border: 1px solid $color-border;
      border-bottom: none;
      border-radius: 18px 18px 0 0;
      transform: translateX(-50%);
    }
  }
</style>
