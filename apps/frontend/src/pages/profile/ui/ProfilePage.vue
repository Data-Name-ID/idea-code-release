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
    @include top-links-bar;
  }

  .edit-bar__inner {
    @include top-links-inner;
  }

  .edit-link {
    @include top-link-pill;
  }

  // ─── Body layout ─────────────────────────────────────────────────────────────

  .profile-body {
    @include page-content-shell;
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
      background: $color-bg-elevated;
    }
  }

  .sidebar-section {
    @include respond-to('lg') {
      background: $color-bg-muted;
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
      background: $color-bg-elevated;
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
