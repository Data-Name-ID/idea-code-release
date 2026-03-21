<script setup lang="ts">
  import { ref, onMounted } from 'vue'
  import { api } from '@shared/api'

  type HealthStatus = 'idle' | 'loading' | 'ok' | 'error'

  const status = ref<HealthStatus>('idle')
  const data = ref<Record<string, unknown> | null>(null)
  const error = ref<string | null>(null)

  async function checkHealth() {
    status.value = 'loading'
    data.value = null
    error.value = null
    try {
      const res = await api.get<Record<string, unknown>>('/health')
      data.value = res.data
      status.value = 'ok'
    } catch (e) {
      status.value = 'error'
      error.value = e instanceof Error ? e.message : 'Unknown error'
    }
  }

  onMounted(checkHealth)
</script>

<template>
  <section class="home">
    <h2>Frontend Bootstrapped</h2>

    <div class="health">
      <span class="health__label">Backend /health</span>
      <span class="health__badge" :class="`health__badge--${status}`">
        <span class="health__dot" />
        {{ status === 'loading' ? 'checking…' : status }}
      </span>
      <button class="health__retry" @click="checkHealth">Retry</button>
    </div>

    <pre v-if="data" class="health__response">{{ JSON.stringify(data, null, 2) }}</pre>
    <p v-if="status === 'error'" class="health__error">{{ error }}</p>
  </section>
</template>

<style lang="scss" scoped>
  .home {
    max-width: 720px;
    display: grid;
    gap: $spacing-4;
  }

  h2 {
    margin: 0;
  }

  .health {
    @include flex-between;
    gap: $spacing-3;
    padding: $spacing-4;
    border: $border-width solid $color-border;
    border-radius: $border-radius-lg;
    background: $color-surface;
    flex-wrap: wrap;

    &__label {
      font-weight: $font-weight-medium;
      font-size: $font-size-sm;
      color: $color-text-muted;
      font-family: monospace;
    }

    &__badge {
      @include flex-center;
      gap: $spacing-2;
      padding: $spacing-1 $spacing-3;
      border-radius: $border-radius-full;
      font-size: $font-size-sm;
      font-weight: $font-weight-medium;
      text-transform: uppercase;
      letter-spacing: 0.05em;

      &--idle {
        background: #f1f5f9;
        color: #64748b;
      }

      &--loading {
        background: #fefce8;
        color: #a16207;
      }

      &--ok {
        background: #dcfce7;
        color: #15803d;
      }

      &--error {
        background: #fee2e2;
        color: #b91c1c;
      }
    }

    &__dot {
      width: 8px;
      height: 8px;
      border-radius: $border-radius-full;
      background: currentColor;
      flex-shrink: 0;

      .health__badge--loading & {
        animation: pulse 1s ease-in-out infinite;
      }
    }

    &__retry {
      margin-left: auto;
      padding: $spacing-1 $spacing-3;
      border: $border-width solid $color-border;
      border-radius: $border-radius-md;
      background: transparent;
      font-size: $font-size-sm;
      cursor: pointer;
      @include transition(background, border-color);

      &:hover {
        background: $color-border;
      }
    }
  }

  .health__response {
    margin: 0;
    padding: $spacing-3 $spacing-4;
    border: $border-width solid $color-border;
    border-radius: $border-radius-md;
    background: $color-surface;
    font-size: $font-size-sm;
    line-height: $line-height-relaxed;
  }

  .health__error {
    font-size: $font-size-sm;
    color: $color-danger;
    font-family: monospace;
    margin: 0;
  }

  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.3;
    }
  }
</style>
