<script setup lang="ts">
  import { computed } from 'vue'
  import type { EventResponse, EventRatingStatus } from '@shared/types/api'

  export interface ActivityItem {
    event: EventResponse
    status: EventRatingStatus | null
    teamName: string | null
  }

  const props = defineProps<{
    items: ActivityItem[]
    isLoading?: boolean
    activeFilter?: 'all' | 'hackathon' | 'win'
  }>()

  const emit = defineEmits<{
    'navigate-to-event': [id: number]
    'filter-change': [filter: 'all' | 'hackathon' | 'win']
  }>()

  const filtered = computed(() => {
    if (!props.activeFilter || props.activeFilter === 'all') return props.items
    if (props.activeFilter === 'win')
      return props.items.filter((i) => i.status === 'winner' || i.status === 'prize_winner')
    return props.items
  })

  function statusLabel(status: EventRatingStatus | null): string | null {
    if (status === 'winner') return '1-е место'
    if (status === 'prize_winner') return '2-е место'
    return null
  }

  function formatDate(iso: string): string {
    return new Intl.DateTimeFormat('ru-RU', { month: 'short', year: 'numeric' }).format(
      new Date(iso),
    )
  }
</script>

<template>
  <div class="feed">
    <div class="feed__header">
      <span class="feed__title">Активность и победы</span>
      <span v-if="items.length" class="feed__count">{{ items.length }} событий</span>
    </div>

    <!-- Filters -->
    <div class="filters">
      <button
        class="filter-btn"
        :class="{ 'filter-btn--active': !activeFilter || activeFilter === 'all' }"
        @click="emit('filter-change', 'all')"
      >
        Всё
      </button>
      <button
        class="filter-btn"
        :class="{ 'filter-btn--active': activeFilter === 'hackathon' }"
        @click="emit('filter-change', 'hackathon')"
      >
        Хакатоны
      </button>
      <button
        class="filter-btn"
        :class="{ 'filter-btn--active': activeFilter === 'win' }"
        @click="emit('filter-change', 'win')"
      >
        Победы
      </button>
    </div>

    <!-- Skeleton -->
    <template v-if="isLoading">
      <div v-for="n in 3" :key="n" class="event-card event-card--skeleton">
        <div class="skeleton skeleton--cover" />
        <div class="skeleton skeleton--line" />
        <div class="skeleton skeleton--line skeleton--line-sm" />
      </div>
    </template>

    <!-- Empty -->
    <div v-else-if="filtered.length === 0" class="empty">
      <p>Событий пока нет</p>
    </div>

    <!-- Items -->
    <template v-else>
      <div
        v-for="item in filtered"
        :key="item.event.id"
        class="event-card"
        :class="{ 'event-card--winner': item.status === 'winner' }"
        role="button"
        tabindex="0"
        @click="emit('navigate-to-event', item.event.id)"
        @keydown.enter="emit('navigate-to-event', item.event.id)"
      >
        <!-- Cover image -->
        <div class="event-card__cover">
          <img
            v-if="item.event.cover"
            :src="item.event.cover"
            :alt="item.event.title"
            class="event-card__img"
          />
          <div v-else class="event-card__img event-card__img--placeholder" />
          <span v-if="statusLabel(item.status)" class="event-card__badge">
            <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12" aria-hidden="true">
              <path d="M8 1l1.94 4.27L14.5 5.8l-3.25 3.17.77 4.49L8 11.27l-4.02 2.19.77-4.49L1.5 5.8l4.56-.53L8 1z" />
            </svg>
            {{ statusLabel(item.status) }}
          </span>
        </div>

        <!-- Content -->
        <div class="event-card__body">
          <span class="event-card__type">Хакатон</span>
          <h3 class="event-card__title">{{ item.event.title }}</h3>
          <div class="event-card__meta">
            <span v-if="item.teamName" class="event-card__team">
              Команда: {{ item.teamName }}
            </span>
            <span class="event-card__date">{{ formatDate(item.event.date) }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
  .feed {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .feed__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .feed__title {
    font-size: 17px;
    font-weight: 700;
    color: var(--p-text-primary);
  }

  .feed__count {
    font-size: 13px;
    font-weight: 600;
    color: var(--p-accent);
    border: 1px solid var(--p-accent);
    border-radius: 100px;
    padding: 2px 10px;
  }

  .filters {
    display: flex;
    gap: 8px;
  }

  .filter-btn {
    padding: 6px 14px;
    border-radius: 100px;
    border: 1px solid var(--p-border);
    background: transparent;
    font-size: 13px;
    font-weight: 500;
    color: var(--p-text-primary);
    cursor: pointer;
    transition: background 150ms, border-color 150ms;

    &--active {
      background: var(--p-accent);
      border-color: var(--p-accent);
      color: #fff;
    }
  }

  .event-card {
    border: 1px solid var(--p-border);
    border-radius: 16px;
    overflow: hidden;
    cursor: pointer;
    transition: border-color 150ms;

    &:hover {
      border-color: var(--p-text-secondary);
    }

    &--winner {
      border-color: var(--p-accent);
    }

    &--skeleton {
      pointer-events: none;
    }
  }

  .event-card__cover {
    position: relative;
    height: 160px;
    background: #1e1e1e;
  }

  .event-card__img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;

    &--placeholder {
      background: #2a2a2a;
    }
  }

  .event-card__badge {
    position: absolute;
    top: 10px;
    right: 10px;
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 100px;
    background: rgba(255, 107, 43, 0.9);
    font-size: 12px;
    font-weight: 600;
    color: #fff;
  }

  .event-card__body {
    padding: 12px 14px 14px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .event-card__type {
    font-size: 12px;
    font-weight: 500;
    color: var(--p-accent);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .event-card__title {
    margin: 0;
    font-size: 16px;
    font-weight: 700;
    color: var(--p-text-primary);
  }

  .event-card__meta {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: var(--p-text-secondary);
  }

  .skeleton {
    border-radius: 8px;
    background: linear-gradient(90deg, #252525 25%, #2e2e2e 50%, #252525 75%);
    background-size: 200% 100%;
    animation: shimmer 1.4s infinite;

    &--cover {
      height: 160px;
      border-radius: 0;
    }

    &--line {
      height: 14px;
      width: 70%;
      margin: 12px 14px 4px;

      &-sm {
        width: 45%;
        margin-top: 0;
      }
    }
  }

  @keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  .empty {
    padding: 32px 0;
    text-align: center;
    color: var(--p-text-secondary);
    font-size: 14px;
  }
</style>
