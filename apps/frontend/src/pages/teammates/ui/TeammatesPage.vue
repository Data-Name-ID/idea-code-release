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
  const pageFrom = computed(() => (total.value === 0 ? 0 : filters.offset + 1))
  const pageTo = computed(() => Math.min(filters.offset + filters.limit, total.value))

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

  function openUserProfile(userId: number): void {
    void router.push(`/users/${userId}`)
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
    <div class="edit-bar">
      <div class="edit-bar__inner">
        <RouterLink :to="{ name: 'profile' }" class="edit-link">Профиль</RouterLink>
        <RouterLink :to="{ name: 'teammates' }" class="edit-link">Сокомандники</RouterLink>
        <RouterLink :to="{ name: 'applications' }" class="edit-link">Заявки</RouterLink>
      </div>
    </div>

    <div class="teammates-body">
      <aside class="teammates-sidebar">
        <section class="sidebar-section">
          <h1 class="section-title">Поиск сокомандников</h1>

          <form class="filters" @submit.prevent="submitSearch">
            <input
              v-model="filters.search"
              class="field"
              type="text"
              placeholder="Имя, username, о себе"
              :disabled="isLoading"
            />
            <input
              v-model="filters.location"
              class="field"
              type="text"
              placeholder="Город"
              :disabled="isLoading"
            />

            <select v-model="filters.roleId" class="field" :disabled="isLoading">
              <option value="">Любая роль</option>
              <option v-for="role in allRoles" :key="role.id" :value="String(role.id)">{{ role.name }}</option>
            </select>

            <select v-model="filters.skillId" class="field" :disabled="isLoading">
              <option value="">Любой навык</option>
              <option v-for="skill in allSkills" :key="skill.id" :value="String(skill.id)">{{ skill.name }}</option>
            </select>

            <label class="checkbox-row">
              <input v-model="filters.openToTeamup" type="checkbox" :disabled="isLoading" />
              Только открытые к поиску команды
            </label>

            <div class="filter-actions">
              <button type="submit" class="btn" :disabled="isLoading">
                {{ isLoading ? 'Ищем…' : 'Искать' }}
              </button>
              <button type="button" class="btn btn--ghost" :disabled="isLoading" @click="resetFilters">Сброс</button>
            </div>
          </form>
        </section>
      </aside>

      <main class="teammates-main">
        <section class="main-section">
          <p v-if="error" class="error">{{ error }}</p>
          <p v-else class="summary">Показаны {{ pageFrom }}-{{ pageTo }} из {{ total }}</p>

          <section v-if="isLoading" class="state">Загрузка...</section>
          <section v-else-if="users.length === 0" class="state">Ничего не найдено</section>

          <section v-else class="grid">
            <article
              v-for="user in users"
              :key="user.id"
              class="card"
              role="button"
              tabindex="0"
              @click="openUserProfile(user.id)"
              @keydown.enter="openUserProfile(user.id)"
              @keydown.space.prevent="openUserProfile(user.id)"
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
            <button type="button" class="btn btn--ghost" :disabled="isLoading || !canPrev" @click="prevPage">Назад</button>
            <button type="button" class="btn btn--ghost" :disabled="isLoading || !canNext" @click="nextPage">Вперёд</button>
          </footer>
        </section>
      </main>
    </div>
  </div>
</template>

<style scoped lang="scss">
  .teammates-page {
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

  .teammates-body {
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

  .teammates-sidebar {
    display: flex;
    flex-direction: column;
    gap: 20px;

    @include respond-to('lg') {
      width: 320px;
      flex-shrink: 0;
      gap: 16px;
    }
  }

  .sidebar-section {
    background: #1a1a1d;
    border: 1px solid rgba($color-accent, 0.2);
    border-radius: $radius-2xl;
    padding: 20px;
  }

  .section-title {
    margin: 0 0 14px;
    font-size: 18px;
    line-height: 1.25;
  }

  .filters {
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

  .teammates-main {
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

  .grid {
    display: grid;
    gap: 12px;

    @include respond-to('lg') {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  .card {
    border: 1px solid $color-border;
    border-radius: $radius-xl;
    padding: 14px;
    background: #141417;
    cursor: pointer;
    transition: border-color $transition-fast, transform $transition-fast;

    &:hover,
    &:focus-visible {
      border-color: rgba($color-accent, 0.45);
      transform: translateY(-1px);
      outline: none;
    }

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
