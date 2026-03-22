<script setup lang="ts">
  import { computed, onUnmounted, watch } from 'vue'

  const props = withDefaults(
    defineProps<{
      modelValue: boolean
      title?: string
    }>(),
    {
      title: 'Фильтры',
    },
  )

  const emit = defineEmits<{
    'update:modelValue': [value: boolean]
  }>()

  const isOpen = computed(() => props.modelValue)

  function close(): void {
    emit('update:modelValue', false)
  }

  watch(
    isOpen,
    (value) => {
      document.body.style.overflow = value ? 'hidden' : ''
    },
    { immediate: true },
  )

  onUnmounted(() => {
    document.body.style.overflow = ''
  })
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="filter-layer" @click.self="close">
      <aside class="filter-panel" role="dialog" aria-modal="true" :aria-label="title">
        <header class="filter-panel__header">
          <h2>{{ title }}</h2>
          <button type="button" class="filter-panel__close" aria-label="Закрыть фильтры" @click="close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
              <path stroke-linecap="round" stroke-linejoin="round" d="m6 6 12 12M18 6 6 18" />
            </svg>
          </button>
        </header>

        <div class="filter-panel__content">
          <slot />
        </div>
      </aside>
    </div>
  </Teleport>
</template>

<style scoped lang="scss">
  .filter-layer {
    position: fixed;
    inset: 0;
    z-index: 260;
    background: rgba($color-bg, 0.6);
    backdrop-filter: blur(3px);
  }

  .filter-panel {
    position: fixed;
    inset: 0;
    background: $color-bg;
    border: 1px solid $color-border;
    display: flex;
    flex-direction: column;
    animation: panel-in-mobile $transition-normal;

    @include respond-to('lg') {
      inset: 0 0 0 auto;
      width: min(420px, 92vw);
      border-left: 1px solid $color-border;
      border-top: none;
      border-right: none;
      border-bottom: none;
      border-radius: 20px 0 0 20px;
      background: $color-bg-elevated;
      box-shadow: -16px 0 36px rgba(0, 0, 0, 0.34);
      animation: panel-in-desktop $transition-normal;
    }
  }

  .filter-panel__header {
    @include flex-between;
    padding: $space-4;
    border-bottom: 1px solid $color-border;

    h2 {
      margin: 0;
      font-size: 18px;
      font-weight: 700;
    }
  }

  .filter-panel__close {
    @include back-button;
  }

  .filter-panel__content {
    overflow: auto;
    padding: $space-4;
    display: grid;
    gap: $space-4;
  }

  @keyframes panel-in-mobile {
    from {
      transform: translateY(14px);
      opacity: 0;
    }

    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  @keyframes panel-in-desktop {
    from {
      transform: translateX(18px);
      opacity: 0;
    }

    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
</style>
