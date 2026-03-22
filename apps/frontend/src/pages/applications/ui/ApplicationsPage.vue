<script setup lang="ts">
  import { computed, onMounted, reactive, ref } from 'vue'
  import { useRoute } from 'vue-router'

  import { participationApplicationApi } from '@entities/participation-application/api'
  import { eventApi } from '@entities/event/api'
  import { roleApi } from '@entities/role/api'
  import { skillApi } from '@entities/skill/api'
  import { authState } from '@shared/auth/session'
  import { formatDateLong } from '@shared/lib/format'
  import type {
    ApplicationStatus,
    EventResponse,
    ParticipationApplicationResponse,
    PreferredTeamFormat,
    RoleResponse,
    SkillResponse,
  } from '@shared/types/api'

  const route = useRoute()

  const filters = reactive({
    eventId: route.query.event_id ? Number(route.query.event_id) : undefined,
    status: (route.query.status as ApplicationStatus | undefined) ?? undefined,
    onlyMine: false,
    limit: 20,
    offset: 0,
  })

  const list = ref<ParticipationApplicationResponse[]>([])
  const total = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const createForm = reactive({
    eventId: route.query.event_id ? String(route.query.event_id) : '',
    desiredRole: '',
    preferredTeamFormat: 'team' as PreferredTeamFormat,
    comment: '',
    skillIds: [] as number[],
  })
  const isCreating = ref(false)
  const createError = ref<string | null>(null)

  const allEvents = ref<EventResponse[]>([])
  const allRoles = ref<RoleResponse[]>([])
  const allSkills = ref<SkillResponse[]>([])

  const isUpdatingId = ref<number | null>(null)
  const statusError = ref<string | null>(null)

  const statusOptions: ApplicationStatus[] = ['pending', 'approved', 'rejected']
  const statusLabels: Record<ApplicationStatus, string> = {
    pending: 'На рассмотрении',
    approved: 'Одобрена',
    rejected: 'Отклонена',
  }

  const currentUserId = computed(() => authState.currentUser.value?.id)
  const canPrev = computed(() => filters.offset > 0)
  const canNext = computed(() => filters.offset + filters.limit < total.value)
  const pageFrom = computed(() => (total.value === 0 ? 0 : filters.offset + 1))
  const pageTo = computed(() => Math.min(filters.offset + filters.limit, total.value))

  async function loadCatalogs(): Promise<void> {
    const [eventsRes, roles, skills] = await Promise.all([
      eventApi.getList({ limit: 100 }),
      roleApi.getList(),
      skillApi.getList(),
    ])
    allEvents.value = eventsRes.data
    allRoles.value = roles
    allSkills.value = skills
  }

  async function loadList(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const response = await participationApplicationApi.getList({
        limit: filters.limit,
        offset: filters.offset,
        event_id: filters.eventId,
        status: filters.status,
        applicant_user_id: filters.onlyMine && currentUserId.value ? currentUserId.value : undefined,
      })
      list.value = response.data
      total.value = response.total
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Не удалось загрузить заявки'
    } finally {
      isLoading.value = false
    }
  }

  async function createApplication(): Promise<void> {
    if (!createForm.eventId) {
      createError.value = 'Выберите хакатон'
      return
    }

    isCreating.value = true
    createError.value = null
    try {
      await participationApplicationApi.create({
        event_id: Number(createForm.eventId),
        desired_role: createForm.desiredRole,
        preferred_team_format: createForm.preferredTeamFormat,
        comment: createForm.comment,
        skill_ids: createForm.skillIds,
      })
      createForm.comment = ''
      createForm.skillIds = []
      filters.offset = 0
      await loadList()
    } catch (e) {
      createError.value = e instanceof Error ? e.message : 'Не удалось создать заявку'
    } finally {
      isCreating.value = false
    }
  }

  async function updateStatus(
    item: ParticipationApplicationResponse,
    status: ApplicationStatus,
  ): Promise<void> {
    if (item.status === status || isUpdatingId.value === item.id) return

    statusError.value = null
    isUpdatingId.value = item.id
    try {
      await participationApplicationApi.updateStatus(item.id, { status })
      await loadList()
    } catch (e) {
      statusError.value = e instanceof Error ? e.message : 'Не удалось обновить статус заявки'
    } finally {
      isUpdatingId.value = null
    }
  }

  function toggleSkill(id: number): void {
    const index = createForm.skillIds.indexOf(id)
    if (index === -1) createForm.skillIds.push(id)
    else createForm.skillIds.splice(index, 1)
  }

  function submitFilters(): void {
    filters.offset = 0
    void loadList()
  }

  function prevPage(): void {
    if (!canPrev.value) return
    filters.offset = Math.max(0, filters.offset - filters.limit)
    void loadList()
  }

  function nextPage(): void {
    if (!canNext.value) return
    filters.offset += filters.limit
    void loadList()
  }

  onMounted(async () => {
    await loadCatalogs()
    await loadList()
  })
