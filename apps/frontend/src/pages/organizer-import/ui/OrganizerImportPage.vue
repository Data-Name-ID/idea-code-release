<script setup lang="ts">
  import { computed, ref } from 'vue'
  import { useRouter } from 'vue-router'

  import { organizerImportApi } from '@entities/organizer-import/api'
  import type {
    OrganizerImportError,
    OrganizerImportRequest,
    OrganizerImportResponse,
    OrganizerMemberInput,
    OrganizerResultInput,
    OrganizerTeamInput,
  } from '@shared/types/api'
  import {
    EMPTY_IMPORT_PAYLOAD,
    clearStoredOrganizerApiKey,
    countMembers,
    createCsvTemplateContent,
    createJsonTemplateContent,
    createXlsxTemplateBlob,
    getStoredOrganizerApiKey,
    parseImportFile,
    placeFromStatus,
    setStoredOrganizerApiKey,
    statusFromPlace,
    validateImportPayload,
  } from '@pages/organizer-import/model/import'

  type Mode = 'file' | 'wizard'

  const router = useRouter()
  const mode = ref<Mode>('file')
  const apiKey = ref(getStoredOrganizerApiKey())
  const isSubmitting = ref(false)
  const isParsing = ref(false)
  const submitError = ref<string | null>(null)
  const parseError = ref<string | null>(null)
  const parseWarnings = ref<string[]>([])
  const selectedFileName = ref('')
  const response = ref<OrganizerImportResponse | null>(null)

  const payload = ref<OrganizerImportRequest>(structuredClone(EMPTY_IMPORT_PAYLOAD))
  const validationErrors = computed(() => validateImportPayload(payload.value))
  const memberCount = computed(() => countMembers(payload.value))
  const canSubmit = computed(() => apiKey.value.trim() !== '' && validationErrors.value.length === 0 && !isSubmitting.value)

  async function handleFileChange(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement
    const file = input.files?.[0]
    if (!file) return

    selectedFileName.value = file.name
    parseError.value = null
    parseWarnings.value = []
    response.value = null

    isParsing.value = true
    try {
      const parsed = await parseImportFile(file)
      payload.value = parsed.payload
      parseWarnings.value = parsed.warnings
      mode.value = 'wizard'
    } catch (error) {
      parseError.value = error instanceof Error ? error.message : 'Не удалось обработать файл'
    } finally {
      isParsing.value = false
      input.value = ''
    }
  }

  function downloadTemplate(type: 'json' | 'csv' | 'xlsx'): void {
    if (type === 'json') {
      downloadBlob('organizer-template.json', new Blob([createJsonTemplateContent()], { type: 'application/json' }))
      return
    }

    if (type === 'csv') {
      downloadBlob('organizer-template.csv', new Blob([createCsvTemplateContent()], { type: 'text/csv;charset=utf-8' }))
      return
    }

    downloadBlob('organizer-template.xlsx', createXlsxTemplateBlob())
  }

  function downloadBlob(fileName: string, blob: Blob): void {
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    link.click()
    URL.revokeObjectURL(url)
  }

  function rememberApiKey(): void {
    setStoredOrganizerApiKey(apiKey.value)
  }

  function clearApiKey(): void {
    apiKey.value = ''
    clearStoredOrganizerApiKey()
  }

  function addTeam(): void {
    payload.value.teams.push({
      external_id: '',
      name: '',
      description: '',
      members: [],
    })
  }

  function removeTeam(index: number): void {
    payload.value.teams.splice(index, 1)
  }

  function addMember(team: OrganizerTeamInput): void {
    if (!team.members) team.members = []
    team.members.push(emptyMember())
  }

  function removeMember(team: OrganizerTeamInput, memberIndex: number): void {
    team.members?.splice(memberIndex, 1)
  }

  function addResult(): void {
    payload.value.results.push({
      status: 'participant',
      place: 4,
      awarded_at: '',
      team_external_id: '',
      user: null,
    })
  }

  function removeResult(index: number): void {
    payload.value.results.splice(index, 1)
  }

  function setResultStatus(result: OrganizerResultInput, status: 'winner' | 'prize_winner' | 'participant'): void {
    result.status = status
    if (typeof result.place !== 'number' || result.place <= 0) {
      result.place = placeFromStatus(status)
    }
  }

  function setResultPlace(result: OrganizerResultInput, value: string): void {
    const num = Number(value)
    if (!Number.isFinite(num) || num <= 0) {
      result.place = null
      return
    }
    result.place = num
    if (!result.status) result.status = statusFromPlace(num)
  }

  function ensureResultUser(result: OrganizerResultInput): void {
    if (!result.user) result.user = emptyMember()
    result.team_external_id = ''
  }

  function isTeamTarget(result: OrganizerResultInput): boolean {
    return result.user == null
  }

  function setTeamTarget(result: OrganizerResultInput): void {
    result.user = null
    if (!result.team_external_id) result.team_external_id = ''
  }

  function emptyMember(): OrganizerMemberInput {
    return {
      telegram_id: null,
      email: '',
      username: '',
      name: '',
      avatar: '',
    }
  }

  async function submitImport(): Promise<void> {
    submitError.value = null
    response.value = null

    if (apiKey.value.trim() === '') {
      submitError.value = 'Введите X-API-Key'
      return
    }

    if (validationErrors.value.length > 0) {
      submitError.value = 'Исправьте ошибки перед отправкой'
      return
    }

    isSubmitting.value = true
    try {
      rememberApiKey()
      response.value = await organizerImportApi.importData(payload.value, apiKey.value)
    } catch (error) {
      submitError.value = error instanceof Error ? error.message : 'Ошибка отправки'
    } finally {
      isSubmitting.value = false
    }
  }

  function summaryTitle(errors: OrganizerImportError[]): string {
    return errors.length === 0 ? 'Импорт завершен' : `Импорт с ошибками (${errors.length})`
  }
