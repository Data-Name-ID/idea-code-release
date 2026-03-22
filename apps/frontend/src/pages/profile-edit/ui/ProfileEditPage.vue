<script setup lang="ts">
  import { ref, reactive, onMounted, computed } from 'vue'
  import { useRouter } from 'vue-router'

  import { authState, setCurrentUser } from '@shared/auth/session'
  import { userApi } from '@entities/user/api'
  import { roleApi } from '@entities/role/api'
  import { skillApi } from '@entities/skill/api'
  import { teamApi } from '@entities/team/api'
  import { eventApi } from '@entities/event/api'
  import type {
    RoleResponse,
    SkillResponse,
    LinkRequest,
    TeamShortResponse,
  } from '@shared/types/api'

  const router = useRouter()
  const user = computed(() => authState.currentUser.value)

  const form = reactive({
    name: '',
    email: '',
    location: '',
    description: '',
    avatar: '',
    links: [] as LinkRequest[],
    roleIds: [] as number[],
    skillIds: [] as number[],
    openToTeamup: true,
  })

  const allRoles = ref<RoleResponse[]>([])
  const allSkills = ref<SkillResponse[]>([])
  const isLoadingOptions = ref(true)
  const isSaving = ref(false)
  const saveError = ref<string | null>(null)
  const userTeams = ref<TeamShortResponse[]>([])
  const isUploadingAvatar = ref(false)
  const avatarUploadError = ref<string | null>(null)
  const sectionLinks = [
    { id: 'section-main', label: 'Основное' },
    { id: 'section-links', label: 'Ссылки' },
    { id: 'section-roles', label: 'Роли' },
    { id: 'section-skills', label: 'Навыки' },
    { id: 'section-teamup', label: 'Поиск команды' },
    { id: 'section-teams', label: 'Команды' },
    { id: 'section-events', label: 'Хакатоны' },
  ] as const

  const teamForm = reactive({
    name: '',
    description: '',
  })
  const isCreatingTeam = ref(false)
  const createTeamError = ref<string | null>(null)
  const createTeamSuccess = ref<string | null>(null)

  const hackathonForm = reactive({
    title: '',
    description: '',
    date: '',
    cover: '',
    teamId: '',
  })
  const isAddingHackathon = ref(false)
  const addHackathonError = ref<string | null>(null)
  const addHackathonSuccess = ref<string | null>(null)

  onMounted(async () => {
    if (user.value) {
      form.name = user.value.name
      form.email = user.value.email ?? ''
      form.location = user.value.location ?? ''
      form.description = user.value.description ?? ''
      form.avatar = user.value.avatar ?? ''
      form.links = user.value.links.map((l) => ({ url: l.url, label: l.label }))
      form.roleIds = user.value.roles.map((r) => r.id)
      form.skillIds = user.value.skills.map((s) => s.id)
      form.openToTeamup = user.value.open_to_teamup
    }

    try {
      const [roles, skills, teams] = await Promise.all([
        roleApi.getList(),
        skillApi.getList(),
        user.value ? teamApi.getList({ user_id: user.value.id, limit: 100 }) : Promise.resolve(null),
      ])
      allRoles.value = roles
      allSkills.value = skills
      userTeams.value = teams?.data ?? []
    } finally {
      isLoadingOptions.value = false
    }
  })

  function addLink(): void {
    form.links.push({ url: '', label: '' })
  }

  function removeLink(index: number): void {
    form.links.splice(index, 1)
  }

  function toggleId(list: number[], id: number): void {
    const idx = list.indexOf(id)
    if (idx === -1) list.push(id)
    else list.splice(idx, 1)
  }

  function scrollToSection(sectionId: string): void {
    const target = document.getElementById(sectionId)
    if (!target) return

    const pageHeader = document.querySelector<HTMLElement>('.page-header')
    const sectionNav = document.querySelector<HTMLElement>('.section-nav')
    const stickyOffset =
      (pageHeader?.getBoundingClientRect().height ?? 0) +
      (sectionNav?.getBoundingClientRect().height ?? 0) +
      12

    const targetTop = target.getBoundingClientRect().top + window.scrollY
    window.scrollTo({
      top: Math.max(targetTop - stickyOffset, 0),
      behavior: 'smooth',
    })
  }

  async function handleAvatarSelected(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement
    const file = input.files?.[0]
    if (!file || !user.value) return

    avatarUploadError.value = null
    if (!file.type.startsWith('image/')) {
      avatarUploadError.value = 'Можно загружать только изображения'
      input.value = ''
      return
    }

    try {
      isUploadingAvatar.value = true
      const updated = await userApi.uploadAvatar(file)
      form.avatar = updated.avatar ?? ''
      setCurrentUser(updated)
    } catch (e) {
      avatarUploadError.value = e instanceof Error ? e.message : 'Не удалось загрузить аватар'
    } finally {
      isUploadingAvatar.value = false
      input.value = ''
    }
  }

  async function handleSubmit(): Promise<void> {
    if (!user.value) return
    isSaving.value = true
    saveError.value = null

    try {
      const updated = await userApi.update(user.value.id, {
        name: form.name || null,
        email: form.email || null,
        avatar: form.avatar || null,
        location: form.location || null,
        description: form.description || null,
        links: form.links.filter((l) => l.url.trim()),
        role_ids: form.roleIds,
        skill_ids: form.skillIds,
        open_to_teamup: form.openToTeamup,
      })
      setCurrentUser(updated)
      await router.replace({ name: 'profile' })
    } catch (e) {
      saveError.value = e instanceof Error ? e.message : 'Не удалось сохранить профиль'
    } finally {
      isSaving.value = false
    }
  }

  async function handleCreateTeam(): Promise<void> {
    if (!teamForm.name.trim()) {
      createTeamError.value = 'Укажите название команды'
      return
    }

    isCreatingTeam.value = true
    createTeamError.value = null
    createTeamSuccess.value = null
    try {
      const created = await teamApi.create({
        name: teamForm.name.trim(),
        description: teamForm.description.trim(),
      })
      const existing = new Set(userTeams.value.map((team) => team.id))
      if (!existing.has(created.id)) {
        userTeams.value.unshift({
          id: created.id,
          name: created.name,
          description: created.description,
        })
      }
      teamForm.name = ''
      teamForm.description = ''
      createTeamSuccess.value = `Команда «${created.name}» создана`
    } catch (e) {
      createTeamError.value = e instanceof Error ? e.message : 'Не удалось создать команду'
    } finally {
      isCreatingTeam.value = false
    }
  }

  async function handleAddHackathon(): Promise<void> {
    if (!hackathonForm.title.trim()) {
      addHackathonError.value = 'Укажите название хакатона'
      return
    }
    if (!hackathonForm.date) {
      addHackathonError.value = 'Укажите дату хакатона'
      return
    }

    const parsedDate = new Date(hackathonForm.date)
    if (Number.isNaN(parsedDate.getTime())) {
      addHackathonError.value = 'Неверный формат даты'
      return
    }
    const isoDate = parsedDate.toISOString()

    isAddingHackathon.value = true
    addHackathonError.value = null
    addHackathonSuccess.value = null
    try {
      const createdEvent = await eventApi.createParticipation({
        title: hackathonForm.title.trim(),
        description: hackathonForm.description.trim(),
        date: isoDate,
        cover: hackathonForm.cover.trim() || null,
        team_id: hackathonForm.teamId ? Number(hackathonForm.teamId) : null,
      })
      hackathonForm.title = ''
      hackathonForm.description = ''
      hackathonForm.date = ''
      hackathonForm.cover = ''
      hackathonForm.teamId = ''
      addHackathonSuccess.value = `Хакатон «${createdEvent.title}» добавлен`
    } catch (e) {
      addHackathonError.value = e instanceof Error ? e.message : 'Не удалось добавить хакатон'
    } finally {
      isAddingHackathon.value = false
    }
  }
