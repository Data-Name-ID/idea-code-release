<script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  import { eventApi } from '@entities/event/api'
  import { participationApplicationApi } from '@entities/participation-application/api'
  import { roleApi } from '@entities/role/api'
  import { skillApi } from '@entities/skill/api'
  import { userApi } from '@entities/user/api'
  import { teamApi } from '@entities/team/api'
  import { formatDateLong, initials } from '@shared/lib/format'
  import type { RoleResponse, SkillResponse } from '@shared/types/api'
  import type { RatingEntry } from '../model/types'

  const route = useRoute()
  const router = useRouter()
  const eventId = computed(() => Number(route.params.id))

  const event = ref<Awaited<ReturnType<typeof eventApi.getById>> | null>(null)
  const isLoading = ref(true)
  const error = ref<string | null>(null)
  const entries = ref<RatingEntry[]>([])
  const isSendingApplication = ref(false)
  const applicationError = ref<string | null>(null)
  const applicationSuccess = ref<string | null>(null)
  const allRoles = ref<RoleResponse[]>([])
  const allSkills = ref<SkillResponse[]>([])
  const applicationForm = ref({
    desiredRole: '',
    preferredTeamFormat: 'team' as 'team' | 'solo',
    comment: '',
    skillIds: [] as number[],
  })

  const winners = computed(() => entries.value.filter((e) => e.status === 'winner'))
  const prizeWinners = computed(() => entries.value.filter((e) => e.status === 'prize_winner'))
  const participants = computed(() => entries.value.filter((e) => e.status === 'participant'))

  onMounted(async () => {
    try {
      const [eventData, ratingsData, rolesData, skillsData] = await Promise.all([
        eventApi.getById(eventId.value),
        eventApi.getRatings(eventId.value),
        roleApi.getList(),
        skillApi.getList(),
      ])

      event.value = eventData
      allRoles.value = rolesData
      allSkills.value = skillsData

      const raw = ratingsData.ratings
      const userIds = [...new Set(raw.map((r) => r.user_id))]
      const teamIds = [...new Set(raw.map((r) => r.team_id).filter((id): id is number => id !== null))]

      const [users, teams] = await Promise.all([
        Promise.all(userIds.map((id) => userApi.getById(id).catch(() => null))),
        Promise.all(teamIds.map((id) => teamApi.getById(id).catch(() => null))),
      ])

      const userMap = new Map(users.filter(Boolean).map((u) => [u!.id, u!]))
      const teamMap = new Map(teams.filter(Boolean).map((t) => [t!.id, t!]))

      const teamSeen = new Set<number>()
      const result: RatingEntry[] = []

      for (const r of raw) {
        if (r.team_id !== null) {
          if (teamSeen.has(r.team_id)) continue
          teamSeen.add(r.team_id)

          const team = teamMap.get(r.team_id)
          const members = raw
            .filter((x) => x.team_id === r.team_id)
            .map((x) => {
              const u = userMap.get(x.user_id)
              return {
                name: u?.name ?? `User #${x.user_id}`,
                avatar: u?.avatar ?? null,
                roles: u?.roles.map((role) => role.name).join(', ') ?? '',
              }
            })

          result.push({
            kind: 'team',
            id: r.team_id,
            status: r.status,
            name: team?.name ?? `Team #${r.team_id}`,
            memberCount: team?.users.length ?? members.length,
            members,
          })
        } else {
          const u = userMap.get(r.user_id)
          result.push({
            kind: 'solo',
            id: r.user_id,
            status: r.status,
            name: u?.name ?? `User #${r.user_id}`,
            avatar: u?.avatar ?? null,
            roles: u?.roles.map((role) => role.name).join(', ') ?? '',
          })
        }
      }

      entries.value = result
    } catch {
      error.value = 'Не удалось загрузить мероприятие'
    } finally {
      isLoading.value = false
    }
  })

  function navigate(entry: RatingEntry): void {
    if (entry.kind === 'team') router.push(`/teams/${entry.id}`)
    else router.push(`/users/${entry.id}`)
  }

  function toggleSkill(skillId: number): void {
    const current = applicationForm.value.skillIds
    const index = current.indexOf(skillId)
    if (index === -1) current.push(skillId)
    else current.splice(index, 1)
  }

  async function sendApplication(): Promise<void> {
    isSendingApplication.value = true
    applicationError.value = null
    applicationSuccess.value = null
    try {
      await participationApplicationApi.create({
        event_id: eventId.value,
        desired_role: applicationForm.value.desiredRole,
        preferred_team_format: applicationForm.value.preferredTeamFormat,
        comment: applicationForm.value.comment,
        skill_ids: applicationForm.value.skillIds,
      })
      applicationForm.value.comment = ''
      applicationForm.value.skillIds = []
      applicationSuccess.value = 'Заявка отправлена'
    } catch (e) {
      applicationError.value = e instanceof Error ? e.message : 'Не удалось отправить заявку'
    } finally {
      isSendingApplication.value = false
    }
  }
