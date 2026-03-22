<script setup lang="ts">
  import { computed, onMounted, reactive, ref } from 'vue'
  import { useRoute } from 'vue-router'

  import { participationApplicationApi } from '@entities/participation-application/api'
  import { eventApi } from '@entities/event/api'
  import { roleApi } from '@entities/role/api'
  import { skillApi } from '@entities/skill/api'
  import { authState } from '@shared/auth/session'
  import { formatDateLong } from '@shared/lib/format'
  import {
    BaseButton,
    BaseCard,
    BaseCheckbox,
    BaseSelect,
    BaseStatusMessage,
    BaseTextarea,
  } from '@shared/ui'
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
            <BaseSelect v-model="createForm.eventId" :disabled="isCreating">
              <option value="">Выберите хакатон</option>
              <option v-for="event in allEvents" :key="event.id" :value="String(event.id)">
                {{ event.title }} · {{ formatDateLong(event.date) }}
              </option>
            </BaseSelect>

            <BaseSelect v-model="createForm.desiredRole" :disabled="isCreating">
              <option value="">Желаемая роль</option>
              <option v-for="role in allRoles" :key="role.id" :value="role.name">{{ role.name }}</option>
            </BaseSelect>

            <BaseSelect v-model="createForm.preferredTeamFormat" :disabled="isCreating">
              <option value="team">Хочу в команду</option>
              <option value="solo">Рассматриваю solo</option>
            </BaseSelect>

            <BaseTextarea
              v-model="createForm.comment"
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

          <BaseStatusMessage v-if="createError" tone="error">{{ createError }}</BaseStatusMessage>

          <BaseButton type="button" :loading="isCreating" @click="createApplication">
            {{ isCreating ? 'Отправляем…' : 'Оставить заявку' }}
          </BaseButton>
        </section>

        <section class="sidebar-section">
          <h2 class="section-subtitle">Фильтры списка</h2>

          <div class="form-grid">
            <BaseSelect v-model="filters.eventId" :disabled="isLoading">
              <option :value="undefined">Все хакатоны</option>
              <option v-for="event in allEvents" :key="event.id" :value="event.id">{{ event.title }}</option>
            </BaseSelect>

            <BaseSelect v-model="filters.status" :disabled="isLoading">
              <option :value="undefined">Все статусы</option>
              <option v-for="status in statusOptions" :key="status" :value="status">{{ statusLabels[status] }}</option>
            </BaseSelect>
          </div>

          <BaseCheckbox v-model="filters.onlyMine" :disabled="isLoading">
            Только мои заявки
          </BaseCheckbox>

          <BaseButton type="button" variant="ghost" :disabled="isLoading" @click="submitFilters">
            Применить
          </BaseButton>
        </section>
      </aside>

      <main class="applications-main">
        <section class="main-section">
          <BaseStatusMessage v-if="error" tone="error">{{ error }}</BaseStatusMessage>
          <p v-else class="summary">Показаны {{ pageFrom }}-{{ pageTo }} из {{ total }}</p>

          <BaseStatusMessage v-if="statusError" tone="error">{{ statusError }}</BaseStatusMessage>

          <section v-if="isLoading" class="state">Загрузка...</section>
          <section v-else-if="list.length === 0" class="state">Список пуст</section>

          <section v-else class="list">
            <BaseCard v-for="item in list" :key="item.id" class="card">
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
                <BaseButton
                  type="button"
                  variant="ghost"
                  :disabled="isLoading || isUpdatingId === item.id"
                  @click="updateStatus(item, 'pending')"
                >
                  На рассмотрении
                </BaseButton>
                <BaseButton
                  type="button"
                  variant="ghost"
                  :disabled="isLoading || isUpdatingId === item.id"
                  @click="updateStatus(item, 'approved')"
                >
                  Одобрить
                </BaseButton>
                <BaseButton
                  type="button"
                  variant="ghost"
                  :disabled="isLoading || isUpdatingId === item.id"
                  @click="updateStatus(item, 'rejected')"
                >
                  Отклонить
                </BaseButton>
              </div>
            </BaseCard>
          </section>

          <footer class="pager">
            <BaseButton type="button" variant="ghost" :disabled="isLoading || !canPrev" @click="prevPage">
              Назад
            </BaseButton>
            <BaseButton type="button" variant="ghost" :disabled="isLoading || !canNext" @click="nextPage">
              Вперёд
            </BaseButton>
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
    @include top-links-bar;
  }

  .edit-bar__inner {
    @include top-links-inner;
  }

  .edit-link {
    @include top-link-pill;
  }

  .applications-body {
    @include page-content-shell;
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
    @include panel-surface($accent: true);
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

  .applications-main {
    min-width: 0;

    @include respond-to('lg') {
      flex: 1;
    }
  }

  .main-section {
    @include section-panel;
    display: grid;
    gap: 12px;
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
    padding: 14px;

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
    border-color: rgba($color-silver, 0.5);
    color: $color-silver;
  }

  .status--approved {
    border-color: $color-success-border;
    color: $color-success;
  }

  .status--rejected {
    border-color: $color-danger-border;
    color: $color-danger;
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
