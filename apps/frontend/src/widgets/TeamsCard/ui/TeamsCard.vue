<script setup lang="ts">
  export interface TeamEntry {
    id: number
    name: string
    role: string
    isActive: boolean
    winCount: number
    memberCount: number
  }

  defineProps<{
    teams: TeamEntry[]
    isLoading?: boolean
  }>()

  const emit = defineEmits<{
    'navigate-to-team': [id: number]
  }>()
</script>

<template>
  <div class="card">
    <div class="card__header">
      <span class="card__title">Команды</span>
      <span v-if="teams.length" class="card__subtitle">Состоит в {{ teams.length }} командах</span>
    </div>

    <!-- Skeleton -->
    <template v-if="isLoading">
      <div v-for="n in 2" :key="n" class="team-item team-item--skeleton">
        <div class="skeleton skeleton--name" />
        <div class="skeleton skeleton--line" />
      </div>
    </template>

    <!-- Empty -->
    <div v-else-if="teams.length === 0" class="empty">
      <p>Команд пока нет</p>
    </div>

    <!-- Teams -->
    <div
      v-for="team in teams"
      v-else
      :key="team.id"
      class="team-item"
      :class="{ 'team-item--active': team.isActive }"
    >
      <div class="team-item__header">
        <span class="team-item__name">{{ team.name }}</span>
        <span class="team-item__status" :class="team.isActive ? 'team-item__status--active' : 'team-item__status--inactive'">
          {{ team.isActive ? 'Активная' : 'Неактивная' }}
        </span>
      </div>
      <p class="team-item__role">Роль: {{ team.role }}</p>
      <div class="team-item__stats">
        <div class="team-stat">
          <span class="team-stat__value">{{ team.winCount }}</span>
          <span class="team-stat__label">побед</span>
        </div>
        <div class="team-stat">
          <span class="team-stat__value">{{ team.memberCount }}</span>
          <span class="team-stat__label">участников</span>
        </div>
      </div>
      <button class="team-item__link" @click="emit('navigate-to-team', team.id)">
        Профиль команды →
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
  .card {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .card__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .card__title {
    font-size: 17px;
    font-weight: 700;
    color: var(--p-text-primary);
  }

  .card__subtitle {
    font-size: 13px;
    color: var(--p-text-secondary);
  }

  .team-item {
    border: 1px solid var(--p-border);
    border-radius: 16px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;

    &--active {
      border-color: var(--p-accent);
    }

    &--skeleton {
      pointer-events: none;
    }
  }

  .team-item__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .team-item__name {
    font-size: 16px;
    font-weight: 700;
    color: var(--p-text-primary);
  }

  .team-item__status {
    font-size: 12px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 100px;

    &--active {
      background: rgba(255, 107, 43, 0.15);
      color: var(--p-accent);
      border: 1px solid var(--p-accent);
    }

    &--inactive {
      background: rgba(255, 255, 255, 0.06);
      color: var(--p-text-secondary);
      border: 1px solid var(--p-border);
    }
  }

  .team-item__role {
    margin: 0;
    font-size: 13px;
    color: var(--p-text-secondary);
  }

  .team-item__stats {
    display: flex;
    gap: 20px;
  }

  .team-stat {
    display: flex;
    flex-direction: column;
    gap: 1px;
  }

  .team-stat__value {
    font-size: 18px;
    font-weight: 700;
    color: var(--p-accent);
  }

  .team-stat__label {
    font-size: 11px;
    color: var(--p-text-secondary);
  }

  .team-item__link {
    background: none;
    border: none;
    padding: 0;
    font-size: 13px;
    font-weight: 600;
    color: var(--p-accent);
    cursor: pointer;
    text-align: left;
    margin-top: 4px;

    &:hover {
      text-decoration: underline;
    }
  }

  .skeleton {
    border-radius: 6px;
    background: linear-gradient(90deg, #252525 25%, #2e2e2e 50%, #252525 75%);
    background-size: 200% 100%;
    animation: shimmer 1.4s infinite;

    &--name {
      height: 18px;
      width: 55%;
    }

    &--line {
      height: 13px;
      width: 40%;
    }
  }

  @keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  .empty {
    padding: 24px 0;
    text-align: center;
    color: var(--p-text-secondary);
    font-size: 14px;
  }
</style>