</script>

<template>
  <div class="event-page">
    <header class="page-header">
      <button class="back-btn" @click="router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
      </button>
      <span class="page-header__title">Мероприятие</span>
      <div style="width: 36px" />
    </header>

    <template v-if="isLoading">
      <div class="page-body">
        <div class="cover-skeleton" />
        <div class="info-skeleton">
          <div class="skel skel--badge" />
          <div class="skel skel--title" />
          <div class="skel skel--line" />
          <div class="skel skel--line skel--short" />
        </div>
      </div>
    </template>

    <div v-else-if="error" class="state-empty">
      <p>{{ error }}</p>
    </div>

    <template v-else-if="event">
      <div class="page-body">
      <div class="cover">
        <img v-if="event.cover" :src="event.cover" :alt="event.title" class="cover__img" />
        <div v-else class="cover__placeholder" />
        <span v-if="event.is_verify" class="cover__badge">
          <svg viewBox="0 0 20 20" fill="currentColor" width="13" height="13">
            <path fill-rule="evenodd" d="M16.403 12.652a3 3 0 0 0 0-5.304 3 3 0 0 0-3.75-3.751 3 3 0 0 0-5.305 0 3 3 0 0 0-3.751 3.75 3 3 0 0 0 0 5.305 3 3 0 0 0 3.75 3.751 3 3 0 0 0 5.305 0 3 3 0 0 0 3.751-3.75Zm-2.546-4.46a.75.75 0 0 0-1.214-.883l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clip-rule="evenodd" />
          </svg>
          Верифицировано
        </span>
      </div>

      <section class="info">
        <h1 class="info__title">{{ event.title }}</h1>
        <div class="info__date">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="15" height="15">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5" />
          </svg>
          {{ formatDateLong(event.date) }}
        </div>
        <p v-if="event.description" class="info__description">{{ event.description }}</p>
      </section>

      <section class="application">
        <div class="application__head">
          <h2 class="application__title">Оставить заявку на участие</h2>
          <RouterLink :to="`/applications?event_id=${event.id}`" class="application__link">Все заявки</RouterLink>
        </div>

        <div class="application__grid">
          <select v-model="applicationForm.desiredRole" class="application__field">
            <option value="">Желаемая роль</option>
            <option v-for="role in allRoles" :key="role.id" :value="role.name">{{ role.name }}</option>
          </select>

          <select v-model="applicationForm.preferredTeamFormat" class="application__field">
            <option value="team">Хочу в команду</option>
            <option value="solo">Рассматриваю solo</option>
          </select>
        </div>

        <textarea
          v-model="applicationForm.comment"
          class="application__field"
          rows="3"
          placeholder="Комментарий о вашем опыте и ожиданиях"
        />

        <div class="application__skills">
          <button
            v-for="skill in allSkills"
            :key="skill.id"
            type="button"
            class="application__skill"
            :class="{ 'application__skill--active': applicationForm.skillIds.includes(skill.id) }"
            @click="toggleSkill(skill.id)"
          >
            {{ skill.name }}
          </button>
        </div>

        <p v-if="applicationError" class="application__error">{{ applicationError }}</p>
        <p v-if="applicationSuccess" class="application__success">{{ applicationSuccess }}</p>

        <button type="button" class="application__submit" :disabled="isSendingApplication" @click="sendApplication">
          {{ isSendingApplication ? 'Отправляем…' : 'Оставить заявку' }}
        </button>
      </section>

      <section v-if="entries.length" class="ratings">
        <h2 class="ratings__title">Результаты</h2>

        <div v-if="winners.length" class="group">
          <div class="group__header group__header--gold">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
              <path fill-rule="evenodd" d="M5.166 2.621v.858c-1.035.148-2.059.33-3.071.543a.75.75 0 0 0-.584.859 6.753 6.753 0 0 0 6.138 5.6 6.73 6.73 0 0 0 2.743 1.346A6.707 6.707 0 0 1 9.279 15H8.54c-1.036 0-1.875.84-1.875 1.875V19.5h-.75a2.25 2.25 0 0 0-2.25 2.25c0 .414.336.75.75.75h15a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-2.25-2.25h-.75v-2.625c0-1.036-.84-1.875-1.875-1.875h-.739a6.706 6.706 0 0 1-1.112-3.173 6.73 6.73 0 0 0 2.743-1.347 6.753 6.753 0 0 0 6.139-5.6.75.75 0 0 0-.585-.858 47.077 47.077 0 0 0-3.07-.543V2.62a.75.75 0 0 0-.658-.744 49.798 49.798 0 0 0-6.093-.377c-2.063 0-4.096.128-6.093.377a.75.75 0 0 0-.657.744Zm0 2.629c0 1.196.312 2.32.857 3.294A5.266 5.266 0 0 1 3.16 5.337a45.6 45.6 0 0 1 2.006-.343v.256Zm13.5 0v-.256c.674.1 1.343.214 2.006.343a5.265 5.265 0 0 1-2.863 3.207 6.72 6.72 0 0 0 .857-3.294Z" clip-rule="evenodd" />
            </svg>
            Победители
          </div>
          <div class="entry-list">
            <template v-for="entry in winners" :key="`${entry.kind}-${entry.id}`">
              <div v-if="entry.kind === 'team'" class="entry entry--winner" role="button" tabindex="0" @click="navigate(entry)" @keydown.enter="navigate(entry)">
                <div class="entry__icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18"><path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" /></svg>
                </div>
                <div class="entry__info">
                  <span class="entry__name">{{ entry.name }}</span>
                  <span class="entry__sub">{{ entry.memberCount }} участников · {{ entry.members.map((m) => m.name).join(', ') }}</span>
                </div>
                <span class="entry__medal entry__medal--gold">1</span>
              </div>
              <div v-else class="entry entry--winner" role="button" tabindex="0" @click="navigate(entry)" @keydown.enter="navigate(entry)">
                <div class="entry__avatar">
                  <img v-if="entry.avatar" :src="entry.avatar" :alt="entry.name" />
                  <span v-else>{{ initials(entry.name) }}</span>
                </div>
                <div class="entry__info">
                  <span class="entry__name">{{ entry.name }}</span>
                  <span v-if="entry.roles" class="entry__sub">{{ entry.roles }}</span>
                </div>
                <span class="entry__medal entry__medal--gold">1</span>
              </div>
            </template>
          </div>
        </div>

        <div v-if="prizeWinners.length" class="group">
          <div class="group__header group__header--silver">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
              <path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 0 1-.383-.218 25.18 25.18 0 0 1-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0 1 12 5.052 5.5 5.5 0 0 1 16.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 0 1-4.244 3.17 15.247 15.247 0 0 1-.383.219l-.022.012-.007.004-.003.001a.752.752 0 0 1-.704 0l-.003-.001Z" />
            </svg>
            Призёры
          </div>
          <div class="entry-list">
            <template v-for="entry in prizeWinners" :key="`${entry.kind}-${entry.id}`">
              <div v-if="entry.kind === 'team'" class="entry entry--prize" role="button" tabindex="0" @click="navigate(entry)" @keydown.enter="navigate(entry)">
                <div class="entry__icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18"><path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" /></svg>
                </div>
                <div class="entry__info">
                  <span class="entry__name">{{ entry.name }}</span>
                  <span class="entry__sub">{{ entry.memberCount }} участников · {{ entry.members.map((m) => m.name).join(', ') }}</span>
                </div>
                <span class="entry__medal entry__medal--silver">2</span>
              </div>
              <div v-else class="entry entry--prize" role="button" tabindex="0" @click="navigate(entry)" @keydown.enter="navigate(entry)">
                <div class="entry__avatar">
                  <img v-if="entry.avatar" :src="entry.avatar" :alt="entry.name" />
                  <span v-else>{{ initials(entry.name) }}</span>
                </div>
                <div class="entry__info">
                  <span class="entry__name">{{ entry.name }}</span>
                  <span v-if="entry.roles" class="entry__sub">{{ entry.roles }}</span>
                </div>
                <span class="entry__medal entry__medal--silver">2</span>
              </div>
            </template>
          </div>
        </div>

        <div v-if="participants.length" class="group">
          <div class="group__header">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
            </svg>
            Участники
          </div>
          <div class="entry-list">
            <template v-for="entry in participants" :key="`${entry.kind}-${entry.id}`">
              <div v-if="entry.kind === 'team'" class="entry entry--compact" role="button" tabindex="0" @click="navigate(entry)" @keydown.enter="navigate(entry)">
                <div class="entry__icon entry__icon--sm">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="14" height="14"><path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" /></svg>
                </div>
                <div class="entry__info">
                  <span class="entry__name">{{ entry.name }}</span>
                  <span class="entry__sub">{{ entry.memberCount }} участников</span>
                </div>
              </div>
              <div v-else class="entry entry--compact" role="button" tabindex="0" @click="navigate(entry)" @keydown.enter="navigate(entry)">
                <div class="entry__avatar entry__avatar--sm">
                  <img v-if="entry.avatar" :src="entry.avatar" :alt="entry.name" />
                  <span v-else>{{ initials(entry.name) }}</span>
                </div>
                <div class="entry__info">
                  <span class="entry__name">{{ entry.name }}</span>
                </div>
              </div>
            </template>
          </div>
        </div>
      </section>

      <div v-else class="state-empty">
        <p>Результаты ещё не опубликованы</p>
      </div>
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
  .event-page {
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

  .page-body {
    @include respond-to('lg') {
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 32px 64px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
  }

  .cover {
    position: relative;
    height: 220px;
    background: #1e1e1e;

    @include respond-to('lg') {
      height: 400px;
      border-radius: $radius-2xl;
      overflow: hidden;
    }
  }

  .cover__img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  .cover__placeholder {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
  }

  .cover__badge {
    position: absolute;
    bottom: 12px;
    left: 16px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    border-radius: $radius-full;
    background: rgba($color-bg, 0.85);
    backdrop-filter: blur(8px);
    font-size: 12px;
    font-weight: 600;
    color: $color-success;
    border: 1px solid rgba($color-success, 0.3);
  }

  .info {
    padding: 20px 16px;
    border-bottom: 1px solid $color-border;
    @include flex-column(8px);

    @include respond-to('lg') {
      padding: 28px 32px;
      background: #141417;
      border: 1px solid $color-border;
      border-radius: $radius-2xl;
    }
  }

  .info__title {
    margin: 0;
    font-size: 22px;
    font-weight: 800;
    line-height: 1.2;
  }

  .info__date {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: $color-text-secondary;

    svg { flex-shrink: 0; }
  }

  .info__description {
    margin: 4px 0 0;
    font-size: 14px;
    color: $color-text-secondary;
    line-height: 1.6;
  }

  .application {
    padding: 20px 16px;
    @include flex-column(10px);
    border-bottom: 1px solid $color-border;

    @include respond-to('lg') {
      padding: 28px 32px;
      background: #141417;
      border: 1px solid $color-border;
      border-radius: $radius-2xl;
    }
  }

  .application__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
  }

  .application__title {
    margin: 0;
    font-size: 17px;
    font-weight: 700;
  }

  .application__link {
    font-size: 13px;
    color: $color-text-secondary;
    text-decoration: none;
  }

  .application__grid {
    display: grid;
    gap: 8px;

    @include respond-to('lg') {
      grid-template-columns: 1fr 1fr;
    }
  }

  .application__field {
    width: 100%;
    padding: 10px 12px;
    border-radius: $radius-md;
    border: 1px solid $color-border;
    background: $color-surface;
    color: $color-text-primary;
    font-size: 14px;
    font-family: inherit;
    box-sizing: border-box;
  }

  .application__skills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .application__skill {
    border: 1px solid $color-border;
    border-radius: $radius-full;
    padding: 6px 10px;
    font-size: 13px;
    color: $color-text-secondary;
    background: transparent;
    cursor: pointer;
  }

  .application__skill--active {
    border-color: rgba($color-accent, 0.45);
    color: $color-accent;
    background: rgba($color-accent, 0.12);
  }

  .application__submit {
    align-self: flex-start;
    border: none;
    border-radius: $radius-full;
    padding: 8px 14px;
    background: $color-accent;
    color: #fff;
    font-weight: 600;
    cursor: pointer;
  }

  .application__error {
    margin: 0;
    color: #f87171;
    font-size: 13px;
  }

  .application__success {
    margin: 0;
    color: #34d399;
    font-size: 13px;
  }

  .ratings {
    padding: 20px 16px;
    @include flex-column(20px);

    @include respond-to('lg') {
      padding: 28px 32px;
      background: #141417;
      border: 1px solid $color-border;
      border-radius: $radius-2xl;
    }
  }

  .ratings__title {
    margin: 0;
    font-size: 17px;
    font-weight: 700;
  }

  .group {
    @include flex-column(8px);
  }

  .group__header {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: $color-text-secondary;

    &--gold  { color: $color-gold; }
    &--silver { color: $color-silver; }
  }

  .entry-list {
    @include flex-column(8px);
  }

  .entry {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    border-radius: $radius-xl;
    border: 1px solid $color-border;
    background: $color-surface;
    cursor: pointer;

    &--winner { border-color: rgba($color-gold, 0.35); background: rgba($color-gold, 0.06); }
    &--prize  { border-color: rgba($color-silver, 0.3); background: rgba($color-silver, 0.05); }
    &--compact { padding: 8px 12px; border-radius: $radius-md; }
  }

  .entry__avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: #2a2a2a;
    @include flex-center;
    font-size: 15px;
    font-weight: 700;
    color: $color-text-secondary;
    flex-shrink: 0;
    overflow: hidden;

    img { width: 100%; height: 100%; object-fit: cover; }
    &--sm { width: 36px; height: 36px; font-size: 12px; }
  }

  .entry__icon {
    width: 44px;
    height: 44px;
    border-radius: $radius-lg;
    background: rgba($color-accent, 0.12);
    border: 1px solid rgba($color-accent, 0.25);
    @include flex-center;
    color: $color-accent;
    flex-shrink: 0;

    &--sm { width: 36px; height: 36px; border-radius: $radius-md; }
  }

  .entry__info {
    flex: 1;
    @include flex-column(3px);
    min-width: 0;
  }

  .entry__name {
    font-size: 15px;
    font-weight: 600;
    @include text-ellipsis;
  }

  .entry__sub {
    font-size: 12px;
    color: $color-text-secondary;
    @include text-ellipsis;
  }

  .entry__medal {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    @include flex-center;
    font-size: 12px;
    font-weight: 800;
    flex-shrink: 0;

    &--gold   { background: rgba($color-gold, 0.2); color: $color-gold; border: 1px solid rgba($color-gold, 0.4); }
    &--silver { background: rgba($color-silver, 0.15); color: $color-silver; border: 1px solid rgba($color-silver, 0.3); }
  }

  .state-empty {
    padding: 48px 16px;
    text-align: center;
    color: $color-text-secondary;
    font-size: 14px;
  }

  .cover-skeleton {
    height: 220px;
    @include skeleton-shimmer;

    @include respond-to('lg') {
      height: 400px;
      border-radius: $radius-2xl;
    }
  }

  .info-skeleton {
    padding: 20px 16px;
    @include flex-column(10px);
  }

  .skel {
    border-radius: $radius-sm;
    @include skeleton-shimmer;

    &--badge { height: 24px; width: 120px; border-radius: $radius-full; }
    &--title { height: 28px; width: 75%; }
    &--line  { height: 14px; width: 50%; }
    &--short { width: 35%; }
  }
</style>
