<script setup lang="ts">
  import { computed, onMounted, reactive, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

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
  const router = useRouter()

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

  const statusOptions: ApplicationStatus[] = ['pending', 'approved', 'rejected']

  const currentUserId = computed(() => authState.currentUser.value?.id)
  const canPrev = computed(() => filters.offset > 0)
  const canNext = computed(() => filters.offset + filters.limit < total.value)

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
    if (item.status === status) return
    await participationApplicationApi.updateStatus(item.id, { status })
    await loadList()
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
    <header class="page-header">
      <button class="back-btn" @click="router.back()">Назад</button>
      <h1 class="page-title">Заявки на участие</h1>
      <RouterLink class="action-link" to="/teammates">Сокомандники</RouterLink>
    </header>

    <section class="panel">
      <h2>Новая заявка</h2>

      <div class="grid-two">
        <select v-model="createForm.eventId" class="field">
          <option value="">Выберите хакатон</option>
          <option v-for="event in allEvents" :key="event.id" :value="String(event.id)">
            {{ event.title }} · {{ formatDateLong(event.date) }}
          </option>
        </select>

        <select v-model="createForm.desiredRole" class="field">
          <option value="">Желаемая роль</option>
          <option v-for="role in allRoles" :key="role.id" :value="role.name">{{ role.name }}</option>
        </select>
      </div>

      <select v-model="createForm.preferredTeamFormat" class="field">
        <option value="team">Хочу в команду</option>
        <option value="solo">Рассматриваю solo</option>
      </select>

      <textarea
        v-model="createForm.comment"
        class="field"
        rows="3"
        placeholder="Комментарий о вашем опыте и ожиданиях"
      />

      <div class="chips">
        <button
          v-for="skill in allSkills"
          :key="skill.id"
          type="button"
          class="chip"
          :class="{ 'chip--active': createForm.skillIds.includes(skill.id) }"
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

    <section class="panel">
      <h2>Фильтры списка</h2>
      <div class="grid-two">
        <select v-model="filters.eventId" class="field">
          <option :value="undefined">Все хакатоны</option>
          <option v-for="event in allEvents" :key="event.id" :value="event.id">{{ event.title }}</option>
        </select>

        <select v-model="filters.status" class="field">
          <option :value="undefined">Все статусы</option>
          <option v-for="status in statusOptions" :key="status" :value="status">{{ status }}</option>
        </select>
      </div>

      <label class="checkbox-row">
        <input v-model="filters.onlyMine" type="checkbox" />
        Только мои заявки
      </label>

      <button type="button" class="btn btn--ghost" @click="submitFilters">Применить</button>
    </section>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-else class="summary">Всего заявок: {{ total }}</p>

    <section v-if="isLoading" class="state">Загрузка...</section>
    <section v-else-if="list.length === 0" class="state">Список пуст</section>

    <section v-else class="list">
      <article v-for="item in list" :key="item.id" class="card">
        <div class="row">
          <strong>#{{ item.id }}</strong>
          <span class="status" :class="`status--${item.status}`">{{ item.status }}</span>
        </div>
        <p class="title">
          {{ allEvents.find((event) => event.id === item.event_id)?.title ?? `Event #${item.event_id}` }}
        </p>
        <p>Кандидат: {{ item.applicant?.name ?? `User #${item.applicant_user_id}` }}</p>
        <p v-if="item.desired_role">Роль: {{ item.desired_role }}</p>
        <p>Формат: {{ item.preferred_team_format }}</p>
        <p v-if="item.comment">{{ item.comment }}</p>
        <p v-if="item.skills.length" class="meta">
          Навыки: {{ item.skills.map((skill) => skill.name).join(', ') }}
        </p>

        <div class="actions">
          <button type="button" class="btn btn--ghost" @click="updateStatus(item, 'pending')">pending</button>
          <button type="button" class="btn btn--ghost" @click="updateStatus(item, 'approved')">approved</button>
          <button type="button" class="btn btn--ghost" @click="updateStatus(item, 'rejected')">rejected</button>
        </div>
      </article>
    </section>

    <footer class="pager">
      <button type="button" class="btn btn--ghost" :disabled="!canPrev" @click="prevPage">Назад</button>
      <button type="button" class="btn btn--ghost" :disabled="!canNext" @click="nextPage">Вперёд</button>
    </footer>
  </div>
</template>

<style scoped lang="scss">
  .applications-page {
    @include page-root;
    padding: 16px;
    display: grid;
    gap: 12px;

    @include respond-to('lg') {
      max-width: 1100px;
      margin: 0 auto;
      padding: 28px;
    }
  }

  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
  }

  .page-title {
    margin: 0;
    font-size: 22px;
  }

  .back-btn,
  .action-link {
    border: 1px solid $color-border;
    border-radius: $radius-md;
    padding: 6px 10px;
    background: transparent;
    color: $color-text-secondary;
    text-decoration: none;
  }

  .panel {
    border: 1px solid $color-border;
    border-radius: $radius-lg;
    padding: 12px;
    display: grid;
    gap: 8px;

    h2 {
      margin: 0;
      font-size: 16px;
    }
  }

  .grid-two {
    display: grid;
    gap: 8px;

    @include respond-to('lg') {
      grid-template-columns: 1fr 1fr;
    }
  }

  .field {
    border: 1px solid $color-border;
    border-radius: $radius-md;
    background: $color-surface;
    color: $color-text-primary;
    padding: 8px 10px;
  }

  .checkbox-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
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
    justify-self: flex-start;
  }

  .btn--ghost {
    background: transparent;
    border-color: $color-border;
    color: $color-text-primary;
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
    padding: 14px;
    color: $color-text-secondary;
  }

  .list {
    display: grid;
    gap: 10px;
  }

  .card {
    border: 1px solid $color-border;
    border-radius: $radius-lg;
    padding: 12px;
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
    gap: 8px;
    margin-top: 10px;
  }

  .pager {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }
</style>
