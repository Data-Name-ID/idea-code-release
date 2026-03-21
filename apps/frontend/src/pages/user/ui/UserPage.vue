<script setup lang="ts">
  import { ref, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  import { userApi } from '@entities/user/api'
  import { eventApi } from '@entities/event/api'
  import { teamApi } from '@entities/team/api'

  import UserProfileCard from '@widgets/UserProfileCard/ui/UserProfileCard.vue'
  import SpecializationCard from '@widgets/SpecializationCard/ui/SpecializationCard.vue'
  import ActivityFeed from '@widgets/ActivityFeed/ui/ActivityFeed.vue'
  import type { ActivityItem } from '@widgets/ActivityFeed/ui/ActivityFeed.vue'
  import TeamsCard from '@widgets/TeamsCard/ui/TeamsCard.vue'
  import type { TeamEntry } from '@widgets/TeamsCard/ui/TeamsCard.vue'

  const route = useRoute()
  const router = useRouter()

  const userId = Number(route.params.id)

  type RawActivityEntry = {
    event: ActivityItem['event']
    status: ActivityItem['status']
    teamId: number | null
  }

  const user = ref<Awaited<ReturnType<typeof userApi.getById>> | null>(null)
  const loading = ref(true)
  const error = ref<string | null>(null)

  const activityFilter = ref<'all' | 'hackathon' | 'win'>('all')
  const activityItems = ref<ActivityItem[]>([])
  const teams = ref<TeamEntry[]>([])
  const loadingActivity = ref(true)
  const loadingTeams = ref(true)

  onMounted(async () => {
    try {
      user.value = await userApi.getById(userId)
    } catch {
      error.value = 'Пользователь не найден'
      loading.value = false
      return
    }
    loading.value = false

    try {
      // ── Activity ──────────────────────────────────────
      const eventsRes = await eventApi.getList({ limit: 50 })
      const events = eventsRes.data

      const ratingResults = await Promise.all(
        events.map((event) => eventApi.getRatings(event.id).catch((): null => null)),
      )

      const raw: RawActivityEntry[] = []
      const teamIdsNeeded = new Set<number>()

      ratingResults.forEach((res, i) => {
        if (!res) return
        const entry = res.ratings.find((r) => r.user_id === userId)
        if (!entry) return
        if (entry.team_id) teamIdsNeeded.add(entry.team_id)
        raw.push({ event: events[i], status: entry.status, teamId: entry.team_id })
      })

      const teamNameMap = new Map<number, string>()
      await Promise.all(
        [...teamIdsNeeded].map((id) =>
          teamApi.getById(id).then((t) => teamNameMap.set(id, t.name)).catch(() => {}),
        ),
      )

      const teamWinCounts = new Map<number, number>()
      raw.forEach(({ status, teamId }) => {
        if (!teamId || (status !== 'winner' && status !== 'prize_winner')) return
        teamWinCounts.set(teamId, (teamWinCounts.get(teamId) ?? 0) + 1)
      })

      activityItems.value = raw
        .sort((a, b) => new Date(b.event.date).getTime() - new Date(a.event.date).getTime())
        .map(({ event, status, teamId }) => ({
          event,
          status,
          teamName: teamId ? (teamNameMap.get(teamId) ?? null) : null,
        }))

      loadingActivity.value = false

      // ── Teams ────────────────────────────────────────
      const teamsRes = await teamApi.getList({ user_id: userId })
      const fullTeams = await Promise.all(
        teamsRes.data.map((t) => teamApi.getById(t.id).catch((): null => null)),
      )

      teams.value = fullTeams
        .filter((t): t is NonNullable<typeof t> => t !== null)
        .map((team): TeamEntry => ({
          id: team.id,
          name: team.name,
          role: user.value?.roles[0]?.name ?? 'Участник',
          isActive: team.events.length > 0,
          winCount: teamWinCounts.get(team.id) ?? 0,
          memberCount: team.users.length,
        }))
    } finally {
      loadingActivity.value = false
      loadingTeams.value = false
    }
  })
</script>

<template>
  <div class="user-page">
    <!-- Header -->
    <header class="page-header">
      <button class="back-btn" @click="router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
      </button>
      <span class="page-header__title">Участник</span>
      <div style="width: 36px" />
    </header>

    <!-- Loading -->
    <div v-if="loading" class="profile-skeleton">
      <div class="skel skel--avatar" />
      <div class="skel skel--name" />
      <div class="skel skel--roles" />
      <div class="skel-stats">
        <div class="skel skel--stat" />
        <div class="skel skel--stat" />
        <div class="skel skel--stat" />
      </div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="state-empty">
      <p>{{ error }}</p>
    </div>

    <!-- Content -->
    <template v-else-if="user">
      <UserProfileCard :user="user" />

      <div class="section">
        <ActivityFeed
          :items="activityItems"
          :is-loading="loadingActivity"
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
          :is-loading="loadingTeams"
          @navigate-to-team="(id) => $router.push(`/teams/${id}`)"
        />
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
  .user-page {
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

  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid var(--p-border);
    position: sticky;
    top: 0;
    z-index: 10;
    background: var(--p-bg);
  }

  .page-header__title {
    font-size: 16px;
    font-weight: 700;
  }

  .back-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border: none;
    background: none;
    color: var(--p-text-primary);
    cursor: pointer;
    border-radius: 8px;

    &:hover { background: var(--p-surface); }
  }

  .section {
    padding: 0 16px;
    margin-top: 20px;
  }

  // ── Skeleton ────────────────────────────────────────────

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

    &--avatar { width: 88px; height: 88px; border-radius: 50%; }
    &--name   { height: 24px; width: 160px; }
    &--roles  { height: 16px; width: 200px; }
    &--stat   { height: 60px; width: 72px; border-radius: 12px; }
  }

  @keyframes shimmer {
    0%   { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  // ── Error / Empty ────────────────────────────────────────

  .state-empty {
    padding: 48px 16px;
    text-align: center;
    color: var(--p-text-secondary);
    font-size: 14px;
  }
</style>
