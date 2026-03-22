<script setup lang="ts">
  withDefaults(
    defineProps<{
      title?: string
      sticky?: boolean
    }>(),
    {
      title: '',
      sticky: true,
    },
  )

  const emit = defineEmits<{
    back: []
  }>()
</script>

<template>
  <header class="base-top-bar" :class="{ 'base-top-bar--sticky': sticky }">
    <button type="button" class="base-top-bar__back" @click="emit('back')">
      <slot name="back-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
      </slot>
    </button>

    <span class="base-top-bar__title">{{ title }}</span>

    <div class="base-top-bar__actions">
      <slot name="actions">
        <div class="base-top-bar__spacer" />
      </slot>
    </div>
  </header>
</template>

<style scoped lang="scss">
  .base-top-bar {
    @include flex-between;
    padding: 12px 16px;
    border-bottom: 1px solid $color-border;

    &--sticky {
      position: sticky;
      top: 0;
      z-index: $z-sticky;
      background: rgba($color-bg, 0.9);
      backdrop-filter: blur(12px);
    }
  }

  .base-top-bar__title {
    font-size: 16px;
    font-weight: 700;
  }

  .base-top-bar__back {
    @include back-button;
  }

  .base-top-bar__actions,
  .base-top-bar__spacer {
    width: 36px;
    display: flex;
    justify-content: flex-end;
  }
</style>
