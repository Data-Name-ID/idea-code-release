<script setup lang="ts">
  import { computed, onMounted, reactive, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  import { teamApi } from '@entities/team/api'
  import { eventApi } from '@entities/event/api'
  import { authState } from '@shared/auth/session'
  import { formatDateLong, initials } from '@shared/lib/format'
  import type { LinkRequest, UserResponse } from '@shared/types/api'
  import type { ActivityFilter, ActivityItem } from '@widgets/ActivityFeed/model/types'

  import UserProfileCard from '@widgets/UserProfileCard/ui/UserProfileCard.vue'
  import ProfileContactsCard from '@widgets/ProfileContactsCard/ui/ProfileContactsCard.vue'
  import ActivityFeed from '@widgets/ActivityFeed/ui/ActivityFeed.vue'

  const route = useRoute()
  const router = useRouter()

  const teamId = computed(() => Number(route.params.id))
  const currentUser = computed(() => authState.currentUser.value)

  const team = ref<Awaited<ReturnType<typeof teamApi.getById>> | null>(null)
  const isLoading = ref(true)
  const error = ref<string | null>(null)

  const activityItems = ref<ActivityItem[]>([])
  const activityFilter = ref<ActivityFilter>('all')
  const isLoadingActivity = ref(false)

  const actionError = ref<string | null>(null)
  const actionSuccess = ref<string | null>(null)

  const showEditForm = ref(false)
  const isSavingProfile = ref(false)
  const editForm = reactive({
    name: '',
    description: '',
    avatar: '',
    location: '',
    links: [] as LinkRequest[],
  })

  const inviteExpiresInHours = ref(72)
  const isCreatingInvite = ref(false)
  const inviteUrl = ref('')
  const inviteExpiresAt = ref<string | null>(null)

  const transferToUserId = ref('')
  const isTransferringCaptain = ref(false)
  const isLeavingTeam = ref(false)
  const removingMemberId = ref<number | null>(null)

  const isCaptain = computed(
    () =>
      team.value !== null &&
      currentUser.value !== null &&
      team.value.captain_user_id === currentUser.value.id,
  )

  const isMember = computed(
    () =>
      team.value !== null &&
      currentUser.value !== null &&
      team.value.users.some((u) => u.id === currentUser.value?.id),
  )

  const captainName = computed(() => {
    if (!team.value || team.value.captain_user_id == null) return null
    const captain = team.value.users.find((u) => u.id === team.value?.captain_user_id)
    return captain?.name ?? null
  })

  const winCount = computed(
    () => activityItems.value.filter((item) => item.status === 'winner' || item.status === 'prize_winner').length,
  )

  const captainCandidates = computed(() => {
    if (!team.value) return []
    return team.value.users.filter((u) => u.id !== team.value?.captain_user_id)
  })

  const teamAsProfileUser = computed<UserResponse | null>(() => {
    if (!team.value) return null
    return {
      id: team.value.id,
      username: `team_${team.value.id}`,
      email: null,
      name: team.value.name,
      avatar: team.value.avatar,
      description: team.value.description,
      location: team.value.location,
      links: team.value.links,
      roles: [],
      skills: [],
    }
  })

  onMounted(() => {
    loadTeam()
  })

  watch(
    () => team.value,
    (value) => {
      if (!value) return
      editForm.name = value.name
      editForm.description = value.description
      editForm.avatar = value.avatar ?? ''
      editForm.location = value.location ?? ''
      editForm.links = value.links.map((link) => ({ url: link.url, label: link.label }))
    },
    { immediate: true },
  )

  async function loadTeam(): Promise<void> {
    isLoading.value = true
    error.value = null
    actionError.value = null
    actionSuccess.value = null

    try {
      const loadedTeam = await teamApi.getById(teamId.value)
      team.value = loadedTeam
      await loadTeamActivity(loadedTeam)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Не удалось загрузить команду'
    } finally {
      isLoading.value = false
    }
  }

  async function loadTeamActivity(teamData: NonNullable<typeof team.value>): Promise<void> {
    isLoadingActivity.value = true
    try {
      const ratingsByEvent = await Promise.all(
        teamData.events.map((event) => eventApi.getRatings(event.id).catch((): null => null)),
      )

      activityItems.value = teamData.events
        .map((event, index) => {
          const ratings = ratingsByEvent[index]
          const teamEntry = ratings?.ratings.find((r) => r.team_id === teamData.id) ?? null
          return {
            event,
            status: teamEntry?.status ?? null,
            teamName: teamData.name,
          } satisfies ActivityItem
        })
        .sort((a, b) => new Date(b.event.date).getTime() - new Date(a.event.date).getTime())
    } finally {
      isLoadingActivity.value = false
    }
  }

  function resetMessages(): void {
    actionError.value = null
    actionSuccess.value = null
  }

  function addLink(): void {
    editForm.links.push({ url: '', label: '' })
  }

  function removeLink(index: number): void {
    editForm.links.splice(index, 1)
  }

  async function saveTeamProfile(): Promise<void> {
    if (!team.value) return
    resetMessages()
    isSavingProfile.value = true
    try {
      const updated = await teamApi.update(team.value.id, {
        name: editForm.name || null,
        description: editForm.description || null,
        avatar: editForm.avatar || null,
        location: editForm.location || null,
        links: editForm.links.filter((link) => link.url.trim()),
      })
      team.value = updated
      actionSuccess.value = 'Профиль команды обновлён'
      showEditForm.value = false
    } catch (e) {
      actionError.value = e instanceof Error ? e.message : 'Не удалось сохранить изменения'
    } finally {
      isSavingProfile.value = false
    }
  }

  async function generateInvite(): Promise<void> {
    if (!team.value) return
    resetMessages()
    isCreatingInvite.value = true
    try {
      const invite = await teamApi.createInvite(team.value.id, {
        expires_in_hours: inviteExpiresInHours.value,
      })
      const url = new URL('/teams/join', window.location.origin)
      url.searchParams.set('token', invite.token)
      inviteUrl.value = url.toString()
      inviteExpiresAt.value = invite.expires_at
      actionSuccess.value = 'Ссылка приглашения создана'
    } catch (e) {
      actionError.value = e instanceof Error ? e.message : 'Не удалось создать приглашение'
    } finally {
      isCreatingInvite.value = false
    }
  }

  async function copyInviteLink(): Promise<void> {
    if (!inviteUrl.value) return
    resetMessages()
    try {
      await navigator.clipboard.writeText(inviteUrl.value)
      actionSuccess.value = 'Ссылка скопирована'
    } catch {
      actionError.value = 'Не удалось скопировать ссылку'
    }
  }

  async function removeMember(userId: number): Promise<void> {
    if (!team.value) return
    resetMessages()
    removingMemberId.value = userId
    try {
      team.value = await teamApi.removeMember(team.value.id, userId)
      actionSuccess.value = 'Участник удалён из команды'
    } catch (e) {
      actionError.value = e instanceof Error ? e.message : 'Не удалось удалить участника'
    } finally {
      removingMemberId.value = null
    }
  }

  async function transferCaptain(): Promise<void> {
    const parsedUserId = Number(transferToUserId.value)
    if (!team.value || !Number.isInteger(parsedUserId)) return
    resetMessages()
    isTransferringCaptain.value = true
    try {
      team.value = await teamApi.transferCaptain(team.value.id, {
        new_captain_user_id: parsedUserId,
      })
      transferToUserId.value = ''
      actionSuccess.value = 'Капитанство передано'
    } catch (e) {
      actionError.value = e instanceof Error ? e.message : 'Не удалось передать капитанство'
    } finally {
      isTransferringCaptain.value = false
    }
  }

  async function leaveTeam(): Promise<void> {
    if (!team.value) return
    resetMessages()
    isLeavingTeam.value = true
    try {
      await teamApi.leave(team.value.id)
      await router.replace({ name: 'profile' })
    } catch (e) {
      actionError.value = e instanceof Error ? e.message : 'Не удалось выйти из команды'
    } finally {
      isLeavingTeam.value = false
    }
  }
</script>

<template>
  <div class="team-page">
    <header class="page-header">
      <button class="back-btn" @click="router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
      </button>
      <span class="page-header__title">Команда</span>
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

    <template v-else-if="team && teamAsProfileUser">
      <div class="profile-body">
        <aside class="profile-sidebar">
          <div class="sidebar-card">
            <UserProfileCard
              :user="teamAsProfileUser"
              :hackathon-count="team.events.length"
              :win-count="winCount"
            />
          </div>
          <div class="sidebar-section">
            <div class="captain-box">
              <p class="captain-box__label">Капитан</p>
              <p class="captain-box__name">{{ captainName ?? 'Не назначен' }}</p>
            </div>
          </div>
        </aside>

        <main class="profile-main">
          <div v-if="actionError" class="alert alert--error">{{ actionError }}</div>
          <div v-if="actionSuccess" class="alert alert--success">{{ actionSuccess }}</div>

          <div class="main-section">
            <ProfileContactsCard
              title="Контакты и ссылки команды"
              :location="team.location"
              :links="team.links"
              empty-text="Контактные данные команды не заполнены"
            />
          </div>

          <div class="main-section">
            <ActivityFeed
              :items="activityItems"
              :is-loading="isLoadingActivity"
              :active-filter="activityFilter"
              @filter-change="activityFilter = $event"
              @navigate-to-event="(id) => router.push(`/events/${id}`)"
            />
          </div>

          <div class="main-section">
            <div class="section-head">
              <h2 class="section-title">Участники</h2>
              <span class="section-caption">{{ team.users.length }} в составе</span>
            </div>

            <div class="member-list">
              <div v-for="member in team.users" :key="member.id" class="member-card">
                <div class="member-card__profile" role="button" tabindex="0" @click="router.push(`/users/${member.id}`)" @keydown.enter="router.push(`/users/${member.id}`)">
                  <div class="member-card__avatar">
                    <img v-if="member.avatar" :src="member.avatar" :alt="member.name" />
                    <span v-else>{{ initials(member.name) }}</span>
                  </div>
                  <div class="member-card__info">
                    <p class="member-card__name">{{ member.name }}</p>
                    <p v-if="member.roles.length" class="member-card__roles">
                      {{ member.roles.map((r) => r.name).join(' · ') }}
                    </p>
                    <span
                      v-if="member.id === team.captain_user_id"
                      class="member-card__badge"
                    >
                      Капитан
                    </span>
                  </div>
                </div>

                <button
                  v-if="isCaptain && member.id !== team.captain_user_id"
                  class="danger-btn"
                  :disabled="removingMemberId === member.id"
                  @click="removeMember(member.id)"
                >
                  {{ removingMemberId === member.id ? 'Удаляем…' : 'Удалить' }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="isCaptain" class="main-section">
            <div class="section-head">
              <h2 class="section-title">Управление командой</h2>
            </div>

            <div class="management">
              <button class="secondary-btn" @click="showEditForm = !showEditForm">
                {{ showEditForm ? 'Скрыть форму редактирования' : 'Редактировать профиль команды' }}
              </button>

              <form v-if="showEditForm" class="edit-form" @submit.prevent="saveTeamProfile">
                <label class="field">
                  <span class="field__label">Название</span>
                  <input v-model="editForm.name" type="text" class="field__input" required />
                </label>

                <label class="field">
                  <span class="field__label">Описание</span>
                  <textarea
                    v-model="editForm.description"
                    class="field__input field__input--textarea"
                    rows="3"
                  />
                </label>

                <label class="field">
                  <span class="field__label">URL аватара</span>
                  <input v-model="editForm.avatar" type="url" class="field__input" />
                </label>

                <label class="field">
                  <span class="field__label">Локация</span>
                  <input v-model="editForm.location" type="text" class="field__input" />
                </label>

                <div class="field">
                  <span class="field__label">Ссылки</span>
                  <div v-for="(link, index) in editForm.links" :key="index" class="link-row">
                    <input v-model="editForm.links[index].url" type="url" class="field__input" placeholder="https://..." />
                    <input v-model="editForm.links[index].label" type="text" class="field__input" placeholder="Название" />
                    <button type="button" class="remove-btn" @click="removeLink(index)">
                      Удалить
                    </button>
                  </div>
                  <button type="button" class="secondary-btn" @click="addLink">
                    + Добавить ссылку
                  </button>
                </div>

                <button type="submit" class="primary-btn" :disabled="isSavingProfile">
                  {{ isSavingProfile ? 'Сохраняем…' : 'Сохранить изменения' }}
                </button>
              </form>

              <div class="invite-box">
                <label class="field">
                  <span class="field__label">Время жизни ссылки (часы)</span>
                  <input
                    v-model.number="inviteExpiresInHours"
                    type="number"
                    min="1"
                    max="720"
                    class="field__input"
                  />
                </label>
                <button class="primary-btn" :disabled="isCreatingInvite" @click="generateInvite">
                  {{ isCreatingInvite ? 'Создаём…' : 'Создать ссылку приглашения' }}
                </button>
                <div v-if="inviteUrl" class="invite-result">
                  <p class="invite-result__label">
                    Ссылка активна до {{ inviteExpiresAt ? formatDateLong(inviteExpiresAt) : 'указанного времени' }}
                  </p>
                  <div class="invite-result__row">
                    <input :value="inviteUrl" class="field__input" readonly />
                    <button class="secondary-btn" @click="copyInviteLink">Копировать</button>
                  </div>
                </div>
              </div>

              <div class="transfer-box">
                <label class="field">
                  <span class="field__label">Передать капитанство</span>
                  <select v-model="transferToUserId" class="field__input">
                    <option value="" disabled>Выберите участника</option>
                    <option
                      v-for="member in captainCandidates"
                      :key="member.id"
                      :value="String(member.id)"
                    >
                      {{ member.name }}
                    </option>
                  </select>
                </label>
                <button
                  class="danger-btn"
                  :disabled="!transferToUserId || isTransferringCaptain"
                  @click="transferCaptain"
                >
                  {{ isTransferringCaptain ? 'Передаём…' : 'Передать капитанство' }}
                </button>
              </div>
            </div>
          </div>

          <div v-else-if="isMember" class="main-section">
            <div class="section-head">
              <h2 class="section-title">Участие в команде</h2>
            </div>
            <button class="danger-btn" :disabled="isLeavingTeam" @click="leaveTeam">
              {{ isLeavingTeam ? 'Выходим…' : 'Выйти из команды' }}
            </button>
          </div>
        </main>
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
  .team-page {
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
      padding: 16px;
    }
  }

  .captain-box {
    @include flex-column(4px);
  }

  .captain-box__label {
    margin: 0;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: $color-text-secondary;
  }

  .captain-box__name {
    margin: 0;
    font-size: 16px;
    font-weight: 700;
  }

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

  .section-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
  }

  .section-title {
    margin: 0;
    font-size: 17px;
    font-weight: 700;
  }

  .section-caption {
    font-size: 13px;
    color: $color-text-secondary;
  }

  .alert {
    border-radius: $radius-md;
    padding: 10px 14px;
    font-size: 14px;
  }

  .alert--error {
    background: rgba($color-danger, 0.15);
    border: 1px solid rgba($color-danger, 0.4);
    color: #f87171;
  }

  .alert--success {
    background: rgba($color-accent, 0.15);
    border: 1px solid rgba($color-accent, 0.4);
    color: #9ce6b3;
  }

  .member-list {
    @include flex-column(10px);
  }

  .member-card {
    border: 1px solid $color-border;
    border-radius: $radius-xl;
    padding: 12px;
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: center;
  }

  .member-card__profile {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
    flex: 1;
  }

  .member-card__avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    overflow: hidden;
    background: #2a2a2a;
    @include flex-center;
    font-weight: 700;
    color: $color-text-secondary;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .member-card__info {
    min-width: 0;
  }

  .member-card__name {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
  }

  .member-card__roles {
    margin: 2px 0 0;
    font-size: 13px;
    color: $color-text-secondary;
  }

  .member-card__badge {
    display: inline-block;
    margin-top: 6px;
    font-size: 11px;
    font-weight: 600;
    color: $color-accent;
    border: 1px solid rgba($color-accent, 0.6);
    border-radius: $radius-full;
    padding: 3px 8px;
  }

  .management {
    @include flex-column(14px);
  }

  .edit-form {
    @include flex-column(12px);
    border: 1px solid $color-border;
    border-radius: $radius-xl;
    padding: 14px;
  }

  .field {
    @include flex-column(6px);
  }

  .field__label {
    font-size: 13px;
    color: $color-text-secondary;
  }

  .field__input {
    width: 100%;
    padding: 10px 12px;
    border-radius: $radius-md;
    border: 1px solid $color-border;
    background: #0f1012;
    color: $color-text-primary;
    font-size: 14px;
    transition: border-color $transition-fast;

    &:focus {
      outline: none;
      border-color: $color-accent;
    }
  }

  .field__input--textarea {
    resize: vertical;
    min-height: 88px;
  }

  .link-row {
    display: grid;
    grid-template-columns: 1fr 1fr auto;
    gap: 8px;
  }

  .primary-btn,
  .secondary-btn,
  .danger-btn {
    border: 1px solid transparent;
    border-radius: $radius-full;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity $transition-fast, border-color $transition-fast, color $transition-fast;

    &:disabled {
      opacity: 0.5;
      cursor: wait;
    }
  }

  .primary-btn {
    background: $color-accent;
    color: #fff;
  }

  .secondary-btn {
    border-color: $color-border;
    background: transparent;
    color: $color-text-primary;
  }

  .danger-btn {
    border-color: rgba($color-danger, 0.5);
    background: rgba($color-danger, 0.1);
    color: #f87171;
  }

  .remove-btn {
    border: 1px solid $color-border;
    border-radius: $radius-md;
    background: transparent;
    color: $color-text-secondary;
    font-size: 12px;
    padding: 0 10px;
    cursor: pointer;
  }

  .invite-box,
  .transfer-box {
    border: 1px solid $color-border;
    border-radius: $radius-xl;
    padding: 14px;
    @include flex-column(10px);
  }

  .invite-result__label {
    margin: 0;
    font-size: 12px;
    color: $color-text-secondary;
  }

  .invite-result__row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 8px;
    align-items: center;
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