</script>

<template>
  <div class="edit-page">
    <header class="page-header">
      <button class="back-btn" @click="router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
      </button>
      <h1 class="page-header__title">Редактировать профиль</h1>
      <button class="save-btn" :disabled="isSaving" @click="handleSubmit">
        {{ isSaving ? 'Сохраняем…' : 'Сохранить' }}
      </button>
    </header>

    <nav class="section-nav" aria-label="Разделы формы">
      <button
        v-for="section in sectionLinks"
        :key="section.id"
        type="button"
        class="section-nav__item"
        @click="scrollToSection(section.id)"
      >
        {{ section.label }}
      </button>
    </nav>

    <form class="form" @submit.prevent="handleSubmit">
      <p v-if="saveError" class="form__error">{{ saveError }}</p>

      <section id="section-main" class="section">
        <h2 class="section__title">Основное</h2>

        <div class="avatar-preview">
          <div class="avatar-ring">
            <img v-if="form.avatar" :src="form.avatar" alt="Аватар" class="avatar-img" />
            <div v-else class="avatar-placeholder">
              <svg viewBox="0 0 24 24" fill="currentColor" width="32" height="32">
                <path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10zm0 2c-5.33 0-8 2.67-8 4v2h16v-2c0-1.33-2.67-4-8-4z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="field">
          <label class="field__label">Загрузка аватара</label>
          <label class="upload-avatar-btn">
            <input
              type="file"
              accept="image/*"
              class="upload-avatar-btn__input"
              :disabled="isUploadingAvatar"
              @change="handleAvatarSelected"
            />
            {{ isUploadingAvatar ? 'Загружаем…' : 'Загрузить файл' }}
          </label>
          <p v-if="avatarUploadError" class="form__error upload-error">{{ avatarUploadError }}</p>
        </div>

        <div class="field">
          <label class="field__label">Имя <span class="required">*</span></label>
          <input v-model="form.name" type="text" class="field__input" required placeholder="Ваше имя" />
        </div>

        <div class="field">
          <label class="field__label">Email</label>
          <input v-model="form.email" type="email" class="field__input" placeholder="you@example.com" />
        </div>

        <div class="field">
          <label class="field__label">Город / местоположение</label>
          <input v-model="form.location" type="text" class="field__input" placeholder="Москва, Россия" />
        </div>

        <div class="field">
          <label class="field__label">О себе</label>
          <textarea v-model="form.description" class="field__input field__input--textarea" rows="3" placeholder="Расскажите о себе…" />
        </div>
      </section>

      <section id="section-links" class="section">
        <h2 class="section__title">Ссылки</h2>

        <div v-for="(link, i) in form.links" :key="i" class="link-row">
          <div class="link-row__fields">
            <input v-model="form.links[i].url" type="url" class="field__input" placeholder="https://github.com/…" />
            <input v-model="form.links[i].label" type="text" class="field__input" placeholder="GitHub" />
          </div>
          <button type="button" class="remove-btn" aria-label="Удалить ссылку" @click="removeLink(i)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <button type="button" class="add-btn" @click="addLink">+ Добавить ссылку</button>
      </section>

      <section id="section-roles" class="section">
        <h2 class="section__title">Роли</h2>
        <p v-if="isLoadingOptions" class="loading-hint">Загрузка…</p>
        <div v-else class="chips">
          <button
            v-for="role in allRoles"
            :key="role.id"
            type="button"
            class="chip"
            :class="{ 'chip--active': form.roleIds.includes(role.id) }"
            @click="toggleId(form.roleIds, role.id)"
          >
            {{ role.name }}
          </button>
        </div>
      </section>

      <section id="section-skills" class="section">
        <h2 class="section__title">Навыки</h2>
        <p v-if="isLoadingOptions" class="loading-hint">Загрузка…</p>
        <div v-else class="chips">
          <button
            v-for="skill in allSkills"
            :key="skill.id"
            type="button"
            class="chip"
            :class="{ 'chip--active': form.skillIds.includes(skill.id) }"
            @click="toggleId(form.skillIds, skill.id)"
          >
            {{ skill.name }}
          </button>
        </div>
      </section>

      <section id="section-teamup" class="section">
        <h2 class="section__title">Поиск сокомандников</h2>
        <label class="checkbox-row">
          <input v-model="form.openToTeamup" type="checkbox" />
          <span>Я открыт(а) к приглашениям в команду</span>
        </label>
      </section>

      <section id="section-teams" class="section">
        <h2 class="section__title">Команды</h2>
        <p class="section__hint">Создайте команду, в которой участвуете</p>
        <p v-if="createTeamError" class="form__error section__error">{{ createTeamError }}</p>
        <p v-if="createTeamSuccess" class="form__success">{{ createTeamSuccess }}</p>

        <div class="field">
          <label class="field__label">Название команды</label>
          <input
            v-model="teamForm.name"
            type="text"
            class="field__input"
            placeholder="например, Team Rocket"
          />
        </div>

        <div class="field">
          <label class="field__label">Описание</label>
          <textarea
            v-model="teamForm.description"
            class="field__input field__input--textarea"
            rows="2"
            placeholder="Коротко о вашей команде"
          />
        </div>

        <button type="button" class="submit-btn submit-btn--inline" :disabled="isCreatingTeam" @click="handleCreateTeam">
          {{ isCreatingTeam ? 'Создаём…' : 'Создать команду' }}
        </button>
      </section>

      <section id="section-events" class="section">
        <h2 class="section__title">Хакатоны</h2>
        <p class="section__hint">Добавьте хакатон, в котором вы участвовали</p>
        <p v-if="addHackathonError" class="form__error section__error">{{ addHackathonError }}</p>
        <p v-if="addHackathonSuccess" class="form__success">{{ addHackathonSuccess }}</p>

        <div class="field">
          <label class="field__label">Название хакатона</label>
          <input
            v-model="hackathonForm.title"
            type="text"
            class="field__input"
            placeholder="например, AI Weekend 2026"
          />
        </div>

        <div class="field">
          <label class="field__label">Описание</label>
          <textarea
            v-model="hackathonForm.description"
            class="field__input field__input--textarea"
            rows="2"
            placeholder="Что это был за хакатон"
          />
        </div>

        <div class="field">
          <label class="field__label">Дата</label>
          <input v-model="hackathonForm.date" type="datetime-local" class="field__input" />
        </div>

        <div class="field">
          <label class="field__label">Обложка (URL)</label>
          <input
            v-model="hackathonForm.cover"
            type="url"
            class="field__input"
            placeholder="https://…"
          />
        </div>

        <div class="field">
          <label class="field__label">Команда</label>
          <select v-model="hackathonForm.teamId" class="field__input">
            <option value="">Личное участие</option>
            <option v-for="team in userTeams" :key="team.id" :value="String(team.id)">
              {{ team.name }}
            </option>
          </select>
        </div>

        <button type="button" class="submit-btn submit-btn--inline" :disabled="isAddingHackathon" @click="handleAddHackathon">
          {{ isAddingHackathon ? 'Добавляем…' : 'Добавить хакатон участия' }}
        </button>
      </section>

      <button type="submit" class="submit-btn" :disabled="isSaving">
        {{ isSaving ? 'Сохраняем…' : 'Сохранить изменения' }}
      </button>
    </form>
  </div>
