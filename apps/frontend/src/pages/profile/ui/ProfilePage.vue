<script setup lang="ts">
  import { ref } from 'vue'

  import UserProfileCard from '@widgets/UserProfileCard/ui/UserProfileCard.vue'
  import SpecializationCard from '@widgets/SpecializationCard/ui/SpecializationCard.vue'
  import ActivityFeed from '@widgets/ActivityFeed/ui/ActivityFeed.vue'
  import TeamsCard from '@widgets/TeamsCard/ui/TeamsCard.vue'

  import {
    MOCK_USER,
    MOCK_HACKATHON_COUNT,
    MOCK_WIN_COUNT,
    MOCK_RANK,
    MOCK_ACTIVITY,
    MOCK_TEAMS,
  } from '../mock'

  const activityFilter = ref<'all' | 'hackathon' | 'win'>('all')
</script>

<template>
  <div class="profile-page">
    <UserProfileCard
      :user="MOCK_USER"
      :hackathon-count="MOCK_HACKATHON_COUNT"
      :win-count="MOCK_WIN_COUNT"
      :rank="MOCK_RANK"
    />

    <div class="section">
      <ActivityFeed
        :items="MOCK_ACTIVITY"
        :is-loading="false"
        :active-filter="activityFilter"
        @filter-change="activityFilter = $event"
        @navigate-to-event="(id) => $router.push(`/events/${id}`)"
      />
    </div>

    <div class="section">
      <SpecializationCard :roles="MOCK_USER.roles" :skills="MOCK_USER.skills" />
    </div>

    <div class="section">
      <TeamsCard
        :teams="MOCK_TEAMS"
        :is-loading="false"
        @navigate-to-team="(id) => $router.push(`/teams/${id}`)"
      />
    </div>
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
</style>
