<script setup lang="ts">
  import { reactive, ref } from 'vue'
  import { useRouter } from 'vue-router'

  import { teamApi } from '@entities/team/api'
  import type { LinkRequest } from '@shared/types/api'

  const router = useRouter()

  const form = reactive({
    name: '',
    description: '',
    avatar: '',
    location: '',
    links: [] as LinkRequest[],
  })

  const isSubmitting = ref(false)
  const submitError = ref<string | null>(null)

  function addLink(): void {
    form.links.push({ url: '', label: '' })
  }

  function removeLink(index: number): void {
    form.links.splice(index, 1)
  }

  async function submit(): Promise<void> {
    isSubmitting.value = true
    submitError.value = null
    try {
      const team = await teamApi.create({
        name: form.name,
        description: form.description,
        avatar: form.avatar || null,
        location: form.location,
        links: form.links.filter((link) => link.url.trim()),
      })
      await router.replace({ name: 'team', params: { id: team.id } })
    } catch (e) {
      submitError.value = e instanceof Error ? e.message : 'Не удалось создать команду'
    } finally {
      isSubmitting.value = false
    }
  }
</script>

<template>
  <div class="team-create-page">
    <header class="page-header">
      <button class="back-btn" @click="router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
      </button>
      <h1 class="page-header__title">Создать команду</h1>
      <div style="width: 36px" />
    </header>

    <form class="form" @submit.prevent="submit">
      <p v-if="submitError" class="form__error">{{ submitError }}</p>

      <section class="section">
        <h2 class="section__title">Основное</h2>
        <label class="field">
          <span class="field__label">Название <span class="required">*</span></span>
          <input v-model="form.name" type="text" class="field__input" required />
        </label>
        <label class="field">
          <span class="field__label">Описание</span>
          <textarea
            v-model="form.description"
            class="field__input field__input--textarea"
            rows="3"
          />
        </label>
        <label class="field">
          <span class="field__label">URL аватара</span>
          <input v-model="form.avatar" type="url" class="field__input" />
        </label>
        <label class="field">
          <span class="field__label">Локация</span>
          <input v-model="form.location" type="text" class="field__input" />
        </label>
      </section>

      <section class="section">
        <h2 class="section__title">Ссылки</h2>
        <div v-for="(link, index) in form.links" :key="index" class="link-row">
          <input v-model="form.links[index].url" type="url" class="field__input" placeholder="https://..." />
          <input v-model="form.links[index].label" type="text" class="field__input" placeholder="Название" />
          <button type="button" class="remove-btn" @click="removeLink(index)">
            Удалить
          </button>
        </div>
        <button type="button" class="add-btn" @click="addLink">
          + Добавить ссылку
        </button>
      </section>

      <button type="submit" class="submit-btn" :disabled="isSubmitting">
        {{ isSubmitting ? 'Создаём…' : 'Создать команду' }}
      </button>
    </form>
  </div>
</template>

<style scoped lang="scss">
  .team-create-page {
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

  .field {
    @include flex-column(6px);
  }

  .field__label {
    font-size: 13px;
    color: $color-text-secondary;
  }

  .required {
    color: $color-accent;
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

  .remove-btn,
  .add-btn {
    border: 1px solid $color-border;
    border-radius: $radius-md;
    background: transparent;
    color: $color-text-primary;
    font-size: 13px;
    padding: 8px 10px;
    cursor: pointer;
  }

  .submit-btn {
    margin: 0 16px 28px;
    border: none;
    border-radius: $radius-full;
    padding: 10px 18px;
    background: $color-accent;
    color: #fff;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;

    &:disabled {
      opacity: 0.5;
      cursor: wait;
    }

    @include respond-to('lg') {
      margin: 0;
      width: fit-content;
      justify-self: flex-start;
    }
  }
</style>
