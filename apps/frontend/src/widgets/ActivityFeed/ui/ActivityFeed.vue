<script setup lang="ts">
  import { computed } from 'vue'
  import type { ActivityItem, ActivityFilter } from '../model/types'
  import { formatDateShort, ratingStatusLabel } from '@shared/lib/format'

  const props = defineProps<{
    items: ActivityItem[]
    isLoading?: boolean
    activeFilter?: ActivityFilter
  }>()

  const emit = defineEmits<{
    'navigate-to-event': [id: number]
    'filter-change': [filter: ActivityFilter]
  }>()

  const filtered = computed(() => {
    if (!props.activeFilter || props.activeFilter === 'all') return props.items
    if (props.activeFilter === 'win')
      return props.items.filter((i) => i.status === 'winner' || i.status === 'prize_winner')
    return props.items
  })
</script>

<template>
  <div class="feed">
    <div class="feed__header">
      <span class="feed__title">Активность и победы</span>
      <span v-if="items.length" class="feed__count">{{ items.length }} событий</span>
    </div>

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

    <div class="events-grid">
      <template v-if="isLoading">
        <div v-for="n in 4" :key="n" class="event-card event-card--skeleton">
          <div class="skel skel--cover" />
          <div class="skel skel--line" />
          <div class="skel skel--line skel--short" />
        </div>
      </template>

      <div v-else-if="filtered.length === 0" class="empty">
        <p>Событий пока нет</p>
      </div>

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
          <div class="event-card__cover">
            <img
              v-if="item.event.cover"
              :src="item.event.cover"
              :alt="item.event.title"
              class="event-card__img"
            />
            <div v-else class="event-card__img event-card__img--placeholder" />
            <span v-if="ratingStatusLabel(item.status)" class="event-card__badge">
              <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12" aria-hidden="true">
                <path d="M8 1l1.94 4.27L14.5 5.8l-3.25 3.17.77 4.49L8 11.27l-4.02 2.19.77-4.49L1.5 5.8l4.56-.53L8 1z" />
              </svg>
              {{ ratingStatusLabel(item.status) }}
            </span>
          </div>

          <div class="event-card__body">
            <span class="event-card__type">Хакатон</span>
            <h3 class="event-card__title">{{ item.event.title }}</h3>
            <div class="event-card__meta">
              <span v-if="item.teamName" class="event-card__team">
                {{ item.teamName }}
              </span>
              <span class="event-card__date">{{ formatDateShort(item.event.date) }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped lang="scss">
  .feed {
    @include flex-column(12px);

    @include respond-to('lg') {
      gap: 16px;
    }
  }

  .events-grid {
    @include flex-column(12px);

    @include respond-to('lg') {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
  }


  .feed__header {
    @include flex-between;
  }

  .feed__title {
    font-size: 17px;
    font-weight: 700;
  }

  .feed__count {
    font-size: 13px;
    font-weight: 600;
    color: $color-accent;
    border: 1px solid $color-accent;
    border-radius: $radius-full;
    padding: 2px 10px;
  }

  .filters {
    display: flex;
    gap: 8px;
  }

  .filter-btn {
    padding: 6px 14px;
    border-radius: $radius-full;
    border: 1px solid $color-border;
    background: transparent;
    font-size: 13px;
    font-weight: 500;
    color: $color-text-primary;
    cursor: pointer;
    transition: background $transition-fast, border-color $transition-fast;

    &--active {
      background: $color-accent;
      border-color: $color-accent;
      color: -text-primary;
    }
  }

  .event-card {
    border: 1px solid $color-border;
    border-radius: $radius-2xl;
    overflow: hidden;
    @include card-interactive;

    &--winner {
      border-color: $color-accent;
    }

    &--skeleton {
      pointer-events: none;
    }
  }

  .event-card__cover {
    position: relative;
    height: 160px;
    background: -surface;
  }

  .event-card__img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;

    &--placeholder {
      background: -surface-soft;
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
    border-radius: $radius-full;
    background: rgba($color-accent, 0.9);
    font-size: 12px;
    font-weight: 600;
    color: -text-primary;
  }

  .event-card__body {
    @include flex-column(4px);
    padding: 12px 14px 14px;
  }

  .event-card__type {
    font-size: 12px;
    font-weight: 500;
    color: $color-accent;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .event-card__title {
    margin: 0;
    font-size: 16px;
    font-weight: 700;
  }

  .event-card__meta {
    @include flex-between;
    font-size: 13px;
    color: $color-text-secondary;
  }

  .skel {
    border-radius: $radius-sm;
    @include skeleton-shimmer;

    &--cover {
      height: 160px;
      border-radius: 0;
    }

    &--line {
      height: 14px;
      width: 70%;
      margin: 12px 14px 4px;
    }

    &--short {
      width: 45%;
      margin-top: 0;
    }
  }

  .empty {
    padding: 32px 0;
    text-align: center;
    color: $color-text-secondary;
    font-size: 14px;

    @include respond-to('lg') {
      grid-column: 1 / -1;
    }
  }
</style>
