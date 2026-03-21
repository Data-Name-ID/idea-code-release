<script setup lang="ts">
  import { ref, computed } from 'vue'

  import { authState } from '@shared/auth/session'

  import UserProfileCard from '@widgets/UserProfileCard/ui/UserProfileCard.vue'
  import SpecializationCard from '@widgets/SpecializationCard/ui/SpecializationCard.vue'
  import ActivityFeed from '@widgets/ActivityFeed/ui/ActivityFeed.vue'
  import type { ActivityItem } from '@widgets/ActivityFeed/ui/ActivityFeed.vue'
  import TeamsCard from '@widgets/TeamsCard/ui/TeamsCard.vue'
  import type { TeamEntry } from '@widgets/TeamsCard/ui/TeamsCard.vue'

  const user = computed(() => authState.currentUser.value)

  const activityFilter = ref<'all' | 'hackathon' | 'win'>('all')

  // These will be populated once dedicated backend endpoints are implemented
  const activityItems: ActivityItem[] = []
  const teams: TeamEntry[] = []
</script>

<template>
  <div class="profile-page">
    <!-- Session not yet initialized — show skeleton -->
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
      <UserProfileCard :user="user" />

      <div class="section">
        <ActivityFeed
          :items="activityItems"
          :is-loading="false"
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
          :is-loading="false"
          @navigate-to-team="(id) => $router.push(`/teams/${id}`)"
        />
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
  .profile-page {
    --p-bg:             #121212;
    --p-surface:        #1c1c1e;
    --p-border:         rgba(255, 255, 255, 0.08);
    --p-accent:         #ff6b2b;
    --p-text-primary:   #ffffff;
    --p-text-secondary: rgba(255, 255, 255, 0.5);

    min-height: 100dvh;
    background: var(--p-bg);
    color: var(--p-text-primary);
    font-family: 'Manrope', 'IBM Plex Sans', sans-serif;
    padding-bottom: 40px;
  }

  .section {
    padding: 0 16px;
    margin-top: 20px;
  }

  /* ── Skeleton ──────────────────────────────────── */

  .profile-skeleton {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 14px;
    padding: 32px 16px;
  }

  .skel-stats {
    display: flex;
    gap: 8px;
  }

  .skel {
    border-radius: 8px;
    background: linear-gradient(90deg, #1e1e1e 25%, #282828 50%, #1e1e1e 75%);
    background-size: 200% 100%;
    animation: shimmer 1.4s infinite;

    &--avatar {
      width: 88px;
      height: 88px;
      border-radius: 50%;
    }

    &--name {
      height: 24px;
      width: 160px;
    }

    &--roles {
      height: 16px;
      width: 200px;
    }

    &--stat {
      height: 60px;
      width: 72px;
      border-radius: 12px;
    }
  }

  @keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }
</style>
