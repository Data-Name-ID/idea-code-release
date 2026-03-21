<script setup lang="ts">
  import { ref, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  import { userApi } from '@entities/user/api'
  import { useUserActivity } from '@shared/composables/useUserActivity'
  import type { ActivityFilter } from '@widgets/ActivityFeed/model/types'

  import UserProfileCard from '@widgets/UserProfileCard/ui/UserProfileCard.vue'
  import SpecializationCard from '@widgets/SpecializationCard/ui/SpecializationCard.vue'
  import ActivityFeed from '@widgets/ActivityFeed/ui/ActivityFeed.vue'
  import TeamsCard from '@widgets/TeamsCard/ui/TeamsCard.vue'

  const route = useRoute()
  const router = useRouter()
  const userId = Number(route.params.id)

  const user = ref<Awaited<ReturnType<typeof userApi.getById>> | null>(null)
  const isLoading = ref(true)
  const error = ref<string | null>(null)
  const activityFilter = ref<ActivityFilter>('all')

  const { activityItems, teams, isLoadingActivity, isLoadingTeams, load } = useUserActivity(userId)

  onMounted(async () => {
    try {
      user.value = await userApi.getById(userId)
    } catch {
      error.value = 'Пользователь не найден'
      isLoading.value = false
      return
    }
    isLoading.value = false

    load()
  })
</script>

<template>
  <div class="user-page">
    <header class="page-header">
      <button class="back-btn" @click="router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
      </button>
      <span class="page-header__title">Участник</span>
      <div style="width: 36px" />
    </header>

    <div v-if="isLoading" class="profile-skeleton">
      <div class="skel skel--avatar" />
      <div class="skel skel--name" />
      <div class="skel skel--roles" />
      <div class="skel-stats">
        <div class="skel skel--stat" />
        <div class="skel skel--stat" />
        <div class="skel skel--stat" />
      </div>
    </div>

    <div v-else-if="error" class="state-empty">
      <p>{{ error }}</p>
    </div>

    <template v-else-if="user">
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
  .user-page {
    @include page-root;
  }

  .page-header {
    @include sticky-header;
  }

  .page-header__title {
    font-size: 16px;
    font-weight: 700;
  }

  .back-btn {
    @include back-button;
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

  .state-empty {
    padding: 48px 16px;
    text-align: center;
    color: $color-text-secondary;
    font-size: 14px;
  }
</style>