</script>

<template>
  <div class="organizer-page">
    <header class="page-header">
      <button class="back-btn" @click="router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
      </button>
      <h1 class="page-header__title">Импорт хакатона</h1>
      <button type="button" class="submit-top" :disabled="!canSubmit" @click="submitImport">
        {{ isSubmitting ? 'Отправка...' : 'Отправить' }}
      </button>
    </header>

    <main class="page-body">
      <section class="hero">
        <div class="hero__main">
          <h2>Один запрос = один хакатон</h2>
          <div class="summary-grid">
            <div class="summary-item">
              <span>Команды</span>
              <strong>{{ payload.teams.length }}</strong>
            </div>
            <div class="summary-item">
              <span>Участники</span>
              <strong>{{ memberCount }}</strong>
            </div>
            <div class="summary-item">
              <span>Результаты</span>
              <strong>{{ payload.results.length }}</strong>
            </div>
          </div>
        </div>
        <div class="token-box">
          <label for="api-key">X-API-Key</label>
          <input id="api-key" v-model="apiKey" type="password" placeholder="Токен организатора" @blur="rememberApiKey">
          <div class="token-actions">
            <button type="button" class="button-secondary" @click="rememberApiKey">Сохранить</button>
            <button type="button" class="button-ghost" @click="clearApiKey">Очистить</button>
          </div>
        </div>
      </section>

      <section class="mode-switch">
        <button type="button" class="mode-switch__button" :class="{ 'mode-switch__button--active': mode === 'file' }" @click="mode = 'file'">Файл</button>
        <button type="button" class="mode-switch__button" :class="{ 'mode-switch__button--active': mode === 'wizard' }" @click="mode = 'wizard'">Редактор</button>
      </section>

      <section v-if="mode === 'file'" class="section-card">
        <div class="section-head">
          <h3>Загрузка файла</h3>
          <div class="template-actions">
            <button type="button" class="button-ghost" @click="downloadTemplate('xlsx')">XLSX</button>
            <button type="button" class="button-ghost" @click="downloadTemplate('csv')">CSV</button>
            <button type="button" class="button-ghost" @click="downloadTemplate('json')">JSON</button>
          </div>
        </div>

        <label class="upload-zone">
          <input type="file" accept=".xlsx,.csv,.json" @change="handleFileChange">
          <span class="upload-zone__title">Выберите файл</span>
          <span class="upload-zone__meta">.xlsx / .csv / .json</span>
        </label>

        <p v-if="selectedFileName" class="state-line">{{ selectedFileName }}</p>
        <p v-if="isParsing" class="state-line">Обработка файла...</p>
        <p v-if="parseError" class="error">{{ parseError }}</p>
        <ul v-if="parseWarnings.length" class="warning-list">
          <li v-for="warning in parseWarnings" :key="warning">{{ warning }}</li>
        </ul>
      </section>

      <section v-if="mode === 'wizard'" class="wizard">
        <div class="section-card">
          <h3>Хакатон</h3>
          <div class="form-grid">
            <label>external_id <input v-model="payload.hackathon.external_id" type="text"></label>
            <label>Название <input v-model="payload.hackathon.title" type="text"></label>
            <label>Дата (ISO) <input v-model="payload.hackathon.date" type="text" placeholder="2026-04-20T10:00:00Z"></label>
            <label>Cover URL <input v-model="payload.hackathon.cover" type="text"></label>
            <label class="full">Описание <textarea v-model="payload.hackathon.description" rows="2" /></label>
          </div>
        </div>

        <div class="section-card">
          <div class="section-head">
            <h3>Команды</h3>
            <button type="button" class="button-secondary" @click="addTeam">Добавить</button>
          </div>

          <div v-if="payload.teams.length === 0" class="empty-block">
            <button type="button" class="button-ghost" @click="addTeam">Добавить первую команду</button>
          </div>

          <div v-for="(team, teamIndex) in payload.teams" :key="teamIndex" class="nested-card">
            <div class="section-head section-head--compact">
              <h4>Команда #{{ teamIndex + 1 }}</h4>
              <button type="button" class="button-ghost" @click="removeTeam(teamIndex)">Удалить</button>
            </div>

            <div class="form-grid">
              <label>external_id <input v-model="team.external_id" type="text"></label>
              <label>Название <input v-model="team.name" type="text"></label>
              <label class="full">Описание <textarea v-model="team.description" rows="2" /></label>
            </div>

            <div class="members">
              <div class="section-head section-head--compact">
                <h4>Участники</h4>
                <button type="button" class="button-ghost" @click="addMember(team)">Добавить</button>
              </div>

              <div v-for="(member, memberIndex) in team.members" :key="memberIndex" class="member-row">
                <input v-model="member.name" type="text" placeholder="Имя">
                <input v-model="member.email" type="text" placeholder="email">
                <input v-model.number="member.telegram_id" type="number" placeholder="telegram_id">
                <button type="button" class="button-ghost member-remove" @click="removeMember(team, memberIndex)">✕</button>
              </div>
            </div>
          </div>
        </div>

        <div class="section-card">
          <div class="section-head">
            <h3>Результаты</h3>
            <button type="button" class="button-secondary" @click="addResult">Добавить</button>
          </div>

          <div v-if="payload.results.length === 0" class="empty-block">
            <button type="button" class="button-ghost" @click="addResult">Добавить первый результат</button>
          </div>

          <div v-for="(result, resultIndex) in payload.results" :key="resultIndex" class="nested-card">
            <div class="section-head section-head--compact">
              <h4>Результат #{{ resultIndex + 1 }}</h4>
              <button type="button" class="button-ghost" @click="removeResult(resultIndex)">Удалить</button>
            </div>

            <div class="form-grid">
              <label>Статус
                <select :value="result.status ?? 'participant'" @change="setResultStatus(result, ($event.target as HTMLSelectElement).value as 'winner' | 'prize_winner' | 'participant')">
                  <option value="winner">winner</option>
                  <option value="prize_winner">prize_winner</option>
                  <option value="participant">participant</option>
                </select>
              </label>
              <label>Место
                <input :value="result.place ?? ''" type="number" min="1" @input="setResultPlace(result, ($event.target as HTMLInputElement).value)">
              </label>
              <label>awarded_at
                <input v-model="result.awarded_at" type="text" placeholder="2026-04-20T18:00:00Z">
              </label>
            </div>

            <div class="target-block">
              <div class="target-switch" role="tablist" aria-label="Тип результата">
                <button
                  type="button"
                  class="target-switch__option"
                  :class="{ 'target-switch__option--active': isTeamTarget(result) }"
                  @click="setTeamTarget(result)"
                >
                  Команда
                </button>
                <button
                  type="button"
                  class="target-switch__option"
                  :class="{ 'target-switch__option--active': !isTeamTarget(result) }"
                  @click="ensureResultUser(result)"
                >
                  Персонально
                </button>
              </div>

              <div v-if="isTeamTarget(result)" class="form-grid">
                <label class="full">team_external_id
                  <input v-model="result.team_external_id" type="text" placeholder="team-alpha">
                </label>
              </div>

              <div v-else class="form-grid">
                <label>Имя <input v-model="result.user.name" type="text"></label>
                <label>email <input v-model="result.user.email" type="text"></label>
                <label>telegram_id <input v-model.number="result.user.telegram_id" type="number"></label>
              </div>
            </div>
          </div>
        </div>

        <div class="section-card submit-card">
          <ul v-if="validationErrors.length" class="error-list">
            <li v-for="error in validationErrors" :key="error">{{ error }}</li>
          </ul>

          <button type="button" class="submit-btn" :disabled="!canSubmit" @click="submitImport">
            {{ isSubmitting ? 'Отправка...' : 'Отправить в API' }}
          </button>
          <p v-if="submitError" class="error">{{ submitError }}</p>
        </div>
      </section>

      <section v-if="response" class="section-card response-card">
        <h3>{{ summaryTitle(response.errors) }}</h3>
        <div class="summary-grid">
          <div class="summary-item"><span>Hackathons</span><strong>{{ response.hackathons.created }}/{{ response.hackathons.updated }}/{{ response.hackathons.skipped }}</strong></div>
          <div class="summary-item"><span>Teams</span><strong>{{ response.teams.created }}/{{ response.teams.updated }}/{{ response.teams.skipped }}</strong></div>
          <div class="summary-item"><span>Results</span><strong>{{ response.results.created }}/{{ response.results.updated }}/{{ response.results.skipped }}</strong></div>
        </div>

        <div v-if="response.errors.length" class="response-errors">
          <ul>
            <li v-for="(item, index) in response.errors" :key="index">[{{ item.entity }}] {{ item.key }} — {{ item.detail }}</li>
          </ul>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped lang="scss">
  .organizer-page {
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

  .submit-top {
    border: none;
    border-radius: $radius-full;
    background: $color-accent;
    color: -text-primary;
    padding: 7px 14px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;

    &:disabled {
      opacity: .45;
      cursor: not-allowed;
    }
  }

  .page-body {
    @include flex-column(16px);
    padding: 16px;

    @include respond-to('lg') {
      max-width: 1100px;
      margin: 0 auto;
      padding: 28px 24px 56px;
      gap: 20px;
    }
  }

  .hero,
  .section-card,
  .nested-card {
    border: 1px solid $color-border;
    border-radius: $radius-2xl;
    background: $color-surface;
  }

  .hero {
    padding: 16px;
    display: grid;
    gap: 16px;

    @include respond-to('lg') {
      grid-template-columns: 1.4fr 1fr;
      align-items: end;
    }
  }

  .hero__main {
    @include flex-column(14px);

    h2 {
      margin: 0;
      font-size: 20px;
      line-height: 1.25;
    }
  }

  .summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 10px;
  }

  .summary-item {
    border: 1px solid rgba($color-accent, 0.3);
    border-radius: $radius-lg;
    background: rgba($color-accent, 0.08);
    padding: 10px;
    @include flex-column(4px);

    span {
      color: $color-text-secondary;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .06em;
    }

    strong {
      font-size: 18px;
      line-height: 1.1;
    }
  }

  .token-box {
    @include flex-column(8px);

    label {
      font-size: 12px;
      color: $color-text-secondary;
      letter-spacing: .04em;
      text-transform: uppercase;
    }
  }

  .token-actions {
    display: flex;
    gap: 8px;
  }

  .mode-switch {
    display: inline-flex;
    gap: 6px;
    border: 1px solid $color-border;
    border-radius: $radius-full;
    padding: 4px;
    background: rgba($color-surface, 0.75);
    width: fit-content;
  }

  .mode-switch__button {
    border: none;
    border-radius: $radius-full;
    background: transparent;
    color: $color-text-secondary;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;

    &--active {
      background: rgba($color-accent, 0.18);
      color: $color-text-primary;
    }
  }

  .section-card {
    padding: 16px;
    @include flex-column(12px);

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 700;
    }
  }

  .section-head {
    @include flex-between;
    gap: 10px;
    flex-wrap: wrap;
  }

  .section-head--compact {
    h4 {
      margin: 0;
      font-size: 14px;
    }
  }

  .wizard {
    @include flex-column(14px);
  }

  .nested-card {
    padding: 14px;
    border-radius: $radius-lg;
    @include flex-column(12px);
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 10px;

    .full {
      grid-column: 1 / -1;
    }
  }

  label {
    @include flex-column(6px);
    font-size: 13px;
    color: $color-text-secondary;
  }

  input[type='text'],
  input[type='password'],
  input[type='number'],
  input:not([type]),
  select,
  textarea {
    @include field-control;
    background: $color-bg-elevated;
    min-height: 40px;
  }

  .upload-zone {
    border: 1px dashed rgba($color-accent, 0.45);
    border-radius: $radius-lg;
    background: rgba($color-accent, 0.04);
    padding: 18px;
    @include flex-column(6px);
    cursor: pointer;

    input {
      display: none;
    }
  }

  .upload-zone__title {
    color: $color-text-primary;
    font-size: 14px;
    font-weight: 600;
  }

  .upload-zone__meta,
  .state-line {
    margin: 0;
    color: $color-text-secondary;
    font-size: 13px;
  }

  .members {
    @include flex-column(10px);
  }

  .member-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr auto;
    gap: 8px;

    @include respond-to('md') {
      grid-template-columns: 1fr;
    }
  }

  .member-remove {
    min-width: 40px;
  }

  .empty-block {
    border: 1px dashed $color-border;
    border-radius: $radius-lg;
    padding: 12px;
  }

  .target-block {
    @include flex-column(10px);
    border: 1px dashed rgba($color-accent, 0.25);
    border-radius: $radius-lg;
    padding: 12px;
    background: rgba($color-surface, 0.35);
  }

  .target-switch {
    display: inline-flex;
    gap: 8px;
    width: fit-content;
    padding: 4px;
    border: 1px solid $color-border;
    border-radius: $radius-full;
    background: rgba($color-surface, 0.75);
  }

  .target-switch__option {
    border: 1px solid transparent;
    border-radius: $radius-full;
    background: transparent;
    color: $color-text-secondary;
    font: inherit;
    font-size: 13px;
    font-weight: 600;
    padding: 6px 12px;
    cursor: pointer;

    &--active {
      border-color: rgba($color-accent, 0.35);
      background: rgba($color-accent, 0.16);
      color: $color-text-primary;
    }

    &:focus-visible {
      outline: none;
      box-shadow: 0 0 0 1px rgba($color-accent, 0.45);
    }
  }

  .template-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .button-secondary,
  .button-ghost,
  .submit-btn {
    border-radius: $radius-md;
    padding: 8px 12px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
  }

  .button-secondary {
    border: none;
    background: rgba($color-accent, 0.22);
    color: $color-text-primary;
  }

  .button-ghost {
    border: 1px solid $color-border;
    background: transparent;
    color: $color-text-primary;
  }

  .submit-card {
    gap: 10px;
  }

  .submit-btn {
    border: none;
    background: $color-accent;
    color: -text-primary;
    padding: 10px 16px;

    &:disabled {
      opacity: .45;
      cursor: not-allowed;
    }
  }

  .error,
  .warning-list,
  .error-list {
    margin: 0;
    color: $color-danger;
    font-size: 13px;
  }

  .warning-list,
  .error-list,
  .response-errors ul {
    padding-left: 18px;
    @include flex-column(4px);
  }

  .response-card {
    border-color: rgba($color-success, 0.35);
    background: rgba($color-success, 0.08);
  }
</style>