</template>

<style scoped lang="scss">
  .edit-page {
    @include page-root;
  }

  .page-header {
    @include sticky-header;
  }

  .page-header__title {
    margin: 0;
    font-size: 16px;
    font-weight: 700;
  }

  .back-btn {
    @include back-button;
  }

  .save-btn {
    padding: 7px 16px;
    border-radius: $radius-full;
    border: none;
    background: $color-accent;
    color: #fff;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity $transition-fast;

    &:disabled {
      opacity: 0.5;
      cursor: wait;
    }
  }

  .form {
    @include flex-column;

    @include respond-to('lg') {
      max-width: 720px;
      width: 100%;
      margin: 0 auto;
      padding: 32px 32px 64px;
      gap: 24px;
    }
  }

  .section-nav {
    position: sticky;
    top: 61px;
    z-index: 5;
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding: 10px 16px;
    border-bottom: 1px solid $color-border;
    background: rgba(18, 18, 20, 0.94);
    backdrop-filter: blur(10px);

    @include respond-to('lg') {
      justify-content: center;
      top: 62px;
    }
  }

  .section-nav__item {
    border: 1px solid $color-border;
    border-radius: $radius-full;
    background: #1a1b20;
    color: $color-text-secondary;
    padding: 6px 12px;
    font-size: 12px;
    cursor: pointer;
    white-space: nowrap;

    &:hover {
      color: #fff;
      border-color: rgba($color-accent, 0.6);
    }
  }

  .form__error {
    margin: 12px 16px;
    padding: 10px 14px;
    border-radius: $radius-md;
    background: rgba($color-danger, 0.15);
    border: 1px solid rgba($color-danger, 0.4);
    color: #f87171;
    font-size: 14px;

    @include respond-to('lg') {
      margin: 0;
    }
  }

  .section {
    scroll-margin-top: 132px;
    padding: 20px 16px;
    @include flex-column(12px);
    border-bottom: 1px solid $color-border;

    @include respond-to('lg') {
      padding: 28px 32px;
      background: #141417;
      border: 1px solid $color-border;
      border-radius: $radius-2xl;
    }
  }

  .section__title {
    margin: 0;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: $color-text-secondary;
    text-transform: uppercase;
  }

  .section__hint {
    margin: 0;
    color: $color-text-secondary;
    font-size: 13px;
  }

  .checkbox-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: $color-text-primary;

    input {
      width: 16px;
      height: 16px;
    }
  }

  .avatar-preview {
    display: flex;
    justify-content: center;
    margin-bottom: 4px;
  }

  .avatar-ring {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    border: 2.5px solid $color-accent;
    padding: 3px;
    overflow: hidden;
  }

  .avatar-img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
    display: block;
  }

  .avatar-placeholder {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: #2a2a2a;
    @include flex-center;
    color: $color-text-secondary;
  }

  .field {
    @include flex-column(6px);
  }

  .upload-avatar-btn {
    display: inline-flex;
    width: fit-content;
    align-items: center;
    justify-content: center;
    min-height: 36px;
    padding: 6px 14px;
    border: 1px solid rgba($color-accent, 0.5);
    border-radius: $radius-full;
    background: rgba($color-accent, 0.14);
    color: #fff;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
  }

  .upload-avatar-btn__input {
    display: none;
  }

  .upload-error {
    margin: 0;
  }

  .field__label {
    font-size: 13px;
    font-weight: 500;
    color: $color-text-secondary;

    .required { color: $color-accent; }
  }

  .field__input {
    width: 100%;
    padding: 10px 12px;
    border-radius: $radius-md;
    border: 1px solid $color-border;
    background: $color-surface;
    color: $color-text-primary;
    font-size: 14px;
    font-family: inherit;
    outline: none;
    box-sizing: border-box;
    transition: border-color $transition-fast;

    &::placeholder { color: $color-text-secondary; }
    &:focus { border-color: $color-accent; }

    &--textarea {
      resize: vertical;
      min-height: 80px;
    }
  }

  .section__error {
    margin: 0;
  }

  .form__success {
    margin: 0;
    padding: 10px 14px;
    border-radius: $radius-md;
    background: rgba(#34d399, 0.12);
    border: 1px solid rgba(#34d399, 0.35);
    color: #34d399;
    font-size: 14px;
  }

  .link-row {
    display: flex;
    gap: 8px;
    align-items: flex-start;
  }

  .link-row__fields {
    flex: 1;
    @include flex-column(6px);
  }

  .remove-btn {
    @include flex-center;
    width: 36px;
    height: 36px;
    flex-shrink: 0;
    margin-top: 2px;
    border: 1px solid $color-border;
    border-radius: $radius-sm;
    background: none;
    color: $color-text-secondary;
    cursor: pointer;

    &:hover {
      border-color: #f87171;
      color: #f87171;
    }
  }

  .add-btn {
    align-self: flex-start;
    padding: 8px 14px;
    border-radius: $radius-full;
    border: 1px dashed $color-border;
    background: none;
    color: $color-text-secondary;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: border-color $transition-fast, color $transition-fast;

    &:hover {
      border-color: $color-accent;
      color: $color-accent;
    }
  }

  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .chip {
    padding: 7px 14px;
    border-radius: $radius-full;
    border: 1px solid $color-border;
    background: none;
    color: $color-text-primary;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: background $transition-fast, border-color $transition-fast, color $transition-fast;

    &--active {
      background: rgba($color-accent, 0.15);
      border-color: $color-accent;
      color: $color-accent;
    }
  }

  .loading-hint {
    margin: 0;
    font-size: 13px;
    color: $color-text-secondary;
  }

  .submit-btn {
    margin: 20px 16px 0;
    padding: 14px;
    border-radius: $radius-lg;
    border: none;
    background: $color-accent;
    color: #fff;
    font-size: 15px;
    font-weight: 700;
    font-family: inherit;
    cursor: pointer;
    transition: opacity $transition-fast;

    &:disabled {
      opacity: 0.5;
      cursor: wait;
    }

    @include respond-to('lg') {
      margin: 0;
    }
  }

  .submit-btn--inline {
    margin-top: 4px;
  }
</style>
