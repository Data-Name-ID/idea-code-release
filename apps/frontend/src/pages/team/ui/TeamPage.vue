<script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  import { teamApi } from '@entities/team/api'
  import { eventApi } from '@entities/event/api'
  import type { EventRatingStatus } from '@shared/types/api'
  import { formatDateLong, initials, ratingStatusLabel } from '@shared/lib/format'

  const route = useRoute()
  const router = useRouter()
  const teamId = computed(() => Number(route.params.id))

  const team = ref<Awaited<ReturnType<typeof teamApi.getById>> | null>(null)
  const isLoading = ref(true)
  const error = ref<string | null>(null)

  interface EventResult {
    id: number
    title: string
    date: string
    cover: string | null
    isVerified: boolean
    status: EventRatingStatus | null
  }

  const eventResults = ref<EventResult[]>([])
  const members = computed(() => team.value?.users ?? [])
  const winCount = computed(
    () => eventResults.value.filter((e) => e.status === 'winner' || e.status === 'prize_winner').length,
  )

  onMounted(async () => {
    try {
      const teamData = await teamApi.getById(teamId.value)
      team.value = teamData

      const ratingsArr = await Promise.all(
        teamData.events.map((event) => eventApi.getRatings(event.id).catch(() => null)),
      )

      eventResults.value = teamData.events
        .map((event, i) => {
          const ratings = ratingsArr[i]
          const entry = ratings?.ratings.find((r) => r.team_id === teamId.value) ?? null
          return {
            id: event.id,
            title: event.title,
            date: event.date,
            cover: event.cover,
            isVerified: event.is_verify,
            status: entry?.status ?? null,
          }
        })
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    } catch {
      error.value = 'Не удалось загрузить команду'
    } finally {
      isLoading.value = false
    }
  })

  function statusClass(status: EventRatingStatus | null): string {
    if (status === 'winner') return 'event-card--winner'
    if (status === 'prize_winner') return 'event-card--prize'
    return ''
  }
</script>

