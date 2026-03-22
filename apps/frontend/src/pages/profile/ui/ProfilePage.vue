<script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'

  import { authState } from '@shared/auth/session'
  import { useUserActivity } from '@shared/composables/useUserActivity'
  import type { ActivityFilter } from '@widgets/ActivityFeed/model/types'

  import UserProfileCard from '@widgets/UserProfileCard/ui/UserProfileCard.vue'
  import SpecializationCard from '@widgets/SpecializationCard/ui/SpecializationCard.vue'
  import ActivityFeed from '@widgets/ActivityFeed/ui/ActivityFeed.vue'
  import TeamsCard from '@widgets/TeamsCard/ui/TeamsCard.vue'

  const user = computed(() => authState.currentUser.value)
  const activityFilter = ref<ActivityFilter>('all')

  const { activityItems, teams, isLoadingActivity, isLoadingTeams, load } = useUserActivity(
    user.value?.id ?? 0,
    user.value?.roles[0]?.name,
  )

  onMounted(() => {
    if (user.value) load()
  })
</script>

<template>
  <div class="profile-page">
    <div v-if="!authState.initialized.value" class="profile-skeleton">
      <div class="skel skel--avatar" />
      <div class="skel skel--name" />
      <div class="skel skel--roles" />
      <div class="skel-stats">
        <div class="skel skel--stat" />
        <div class="skel skel--stat" />
        <div class="skel skel--stat" />
      </div>
    </div>

    <template v-else-if="user">
      <div class="edit-bar">
        <div class="edit-bar__inner">
          <RouterLink :to="{ name: 'teammates' }" class="edit-link">
            Сокомандники
          </RouterLink>
          <RouterLink :to="{ name: 'applications' }" class="edit-link">
            Заявки
          </RouterLink>
          <RouterLink :to="{ name: 'profile-edit' }" class="edit-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="15" height="15">
              <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125" />
            </svg>
            Редактировать
          </RouterLink>
        </div>
      </div>

      <div class="profile-body">
        <aside class="profile-sidebar">
          <div class="sidebar-card">
            <UserProfileCard :user="user" />
          </div>
          <div class="sidebar-section">
            <SpecializationCard :roles="user.roles" :skills="user.skills" />
          </div>
        </aside>

        <main class="profile-main">
          <div class="main-section">
            <ActivityFeed
              :items="activityItems"
              :is-loading="isLoadingActivity"
              :active-filter="activityFilter"
              @filter-change="activityFilter = $event"
              @navigate-to-event="(id) => $router.push(`/events/${id}`)"
            />
          </div>
          <div class="main-section">
            <TeamsCard
              :teams="teams"
              :is-loading="isLoadingTeams"
              @navigate-to-team="(id) => $router.push(`/teams/${id}`)"
            />
          </div>
        </main>
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
  .profile-page {
    @include page-root;
  }

  // ─── Edit bar ────────────────────────────────────────────────────────────────

  .edit-bar {
    display: flex;
    justify-content: flex-end;
    padding: 10px 16px 0;
    border-bottom: 1px solid $color-border;

    @include respond-to('lg') {
      padding: 0;
      border-bottom: none;
    }
  }

  .edit-bar__inner {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    padding: 10px 0 10px;

    @include respond-to('lg') {
      max-width: 1200px;
      width: 100%;
      margin: 0 auto;
      padding: 14px 32px;
      border-bottom: 1px solid $color-border;
    }
  }

  .edit-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    border-radius: $radius-full;
    border: 1px solid $color-border;
    color: $color-text-secondary;
    font-size: 13px;
    font-weight: 500;
    text-decoration: none;
    transition: border-color $transition-fast, color $transition-fast;

    &:hover {
      border-color: $color-accent;
      color: $color-accent;
      text-decoration: none;
    }
  }

  // ─── Body layout ─────────────────────────────────────────────────────────────

  .profile-body {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 16px 16px 48px;

    @include respond-to('lg') {
      flex-direction: row;
      align-items: flex-start;
      gap: 24px;
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 32px 64px;
    }
  }

  // ─── Sidebar ─────────────────────────────────────────────────────────────────

  .profile-sidebar {
    display: flex;
    flex-direction: column;
    gap: 20px;

    @include respond-to('lg') {
      width: 320px;
      flex-shrink: 0;
      gap: 16px;
    }
  }

  .sidebar-card {
    @include respond-to('lg') {
      border: 1px solid $color-border;
      border-radius: $radius-2xl;
      background: #141417;
    }
  }

  .sidebar-section {
    @include respond-to('lg') {
      background: #1a1a1d;
      border: 1px solid rgba($color-accent, 0.2);
      border-radius: $radius-2xl;
    }
  }

  // ─── Main column ─────────────────────────────────────────────────────────────

  .profile-main {
    display: flex;
    flex-direction: column;
    gap: 20px;
    min-width: 0;

    @include respond-to('lg') {
      flex: 1;
      gap: 24px;
    }
  }

  .main-section {
    @include respond-to('lg') {
      background: #141417;
      border: 1px solid $color-border;
      border-radius: $radius-2xl;
      padding: 28px 32px;
    }
  }

  // ─── Skeleton ────────────────────────────────────────────────────────────────

  .profile-skeleton {
    @include flex-column(14px);
    align-items: center;
    padding: 32px 16px;
  }

  .skel-stats {
    display: flex;
    gap: 8px;
  }

  .skel {
    border-radius: $radius-sm;
    @include skeleton-shimmer;

    &--avatar { width: 88px; height: 88px; border-radius: 50%; }
    &--name   { height: 24px; width: 160px; }
    &--roles  { height: 16px; width: 200px; }
    &--stat   { height: 60px; width: 72px; border-radius: $radius-lg; }
  }
</style>
