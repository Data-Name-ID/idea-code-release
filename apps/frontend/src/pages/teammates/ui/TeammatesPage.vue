<script setup lang="ts">
  import { computed, onMounted, reactive, ref } from 'vue'
  import { useRouter } from 'vue-router'

  import { userApi } from '@entities/user/api'
  import { roleApi } from '@entities/role/api'
  import { skillApi } from '@entities/skill/api'
  import type { RoleResponse, SkillResponse, UserShortResponse } from '@shared/types/api'

  const router = useRouter()

  const filters = reactive({
    search: '',
    location: '',
    roleId: '',
    skillId: '',
    openToTeamup: true,
    limit: 20,
    offset: 0,
  })

  const users = ref<UserShortResponse[]>([])
  const total = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const allRoles = ref<RoleResponse[]>([])
  const allSkills = ref<SkillResponse[]>([])

  const canPrev = computed(() => filters.offset > 0)
  const canNext = computed(() => filters.offset + filters.limit < total.value)

  async function loadFilters(): Promise<void> {
    const [roles, skills] = await Promise.all([roleApi.getList(), skillApi.getList()])
    allRoles.value = roles
    allSkills.value = skills
  }

  async function loadUsers(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const res = await userApi.getList({
        search: filters.search || undefined,
        location: filters.location || undefined,
        role_id: filters.roleId ? Number(filters.roleId) : undefined,
        skill_id: filters.skillId ? Number(filters.skillId) : undefined,
        open_to_teamup: filters.openToTeamup,
        limit: filters.limit,
        offset: filters.offset,
      })
      users.value = res.data
      total.value = res.total
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Не удалось загрузить сокомандников'
    } finally {
      isLoading.value = false
    }
  }

  function submitSearch(): void {
    filters.offset = 0
    void loadUsers()
  }

  function resetFilters(): void {
    filters.search = ''
    filters.location = ''
    filters.roleId = ''
    filters.skillId = ''
    filters.openToTeamup = true
    filters.offset = 0
    void loadUsers()
  }

  function prevPage(): void {
    if (!canPrev.value) return
    filters.offset = Math.max(0, filters.offset - filters.limit)
    void loadUsers()
  }

  function nextPage(): void {
    if (!canNext.value) return
    filters.offset += filters.limit
    void loadUsers()
  }

  onMounted(async () => {
    await loadFilters()
    await loadUsers()
  })
</script>

<template>
  <div class="teammates-page">
    <header class="page-header">
      <button class="back-btn" @click="router.back()">Назад</button>
      <h1 class="page-title">Поиск сокомандников</h1>
      <RouterLink class="action-link" to="/applications">Заявки</RouterLink>
    </header>

    <section class="filters">
      <input v-model="filters.search" class="field" type="text" placeholder="Имя, username, о себе" />
      <input v-model="filters.location" class="field" type="text" placeholder="Город" />

      <select v-model="filters.roleId" class="field">
        <option value="">Любая роль</option>
        <option v-for="role in allRoles" :key="role.id" :value="String(role.id)">{{ role.name }}</option>
      </select>

      <select v-model="filters.skillId" class="field">
        <option value="">Любой навык</option>
        <option v-for="skill in allSkills" :key="skill.id" :value="String(skill.id)">{{ skill.name }}</option>
      </select>

      <label class="checkbox-row">
        <input v-model="filters.openToTeamup" type="checkbox" />
        Только открытые к поиску команды
      </label>

      <div class="filter-actions">
        <button type="button" class="btn" @click="submitSearch">Искать</button>
        <button type="button" class="btn btn--ghost" @click="resetFilters">Сброс</button>
      </div>
    </section>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-else class="summary">Найдено: {{ total }}</p>

    <section v-if="isLoading" class="state">Загрузка...</section>

    <section v-else-if="users.length === 0" class="state">Ничего не найдено</section>

    <section v-else class="grid">
      <article
        v-for="user in users"
        :key="user.id"
        class="card"
        role="button"
        tabindex="0"
        @click="router.push(`/users/${user.id}`)"
        @keydown.enter="router.push(`/users/${user.id}`)"
      >
        <div class="card-head">
          <h3>{{ user.name }}</h3>
          <span>@{{ user.username }}</span>
        </div>
        <p>{{ user.location || 'Локация не указана' }}</p>
        <p class="meta">{{ user.roles.map((item) => item.name).join(', ') || 'Роль не указана' }}</p>
        <p class="meta">{{ user.skills.map((item) => item.name).join(', ') || 'Навыки не указаны' }}</p>
      </article>
    </section>

    <footer class="pager">
      <button type="button" class="btn btn--ghost" :disabled="!canPrev" @click="prevPage">Назад</button>
      <button type="button" class="btn btn--ghost" :disabled="!canNext" @click="nextPage">Вперёд</button>
    </footer>
  </div>
</template>

<style scoped lang="scss">
  .teammates-page {
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

  .filters {
    border: 1px solid $color-border;
    border-radius: $radius-lg;
    padding: 12px;
    display: grid;
    gap: 8px;
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

  .filter-actions {
    display: flex;
    gap: 8px;
  }

  .btn {
    border: 1px solid transparent;
    border-radius: $radius-md;
    padding: 8px 12px;
    background: $color-accent;
    color: #0f0f11;
    font-weight: 600;
    cursor: pointer;
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

  .grid {
    display: grid;
    gap: 10px;

    @include respond-to('lg') {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  .card {
    border: 1px solid $color-border;
    border-radius: $radius-lg;
    padding: 12px;
    background: #141417;
    cursor: pointer;

    p {
      margin: 6px 0 0;
    }
  }

  .card-head {
    display: flex;
    justify-content: space-between;
    gap: 8px;

    h3 {
      margin: 0;
      font-size: 16px;
    }

    span {
      color: $color-text-secondary;
      font-size: 13px;
    }
  }

  .meta {
    color: $color-text-secondary;
    font-size: 13px;
  }

  .pager {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }
</style>
