<script setup lang="ts">
  import type { RoleResponse, SkillResponse } from '@shared/types/api'

  defineProps<{
    roles: RoleResponse[]
    skills: SkillResponse[]
  }>()
</script>

<template>
  <div class="card">
    <div class="card__header">
      <span class="card__title">Специализация</span>
      <span class="card__subtitle">Роли и навыки</span>
    </div>

    <div v-if="roles.length" class="section">
      <div class="section__label">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="14" height="14" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 0 0 .75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 0 0-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0 1 12 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 0 1-.673-.38m0 0A2.18 2.18 0 0 1 3 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 0 1 3.413-.387m7.5 0V5.25A2.25 2.25 0 0 0 13.5 3h-3a2.25 2.25 0 0 0-2.25 2.25v.894m7.5 0a48.667 48.667 0 0 0-7.5 0M12 12.75h.008v.008H12v-.008Z" />
        </svg>
        <span>Роли</span>
      </div>
      <div class="roles-list">
        <div v-for="role in roles" :key="role.id" class="role-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="14" height="14" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5" />
          </svg>
          <span>{{ role.name }}</span>
        </div>
      </div>
    </div>

    <div v-if="skills.length" class="section">
      <div class="section__label section__label--mono">
        <span>&gt;_</span>
        <span>Навыки</span>
      </div>
      <div class="skills-list">
        <span v-for="skill in skills" :key="skill.id" class="skill-chip">
          {{ skill.name }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
  .card {
    border: 1px solid $color-accent;
    border-radius: $radius-2xl;
    padding: 16px;
    @include flex-column(16px);
  }

  .card__header {
    @include flex-between;
  }

  .card__title {
    font-size: 16px;
    font-weight: 700;
  }

  .card__subtitle {
    font-size: 13px;
    color: $color-text-secondary;
  }

  .section {
    @include flex-column(10px);
    border: 1px solid $color-accent;
    border-radius: $radius-lg;
    padding: 14px;
  }

  .section__label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    font-weight: 600;
    color: $color-accent;

    &--mono {
      font-family: $font-family-mono;
    }
  }

  .roles-list {
    @include flex-column(8px);
  }

  .role-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border: 1px solid $color-border;
    border-radius: $radius-md;
    font-size: 14px;
    font-weight: 500;

    svg {
      color: $color-text-secondary;
      flex-shrink: 0;
    }
  }

  .skills-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .skill-chip {
    padding: 6px 12px;
    border: 1px solid $color-border;
    border-radius: $radius-full;
    font-size: 13px;
  }
</style>
