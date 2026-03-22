<script setup lang="ts">
  import { computed, onMounted, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  import { teamApi } from '@entities/team/api'

  const route = useRoute()
  const router = useRouter()

  const token = computed(() => {
    const raw = route.query.token
    return typeof raw === 'string' ? raw : ''
  })

  const isJoining = ref(false)
  const joinError = ref<string | null>(null)
  const joinedTeam = ref<Awaited<ReturnType<typeof teamApi.getById>> | null>(null)

  onMounted(() => {
    joinByInvite()
  })

  async function joinByInvite(): Promise<void> {
    if (!token.value) {
      joinError.value = 'В ссылке отсутствует токен приглашения'
      return
    }
    isJoining.value = true
    joinError.value = null
    joinedTeam.value = null

    try {
      joinedTeam.value = await teamApi.joinByInvite({ token: token.value })
    } catch (e) {
      joinError.value = e instanceof Error ? e.message : 'Не удалось вступить в команду'
    } finally {
      isJoining.value = false
    }
  }
</script>

<template>
  <div class="team-join-page">
    <header class="page-header">
      <button class="back-btn" @click="router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
      </button>
      <h1 class="page-header__title">Вступление в команду</h1>
      <div style="width: 36px" />
    </header>

    <main class="content">
      <div v-if="isJoining" class="state-card">
        <p>Проверяем приглашение и добавляем вас в команду…</p>
      </div>

      <div v-else-if="joinError" class="state-card state-card--error">
        <p>{{ joinError }}</p>
        <button class="action-btn" @click="joinByInvite">Повторить</button>
      </div>

      <div v-else-if="joinedTeam" class="state-card state-card--success">
        <p>Вы успешно вступили в команду «{{ joinedTeam.name }}».</p>
        <button class="action-btn" @click="router.replace({ name: 'team', params: { id: joinedTeam.id } })">
          Перейти в профиль команды
        </button>
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
  .team-join-page {
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

  .content {
    padding: 24px 16px 48px;

    @include respond-to('lg') {
      max-width: 620px;
      margin: 0 auto;
      padding: 40px 32px 64px;
    }
  }

  .state-card {
    border: 1px solid $color-border;
    border-radius: $radius-2xl;
    background: #141417;
    padding: 20px 18px;
    color: $color-text-primary;
    @include flex-column(12px);

    p {
      margin: 0;
      font-size: 14px;
      line-height: 1.5;
    }
  }

  .state-card--error {
    border-color: rgba($color-danger, 0.5);
    background: rgba($color-danger, 0.1);
  }

  .state-card--success {
    border-color: rgba($color-accent, 0.5);
    background: rgba($color-accent, 0.08);
  }

  .action-btn {
    width: fit-content;
    border: none;
    border-radius: $radius-full;
    padding: 8px 14px;
    background: $color-accent;
    color: #fff;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
  }
</style>
