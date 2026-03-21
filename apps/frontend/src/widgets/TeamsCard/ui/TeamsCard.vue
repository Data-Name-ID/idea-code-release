<script setup lang="ts">
  import type { TeamEntry } from '../model/types'

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

    <template v-if="isLoading">
      <div v-for="n in 2" :key="n" class="team-item team-item--skeleton">
        <div class="skel skel--name" />
        <div class="skel skel--line" />
      </div>
    </template>

    <div v-else-if="teams.length === 0" class="empty">
      <p>Команд пока нет</p>
    </div>

    <div
      v-for="team in teams"
      v-else
      :key="team.id"
      class="team-item"
      :class="{ 'team-item--active': team.isActive }"
    >
      <div class="team-item__header">
        <span class="team-item__name">{{ team.name }}</span>
        <span
          class="team-item__status"
          :class="team.isActive ? 'team-item__status--active' : 'team-item__status--inactive'"
        >
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
    @include flex-column(12px);
  }

  .card__header {
    @include flex-between;
  }

  .card__title {
    font-size: 17px;
    font-weight: 700;
  }

  .card__subtitle {
    font-size: 13px;
    color: $color-text-secondary;
  }

  .team-item {
    border: 1px solid $color-border;
    border-radius: $radius-2xl;
    padding: 16px;
    @include flex-column(8px);

    &--active {
      border-color: $color-accent;
    }

    &--skeleton {
      pointer-events: none;
    }
  }

  .team-item__header {
    @include flex-between;
  }

  .team-item__name {
    font-size: 16px;
    font-weight: 700;
  }

  .team-item__status {
    font-size: 12px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: $radius-full;

    &--active {
      background: rgba($color-accent, 0.15);
      color: $color-accent;
      border: 1px solid $color-accent;
    }

    &--inactive {
      background: rgba(255, 255, 255, 0.06);
      color: $color-text-secondary;
      border: 1px solid $color-border;
    }
  }

  .team-item__role {
    margin: 0;
    font-size: 13px;
    color: $color-text-secondary;
  }

  .team-item__stats {
    display: flex;
    gap: 20px;
  }

  .team-stat {
    @include flex-column(1px);
  }

  .team-stat__value {
    font-size: 18px;
    font-weight: 700;
    color: $color-accent;
  }

  .team-stat__label {
    font-size: 11px;
    color: $color-text-secondary;
  }

  .team-item__link {
    background: none;
    border: none;
    padding: 0;
    font-size: 13px;
    font-weight: 600;
    color: $color-accent;
    cursor: pointer;
    text-align: left;
    margin-top: 4px;

    &:hover {
      text-decoration: underline;
    }
  }

  .skel {
    border-radius: 6px;
    @include skeleton-shimmer;

    &--name {
      height: 18px;
      width: 55%;
    }

    &--line {
      height: 13px;
      width: 40%;
    }
  }

  .empty {
    padding: 24px 0;
    text-align: center;
    color: $color-text-secondary;
    font-size: 14px;
  }
</style>