<template>
  <div class="team-page">
    <header class="page-header">
      <button class="back-btn" @click="router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
      </button>
      <span class="page-header__title">Команда</span>
      <div style="width: 36px" />
    </header>

    <template v-if="isLoading">
      <div class="hero-skeleton">
        <div class="skel skel--icon" />
        <div class="skel skel--title" />
        <div class="skel skel--line" />
        <div class="skel-stats">
          <div class="skel skel--stat" />
          <div class="skel skel--stat" />
        </div>
      </div>
    </template>

    <div v-else-if="error" class="state-empty">
      <p>{{ error }}</p>
    </div>

    <template v-else-if="team">
      <section class="hero">
        <div class="hero__icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="32" height="32">
            <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
          </svg>
        </div>
        <h1 class="hero__name">{{ team.name }}</h1>
        <p v-if="team.description" class="hero__description">{{ team.description }}</p>
        <div class="hero__stats">
          <div class="stat">
            <span class="stat__value">{{ members.length }}</span>
            <span class="stat__label">Участников</span>
          </div>
          <div class="stat">
            <span class="stat__value">{{ eventResults.length }}</span>
            <span class="stat__label">Мероприятий</span>
          </div>
          <div class="stat stat--accent">
            <span class="stat__value">{{ winCount }}</span>
            <span class="stat__label">Побед</span>
          </div>
        </div>
      </section>

      <section class="section">
        <h2 class="section__title">Участники</h2>
        <div class="member-list">
          <div
            v-for="member in members"
            :key="member.id"
            class="member"
            role="button"
            tabindex="0"
            @click="router.push(`/users/${member.id}`)"
            @keydown.enter="router.push(`/users/${member.id}`)"
          >
            <div class="member__avatar">
              <img v-if="member.avatar" :src="member.avatar" :alt="member.name" />
              <span v-else>{{ initials(member.name) }}</span>
            </div>
            <div class="member__info">
              <span class="member__name">{{ member.name }}</span>
              <span v-if="member.roles.length" class="member__roles">
                {{ member.roles.map((r) => r.name).join(' · ') }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <section v-if="eventResults.length" class="section">
        <h2 class="section__title">Мероприятия</h2>
        <div class="event-list">
          <div
            v-for="evt in eventResults"
            :key="evt.id"
            class="event-card"
            :class="statusClass(evt.status)"
            role="button"
            tabindex="0"
            @click="router.push(`/events/${evt.id}`)"
            @keydown.enter="router.push(`/events/${evt.id}`)"
          >
            <div class="event-card__cover">
              <img v-if="evt.cover" :src="evt.cover" :alt="evt.title" class="event-card__img" />
              <div v-else class="event-card__img event-card__img--placeholder" />
              <span v-if="ratingStatusLabel(evt.status)" class="event-card__badge">
                <svg viewBox="0 0 16 16" fill="currentColor" width="11" height="11">
                  <path d="M8 1l1.94 4.27L14.5 5.8l-3.25 3.17.77 4.49L8 11.27l-4.02 2.19.77-4.49L1.5 5.8l4.56-.53L8 1z" />
                </svg>
                {{ ratingStatusLabel(evt.status) }}
              </span>
              <span v-if="evt.isVerified" class="event-card__verify">
                <svg viewBox="0 0 20 20" fill="currentColor" width="11" height="11">
                  <path fill-rule="evenodd" d="M16.403 12.652a3 3 0 0 0 0-5.304 3 3 0 0 0-3.75-3.751 3 3 0 0 0-5.305 0 3 3 0 0 0-3.751 3.75 3 3 0 0 0 0 5.305 3 3 0 0 0 3.75 3.751 3 3 0 0 0 5.305 0 3 3 0 0 0 3.751-3.75Zm-2.546-4.46a.75.75 0 0 0-1.214-.883l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clip-rule="evenodd" />
                </svg>
              </span>
            </div>
            <div class="event-card__body">
              <h3 class="event-card__title">{{ evt.title }}</h3>
              <span class="event-card__date">{{ formatDateLong(evt.date) }}</span>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped lang="scss">
  .team-page {
    @include page-root;
  }

  .page-header {
    @include sticky-header;
  }

  .page-header__title {
    font-size: 16px;
    font-weight: 700;
  }

  .back-btn {
    @include back-button;
  }

  .hero {
    @include flex-column(10px);
    align-items: center;
    padding: 32px 16px 24px;
    border-bottom: 1px solid $color-border;
  }

  .hero__icon {
    width: 80px;
    height: 80px;
    border-radius: $radius-3xl;
    background: rgba($color-accent, 0.12);
    border: 1px solid rgba($color-accent, 0.3);
    @include flex-center;
    color: $color-accent;
  }

  .hero__name {
    margin: 4px 0 0;
    font-size: 24px;
    font-weight: 800;
    text-align: center;
  }

  .hero__description {
    margin: 0;
    font-size: 14px;
    color: $color-text-secondary;
    text-align: center;
    line-height: 1.5;
  }

  .hero__stats {
    display: flex;
    gap: 8px;
    margin-top: 8px;
  }

  .stat {
    @include flex-column(2px);
    align-items: center;
    padding: 10px 20px;
    border: 1px solid $color-border;
    border-radius: $radius-lg;
    min-width: 72px;

    &--accent .stat__value { color: $color-accent; }
  }

  .stat__value {
    font-size: 20px;
    font-weight: 800;
  }

  .stat__label {
    font-size: 11px;
    color: $color-text-secondary;
    white-space: nowrap;
  }

  .section {
    padding: 20px 16px;
    @include flex-column(12px);
    border-bottom: 1px solid $color-border;
  }

  .section__title {
    margin: 0;
    font-size: 17px;
    font-weight: 700;
  }

  .member-list {
    @include flex-column(8px);
  }

  .member {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-radius: $radius-lg;
    border: 1px solid $color-border;
    background: $color-surface;
    @include card-interactive;
  }

  .member__avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: #2a2a2a;
    @include flex-center;
    font-size: 14px;
    font-weight: 700;
    color: $color-text-secondary;
    flex-shrink: 0;
    overflow: hidden;

    img { width: 100%; height: 100%; object-fit: cover; }
  }

  .member__info {
    @include flex-column(2px);
    min-width: 0;
  }

  .member__name {
    font-size: 15px;
    font-weight: 600;
  }

  .member__roles {
    font-size: 12px;
    color: $color-text-secondary;
    @include text-ellipsis;
  }

  .event-list {
    @include flex-column(10px);
  }

  .event-card {
    border: 1px solid $color-border;
    border-radius: $radius-2xl;
    overflow: hidden;
    @include card-interactive;

    &--winner { border-color: $color-gold; }
    &--prize  { border-color: $color-silver; }
  }

  .event-card__cover {
    position: relative;
    height: 120px;
    background: #1e1e1e;
  }

  .event-card__img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;

    &--placeholder { background: #2a2a2a; }
  }

  .event-card__badge {
    position: absolute;
    top: 8px;
    right: 8px;
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 3px 9px;
    border-radius: $radius-full;
    background: rgba($color-gold, 0.9);
    font-size: 11px;
    font-weight: 700;
    color: #1a1400;
  }

  .event-card--prize .event-card__badge {
    background: rgba($color-silver, 0.9);
    color: #0d0f11;
  }

  .event-card__verify {
    position: absolute;
    top: 8px;
    left: 8px;
    @include flex-center;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: rgba($color-bg, 0.8);
    backdrop-filter: blur(6px);
    color: $color-success;
  }

  .event-card__body {
    padding: 10px 14px 12px;
    @include flex-between;
    align-items: baseline;
    gap: 8px;
  }

  .event-card__title {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
    flex: 1;
    min-width: 0;
    @include text-ellipsis;
  }

  .event-card__date {
    font-size: 12px;
    color: $color-text-secondary;
    flex-shrink: 0;
  }

  .hero-skeleton {
    @include flex-column(12px);
    align-items: center;
    padding: 32px 16px 24px;
  }

  .skel-stats {
    display: flex;
    gap: 8px;
    margin-top: 4px;
  }

  .skel {
    border-radius: $radius-sm;
    @include skeleton-shimmer;

    &--icon  { width: 80px; height: 80px; border-radius: $radius-3xl; }
    &--title { height: 28px; width: 160px; }
    &--line  { height: 14px; width: 220px; }
    &--stat  { height: 58px; width: 80px; border-radius: $radius-lg; }
  }

  .state-empty {
    padding: 48px 16px;
    text-align: center;
    color: $color-text-secondary;
    font-size: 14px;
  }
</style>
