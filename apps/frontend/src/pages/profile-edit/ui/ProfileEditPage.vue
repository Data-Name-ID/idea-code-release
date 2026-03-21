<script setup lang="ts">
  import { ref, reactive, onMounted, computed } from 'vue'
  import { useRouter } from 'vue-router'

  import { authState, setCurrentUser } from '@shared/auth/session'
  import { userApi } from '@entities/user/api'
  import { roleApi } from '@entities/role/api'
  import { skillApi } from '@entities/skill/api'
  import type { RoleResponse, SkillResponse, LinkRequest } from '@shared/types/api'

  const router = useRouter()

  const user = computed(() => authState.currentUser.value)

  // ── Form state ────────────────────────────────────────────

  const form = reactive({
    name: '',
    email: '',
    location: '',
    description: '',
    avatar: '',
    links: [] as LinkRequest[],
    role_ids: [] as number[],
    skill_ids: [] as number[],
  })

  // ── Available roles & skills ──────────────────────────────

  const allRoles = ref<RoleResponse[]>([])
  const allSkills = ref<SkillResponse[]>([])
  const loadingOptions = ref(true)

  // ── Save state ────────────────────────────────────────────

  const saving = ref(false)
  const saveError = ref<string | null>(null)

  // ── Init ──────────────────────────────────────────────────

  onMounted(async () => {
    if (user.value) {
      form.name = user.value.name
      form.email = user.value.email ?? ''
      form.location = user.value.location ?? ''
      form.description = user.value.description ?? ''
      form.avatar = user.value.avatar ?? ''
      form.links = user.value.links.map((l) => ({ url: l.url, label: l.label }))
      form.role_ids = user.value.roles.map((r) => r.id)
      form.skill_ids = user.value.skills.map((s) => s.id)
    }

    try {
      const [roles, skills] = await Promise.all([roleApi.getList(), skillApi.getList()])
      allRoles.value = roles
      allSkills.value = skills
    } finally {
      loadingOptions.value = false
    }
  })

  // ── Links management ──────────────────────────────────────

  function addLink(): void {
    form.links.push({ url: '', label: '' })
  }

  function removeLink(index: number): void {
    form.links.splice(index, 1)
  }

  // ── Role / skill toggle ───────────────────────────────────

  function toggleRole(id: number): void {
    const idx = form.role_ids.indexOf(id)
    if (idx === -1) form.role_ids.push(id)
    else form.role_ids.splice(idx, 1)
  }

  function toggleSkill(id: number): void {
    const idx = form.skill_ids.indexOf(id)
    if (idx === -1) form.skill_ids.push(id)
    else form.skill_ids.splice(idx, 1)
  }

  // ── Submit ────────────────────────────────────────────────

  async function handleSubmit(): Promise<void> {
    if (!user.value) return
    saving.value = true
    saveError.value = null

    try {
      const updated = await userApi.update(user.value.id, {
        name: form.name || null,
        email: form.email || null,
        avatar: form.avatar || null,
        location: form.location || null,
        description: form.description || null,
        links: form.links.filter((l) => l.url.trim()),
        role_ids: form.role_ids,
        skill_ids: form.skill_ids,
      })
      setCurrentUser(updated)
      await router.replace({ name: 'profile' })
    } catch (e) {
      saveError.value = e instanceof Error ? e.message : 'Не удалось сохранить профиль'
    } finally {
      saving.value = false
    }
  }
</script>

<template>
  <div class="edit-page">
    <header class="edit-header">
      <button class="back-btn" @click="router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
      </button>
      <h1 class="edit-header__title">Редактировать профиль</h1>
      <button
        class="save-btn"
        :disabled="saving"
        @click="handleSubmit"
      >
        {{ saving ? 'Сохраняем…' : 'Сохранить' }}
      </button>
    </header>

    <form class="form" @submit.prevent="handleSubmit">
      <!-- Error -->
      <p v-if="saveError" class="form__error">{{ saveError }}</p>

      <!-- ── Basic info ──────────────────────────── -->
      <section class="section">
        <h2 class="section__title">Основное</h2>

        <!-- Avatar preview -->
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
          <label class="field__label">URL аватара</label>
          <input v-model="form.avatar" type="url" class="field__input" placeholder="https://…" />
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

      <!-- ── Links ──────────────────────────────── -->
      <section class="section">
        <h2 class="section__title">Ссылки</h2>

        <div v-for="(link, i) in form.links" :key="i" class="link-row">
          <div class="link-row__fields">
            <input
              v-model="form.links[i].url"
              type="url"
              class="field__input"
              placeholder="https://github.com/…"
            />
            <input
              v-model="form.links[i].label"
              type="text"
              class="field__input"
              placeholder="GitHub"
            />
          </div>
          <button type="button" class="remove-btn" aria-label="Удалить ссылку" @click="removeLink(i)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <button type="button" class="add-btn" @click="addLink">
          + Добавить ссылку
        </button>
      </section>

      <!-- ── Roles ──────────────────────────────── -->
      <section class="section">
        <h2 class="section__title">Роли</h2>
        <p v-if="loadingOptions" class="loading-hint">Загрузка…</p>
        <div v-else class="chips">
          <button
            v-for="role in allRoles"
            :key="role.id"
            type="button"
            class="chip"
            :class="{ 'chip--active': form.role_ids.includes(role.id) }"
            @click="toggleRole(role.id)"
          >
            {{ role.name }}
          </button>
        </div>
      </section>

      <!-- ── Skills ─────────────────────────────── -->
      <section class="section">
        <h2 class="section__title">Навыки</h2>
        <p v-if="loadingOptions" class="loading-hint">Загрузка…</p>
        <div v-else class="chips">
          <button
            v-for="skill in allSkills"
            :key="skill.id"
            type="button"
            class="chip"
            :class="{ 'chip--active': form.skill_ids.includes(skill.id) }"
            @click="toggleSkill(skill.id)"
          >
            {{ skill.name }}
          </button>
        </div>
      </section>

      <!-- Bottom save -->
      <button
        type="submit"
        class="submit-btn"
        :disabled="saving"
      >
        {{ saving ? 'Сохраняем…' : 'Сохранить изменения' }}
      </button>
    </form>
  </div>
