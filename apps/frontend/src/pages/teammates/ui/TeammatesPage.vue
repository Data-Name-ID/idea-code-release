<script setup lang="ts">
  import { computed, onMounted, reactive, ref } from 'vue'
  import { useRouter } from 'vue-router'

  import { userApi } from '@entities/user/api'
  import { roleApi } from '@entities/role/api'
  import { skillApi } from '@entities/skill/api'
  import {
    BaseButton,
    BaseCard,
    BaseCheckbox,
    BaseFilterPanel,
    BaseInput,
    BaseSelect,
    BaseStatusMessage,
  } from '@shared/ui'
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

  const isFiltersOpen = ref(false)
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

  function applyFilters(): void {
    filters.offset = 0
    isFiltersOpen.value = false
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
    <div class="teammates-body">
      <main class="teammates-main">
        <section class="main-section">
          <div class="section-head">
            <h1 class="section-title">Сокомандники</h1>
            <BaseButton type="button" variant="ghost" @click="isFiltersOpen = true">Фильтры</BaseButton>
          </div>

          <BaseStatusMessage v-if="error" tone="error">{{ error }}</BaseStatusMessage>
          <p v-else class="summary">Показаны {{ pageFrom }}-{{ pageTo }} из {{ total }}</p>

          <section v-if="isLoading" class="state">Загрузка...</section>
          <section v-else-if="users.length === 0" class="state">Ничего не найдено</section>

          <section v-else class="grid">
            <BaseCard
              v-for="user in users"
              :key="user.id"
              class="card"
              :interactive="true"
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

    <BaseFilterPanel v-model="isFiltersOpen" title="Фильтры поиска">
      <form class="filters" @submit.prevent="applyFilters">
        <BaseInput
          v-model="filters.search"
          type="text"
          placeholder="Имя, username, о себе"
          :disabled="isLoading"
        />
        <BaseInput
          v-model="filters.location"
          type="text"
          placeholder="Город"
          :disabled="isLoading"
        />

        <BaseSelect v-model="filters.roleId" :disabled="isLoading">
          <option value="">Любая роль</option>
          <option v-for="role in allRoles" :key="role.id" :value="String(role.id)">{{ role.name }}</option>
        </BaseSelect>

        <BaseSelect v-model="filters.skillId" :disabled="isLoading">
          <option value="">Любой навык</option>
          <option v-for="skill in allSkills" :key="skill.id" :value="String(skill.id)">{{ skill.name }}</option>
        </BaseSelect>

        <BaseCheckbox v-model="filters.openToTeamup" :disabled="isLoading">
          Только открытые к поиску команды
        </BaseCheckbox>

        <div class="filter-actions">
          <BaseButton type="submit" :loading="isLoading" block>
            {{ isLoading ? 'Ищем…' : 'Применить фильтры' }}
          </BaseButton>
          <BaseButton type="button" variant="ghost" :disabled="isLoading" block @click="resetFilters">
            Сбросить
          </BaseButton>
        </div>
      </form>
    </BaseFilterPanel>
  </div>
</template>

<style scoped lang="scss">
  .teammates-page {
    @include page-root;
  }

  .teammates-body {
    max-width: 1200px;
    margin: 0 auto;
    padding: $space-4 $space-4 56px;

    @include respond-to('lg') {
      padding: $space-8 $space-8 64px;
    }
  }

  .main-section {
    @include section-panel;
    display: grid;
    gap: $space-3;
  }

  .section-head {
    @include flex-between;
    gap: $space-3;
  }

  .section-title {
    margin: 0;
    font-size: 22px;
    font-weight: 800;
  }

  .summary {
    margin: 0;
    color: $color-text-secondary;
  }

  .state {
    border: 1px dashed $color-border;
    border-radius: $radius-md;
    padding: $space-4;
    color: $color-text-secondary;
  }

  .grid {
    display: grid;
    gap: $space-3;

    @include respond-to('lg') {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  .card {
    padding: 14px;

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
    gap: $space-2;
    justify-content: flex-end;
  }

  .filters {
    display: grid;
    gap: $space-3;
  }

  .filter-actions {
    display: grid;
    gap: $space-2;
    margin-top: $space-1;
  }
</style>