</script>

<template>
  <div class="applications-page">
    <div class="edit-bar">
      <div class="edit-bar__inner">
        <RouterLink :to="{ name: 'profile' }" class="edit-link">Профиль</RouterLink>
        <RouterLink :to="{ name: 'teammates' }" class="edit-link">Сокомандники</RouterLink>
        <RouterLink :to="{ name: 'applications' }" class="edit-link">Заявки</RouterLink>
      </div>
    </div>

    <div class="applications-body">
      <aside class="applications-sidebar">
        <section class="sidebar-section">
          <h1 class="section-title">Новая заявка</h1>

          <div class="form-grid">
            <select v-model="createForm.eventId" class="field" :disabled="isCreating">
              <option value="">Выберите хакатон</option>
              <option v-for="event in allEvents" :key="event.id" :value="String(event.id)">
                {{ event.title }} · {{ formatDateLong(event.date) }}
              </option>
            </select>

            <select v-model="createForm.desiredRole" class="field" :disabled="isCreating">
              <option value="">Желаемая роль</option>
              <option v-for="role in allRoles" :key="role.id" :value="role.name">{{ role.name }}</option>
            </select>

            <select v-model="createForm.preferredTeamFormat" class="field" :disabled="isCreating">
              <option value="team">Хочу в команду</option>
              <option value="solo">Рассматриваю solo</option>
            </select>

            <textarea
              v-model="createForm.comment"
              class="field"
              rows="3"
              placeholder="Комментарий о вашем опыте и ожиданиях"
              :disabled="isCreating"
            />
          </div>

          <div class="chips">
            <button
              v-for="skill in allSkills"
              :key="skill.id"
              type="button"
              class="chip"
              :class="{ 'chip--active': createForm.skillIds.includes(skill.id) }"
              :disabled="isCreating"
              @click="toggleSkill(skill.id)"
            >
              {{ skill.name }}
            </button>
          </div>

          <p v-if="createError" class="error">{{ createError }}</p>

          <button type="button" class="btn" :disabled="isCreating" @click="createApplication">
            {{ isCreating ? 'Отправляем…' : 'Оставить заявку' }}
          </button>
        </section>

        <section class="sidebar-section">
          <h2 class="section-subtitle">Фильтры списка</h2>

          <div class="form-grid">
            <select v-model="filters.eventId" class="field" :disabled="isLoading">
              <option :value="undefined">Все хакатоны</option>
              <option v-for="event in allEvents" :key="event.id" :value="event.id">{{ event.title }}</option>
            </select>

            <select v-model="filters.status" class="field" :disabled="isLoading">
              <option :value="undefined">Все статусы</option>
              <option v-for="status in statusOptions" :key="status" :value="status">{{ statusLabels[status] }}</option>
            </select>
          </div>

          <label class="checkbox-row">
            <input v-model="filters.onlyMine" type="checkbox" :disabled="isLoading" />
            Только мои заявки
          </label>

          <button type="button" class="btn btn--ghost" :disabled="isLoading" @click="submitFilters">Применить</button>
        </section>
      </aside>

      <main class="applications-main">
        <section class="main-section">
          <p v-if="error" class="error">{{ error }}</p>
          <p v-else class="summary">Показаны {{ pageFrom }}-{{ pageTo }} из {{ total }}</p>

          <p v-if="statusError" class="error">{{ statusError }}</p>

          <section v-if="isLoading" class="state">Загрузка...</section>
          <section v-else-if="list.length === 0" class="state">Список пуст</section>

          <section v-else class="list">
            <article v-for="item in list" :key="item.id" class="card">
              <div class="row">
                <strong>#{{ item.id }}</strong>
                <span class="status" :class="`status--${item.status}`">{{ statusLabels[item.status] }}</span>
              </div>

              <p class="title">
                {{ allEvents.find((event) => event.id === item.event_id)?.title ?? 'Event #' + item.event_id }}
              </p>
              <p>Кандидат: {{ item.applicant?.name ?? 'User #' + item.applicant_user_id }}</p>
              <p v-if="item.desired_role">Роль: {{ item.desired_role }}</p>
              <p>Формат: {{ item.preferred_team_format === 'solo' ? 'Solo' : 'Команда' }}</p>
              <p v-if="item.comment">{{ item.comment }}</p>
              <p v-if="item.skills.length" class="meta">
                Навыки: {{ item.skills.map((skill) => skill.name).join(', ') }}
              </p>

              <div class="actions">
                <button
                  type="button"
                  class="btn btn--ghost"
                  :disabled="isLoading || isUpdatingId === item.id"
                  @click="updateStatus(item, 'pending')"
                >
                  На рассмотрении
                </button>
                <button
                  type="button"
                  class="btn btn--ghost"
                  :disabled="isLoading || isUpdatingId === item.id"
                  @click="updateStatus(item, 'approved')"
                >
                  Одобрить
                </button>
                <button
                  type="button"
                  class="btn btn--ghost"
                  :disabled="isLoading || isUpdatingId === item.id"
                  @click="updateStatus(item, 'rejected')"
                >
                  Отклонить
                </button>
              </div>
            </article>
          </section>

          <footer class="pager">
            <button type="button" class="btn btn--ghost" :disabled="isLoading || !canPrev" @click="prevPage">Назад</button>
            <button type="button" class="btn btn--ghost" :disabled="isLoading || !canNext" @click="nextPage">Вперёд</button>
          </footer>
        </section>
      </main>
    </div>
  </div>
