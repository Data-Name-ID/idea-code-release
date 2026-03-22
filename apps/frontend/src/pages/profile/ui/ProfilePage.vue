<script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'

  import { authState } from '@shared/auth/session'
  import { useUserActivity } from '@shared/composables/useUserActivity'
  import { BaseButton } from '@shared/ui'
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
      <div class="profile-body">
        <aside class="profile-sidebar">
          <RouterLink :to="{ name: 'profile-edit' }" class="profile-edit-link">
            <BaseButton type="button" variant="ghost" block>Редактировать профиль</BaseButton>
          </RouterLink>
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

  .profile-edit-link {
    text-decoration: none;
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
