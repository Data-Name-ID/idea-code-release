import { ref } from 'vue'

import { eventApi } from '@entities/event/api'
import { teamApi } from '@entities/team/api'
import type { ActivityItem } from '@widgets/ActivityFeed/model/types'
import type { TeamEntry } from '@widgets/TeamsCard/model/types'

export function useUserActivity(userId: number, userRoleName?: string) {
  const activityItems = ref<ActivityItem[]>([])
  const teams = ref<TeamEntry[]>([])
  const isLoadingActivity = ref(true)
  const isLoadingTeams = ref(true)

  async function load() {
    try {
      const eventsRes = await eventApi.getList({ limit: 50 })
      const ratingResults = await Promise.all(
        eventsRes.data.map((event) => eventApi.getRatings(event.id).catch((): null => null)),
      )

      const rawEntries: Array<{ event: ActivityItem['event']; status: ActivityItem['status']; teamId: number | null }> = []
      const teamIdsNeeded = new Set<number>()

      ratingResults.forEach((res, i) => {
        if (!res) return
        const entry = res.ratings.find((r) => r.user_id === userId)
        if (!entry) return
        if (entry.team_id) teamIdsNeeded.add(entry.team_id)
        rawEntries.push({ event: eventsRes.data[i], status: entry.status, teamId: entry.team_id })
      })

      const teamNameMap = new Map<number, string>()
      await Promise.all(
        [...teamIdsNeeded].map((id) =>
          teamApi.getById(id).then((t) => teamNameMap.set(id, t.name)).catch(() => {}),
        ),
      )

      const teamWinCounts = new Map<number, number>()
      rawEntries.forEach(({ status, teamId }) => {
        if (!teamId || (status !== 'winner' && status !== 'prize_winner')) return
        teamWinCounts.set(teamId, (teamWinCounts.get(teamId) ?? 0) + 1)
      })

      activityItems.value = rawEntries
        .sort((a, b) => new Date(b.event.date).getTime() - new Date(a.event.date).getTime())
        .map(({ event, status, teamId }) => ({
          event,
          status,
          teamName: teamId ? (teamNameMap.get(teamId) ?? null) : null,
        }))

      isLoadingActivity.value = false

      const teamsRes = await teamApi.getList({ user_id: userId })
      const fullTeams = await Promise.all(
        teamsRes.data.map((t) => teamApi.getById(t.id).catch((): null => null)),
      )

      teams.value = fullTeams
        .filter((t): t is NonNullable<typeof t> => t !== null)
        .map((team) => ({
          id: team.id,
          name: team.name,
          role: userRoleName ?? 'Участник',
          isActive: team.events.length > 0,
          winCount: teamWinCounts.get(team.id) ?? 0,
          memberCount: team.users.length,
        }))
    } finally {
      isLoadingActivity.value = false
      isLoadingTeams.value = false
    }
  }

  return { activityItems, teams, isLoadingActivity, isLoadingTeams, load }
}