</template>

<style scoped lang="scss">
  .applications-page {
    @include page-root;
  }

  .edit-bar {
    display: flex;
    justify-content: flex-end;
    padding: 10px 16px 0;
    border-bottom: 1px solid $color-border;

    @include respond-to('lg') {
      padding: 0;
      border-bottom: none;
    }
  }

  .edit-bar__inner {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    padding: 10px 0 10px;

    @include respond-to('lg') {
      max-width: 1200px;
      width: 100%;
      margin: 0 auto;
      padding: 14px 32px;
      border-bottom: 1px solid $color-border;
    }
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
    transition: border-color $transition-fast, color $transition-fast, background-color $transition-fast;

    &:hover {
      border-color: $color-accent;
      color: $color-accent;
      text-decoration: none;
    }

    &.router-link-exact-active {
      border-color: rgba($color-accent, 0.45);
      background: rgba($color-accent, 0.12);
      color: $color-accent;
    }
  }

  .applications-body {
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

  .applications-sidebar {
    display: flex;
    flex-direction: column;
    gap: 20px;

    @include respond-to('lg') {
      width: 360px;
      flex-shrink: 0;
      gap: 16px;
    }
  }

  .sidebar-section {
    background: #1a1a1d;
    border: 1px solid rgba($color-accent, 0.2);
    border-radius: $radius-2xl;
    padding: 20px;
    display: grid;
    gap: 12px;
  }

  .section-title,
  .section-subtitle {
    margin: 0;
    font-size: 18px;
    line-height: 1.25;
  }

  .section-subtitle {
    font-size: 16px;
  }

  .form-grid {
    display: grid;
    gap: 10px;
  }

  .field {
    border: 1px solid $color-border;
    border-radius: $radius-md;
    background: $color-surface;
    color: $color-text-primary;
    padding: 9px 12px;
  }

  .checkbox-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: $color-text-secondary;
  }

  .chips {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .chip {
    border: 1px solid $color-border;
    border-radius: $radius-full;
    padding: 6px 10px;
    background: transparent;
    color: $color-text-primary;
    cursor: pointer;
    transition: border-color $transition-fast, background-color $transition-fast, color $transition-fast;

    &:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }
  }

  .chip--active {
    border-color: rgba($color-accent, 0.5);
    background: rgba($color-accent, 0.16);
  }

  .btn {
    border: 1px solid transparent;
    border-radius: $radius-md;
    padding: 8px 12px;
    background: $color-accent;
    color: #0f0f11;
    font-weight: 600;
    cursor: pointer;
    width: fit-content;
    transition: border-color $transition-fast, color $transition-fast, opacity $transition-fast;

    &:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }
  }

  .btn--ghost {
    background: transparent;
    border-color: $color-border;
    color: $color-text-primary;
  }

  .applications-main {
    min-width: 0;

    @include respond-to('lg') {
      flex: 1;
    }
  }

  .main-section {
    background: #141417;
    border: 1px solid $color-border;
    border-radius: $radius-2xl;
    padding: 20px;
    display: grid;
    gap: 12px;

    @include respond-to('lg') {
      padding: 28px 32px;
      gap: 16px;
    }
  }

  .error {
    margin: 0;
    color: #ff8787;
  }

  .summary {
    margin: 0;
    color: $color-text-secondary;
  }

  .state {
    border: 1px dashed $color-border;
    border-radius: $radius-md;
    padding: 16px;
    color: $color-text-secondary;
  }

  .list {
    display: grid;
    gap: 12px;
  }

  .card {
    border: 1px solid $color-border;
    border-radius: $radius-xl;
    padding: 14px;
    background: #141417;

    p {
      margin: 6px 0 0;
    }
  }

  .row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }

  .title {
    font-weight: 700;
  }

  .status {
    border-radius: $radius-full;
    padding: 4px 8px;
    font-size: 12px;
    border: 1px solid $color-border;
  }

  .status--pending {
    border-color: #9aa2b1;
    color: #c4cad6;
  }

  .status--approved {
    border-color: #3ca25f;
    color: #6fe58f;
  }

  .status--rejected {
    border-color: #a23c3c;
    color: #f09191;
  }

  .meta {
    color: $color-text-secondary;
    font-size: 13px;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
  }

  .pager {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }
</style>
