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
        <RouterLink :to="{ name: 'profile-edit' }" class="edit-link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="15" height="15">
            <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125" />
          </svg>
          Редактировать
        </RouterLink>
      </div>

      <UserProfileCard :user="user" />

      <div class="section">
        <ActivityFeed
          :items="activityItems"
          :is-loading="isLoadingActivity"
          :active-filter="activityFilter"
          @filter-change="activityFilter = $event"
          @navigate-to-event="(id) => $router.push(`/events/${id}`)"
        />
      </div>

      <div class="section">
        <SpecializationCard :roles="user.roles" :skills="user.skills" />
      </div>

      <div class="section">
        <TeamsCard
          :teams="teams"
          :is-loading="isLoadingTeams"
          @navigate-to-team="(id) => $router.push(`/teams/${id}`)"
        />
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
  .profile-page {
    @include page-root;
  }

  .edit-bar {
    display: flex;
    justify-content: flex-end;
    padding: 10px 16px 0;
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

  .section {
    padding: 0 16px;
    margin-top: 20px;
  }

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