</template>

<style scoped lang="scss">
  .edit-page {
    --p-bg:             #121212;
    --p-surface:        #1c1c1e;
    --p-border:         rgba(255, 255, 255, 0.08);
    --p-accent:         #ff6b2b;
    --p-text-primary:   #ffffff;
    --p-text-secondary: rgba(255, 255, 255, 0.5);

    min-height: 100dvh;
    background: var(--p-bg);
    color: var(--p-text-primary);
    font-family: 'Manrope', 'IBM Plex Sans', sans-serif;
    padding-bottom: 40px;
  }

  /* ── Header ─────────────────────────────────── */

  .edit-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid var(--p-border);
    position: sticky;
    top: 0;
    z-index: 10;
    background: var(--p-bg);
  }

  .edit-header__title {
    margin: 0;
    font-size: 16px;
    font-weight: 700;
    color: var(--p-text-primary);
  }

  .back-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border: none;
    background: none;
    color: var(--p-text-primary);
    cursor: pointer;
    border-radius: 8px;

    &:hover {
      background: var(--p-surface);
    }
  }

  .save-btn {
    padding: 7px 16px;
    border-radius: 100px;
    border: none;
    background: var(--p-accent);
    color: #fff;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 150ms;

    &:disabled {
      opacity: 0.5;
      cursor: wait;
    }
  }

  /* ── Form ───────────────────────────────────── */

  .form {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .form__error {
    margin: 12px 16px;
    padding: 10px 14px;
    border-radius: 10px;
    background: rgba(220, 38, 38, 0.15);
    border: 1px solid rgba(220, 38, 38, 0.4);
    color: #f87171;
    font-size: 14px;
  }

  /* ── Sections ───────────────────────────────── */

  .section {
    padding: 20px 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    border-bottom: 1px solid var(--p-border);
  }

  .section__title {
    margin: 0;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: var(--p-text-secondary);
    text-transform: uppercase;
  }

  /* ── Avatar ─────────────────────────────────── */

  .avatar-preview {
    display: flex;
    justify-content: center;
    margin-bottom: 4px;
  }

  .avatar-ring {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    border: 2.5px solid var(--p-accent);
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
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--p-text-secondary);
  }

  /* ── Fields ─────────────────────────────────── */

  .field {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .field__label {
    font-size: 13px;
    font-weight: 500;
    color: var(--p-text-secondary);

    .required {
      color: var(--p-accent);
    }
  }

  .field__input {
    width: 100%;
    padding: 10px 12px;
    border-radius: 10px;
    border: 1px solid var(--p-border);
    background: var(--p-surface);
    color: var(--p-text-primary);
    font-size: 14px;
    font-family: inherit;
    outline: none;
    box-sizing: border-box;
    transition: border-color 150ms;

    &::placeholder {
      color: var(--p-text-secondary);
    }

    &:focus {
      border-color: var(--p-accent);
    }

    &--textarea {
      resize: vertical;
      min-height: 80px;
    }
  }

  /* ── Links ──────────────────────────────────── */

  .link-row {
    display: flex;
    gap: 8px;
    align-items: flex-start;
  }

  .link-row__fields {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .remove-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    flex-shrink: 0;
    margin-top: 2px;
    border: 1px solid var(--p-border);
    border-radius: 8px;
    background: none;
    color: var(--p-text-secondary);
    cursor: pointer;

    &:hover {
      border-color: #f87171;
      color: #f87171;
    }
  }

  .add-btn {
    align-self: flex-start;
    padding: 8px 14px;
    border-radius: 100px;
    border: 1px dashed var(--p-border);
    background: none;
    color: var(--p-text-secondary);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: border-color 150ms, color 150ms;

    &:hover {
      border-color: var(--p-accent);
      color: var(--p-accent);
    }
  }

  /* ── Chips ──────────────────────────────────── */

  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .chip {
    padding: 7px 14px;
    border-radius: 100px;
    border: 1px solid var(--p-border);
    background: none;
    color: var(--p-text-primary);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: background 150ms, border-color 150ms, color 150ms;

    &--active {
      background: rgba(255, 107, 43, 0.15);
      border-color: var(--p-accent);
      color: var(--p-accent);
    }
  }

  .loading-hint {
    margin: 0;
    font-size: 13px;
    color: var(--p-text-secondary);
  }

  /* ── Submit button ──────────────────────────── */

  .submit-btn {
    margin: 20px 16px 0;
    padding: 14px;
    border-radius: 12px;
    border: none;
    background: var(--p-accent);
    color: #fff;
    font-size: 15px;
    font-weight: 700;
    font-family: inherit;
    cursor: pointer;
    transition: opacity 150ms;

    &:disabled {
      opacity: 0.5;
      cursor: wait;
    }
  }
</style>
