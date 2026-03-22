<script setup lang="ts">
  type CardVariant = 'default' | 'muted' | 'accent'

  withDefaults(
    defineProps<{
      variant?: CardVariant
      interactive?: boolean
      padded?: boolean
    }>(),
    {
      variant: 'default',
      interactive: false,
      padded: true,
    },
  )
</script>

<template>
  <section class="base-card" :class="[`base-card--${variant}`, { 'base-card--interactive': interactive, 'base-card--padded': padded }]">
    <slot />
  </section>
</template>

<style scoped lang="scss">
  .base-card {
    border-radius: $radius-2xl;
    border: 1px solid $color-border;
    background: $color-bg-elevated;

    &--muted {
      background: $color-bg-muted;
    }

    &--accent {
      background: $color-bg-muted;
      border-color: rgba($color-accent, 0.2);
    }

    &--padded {
      padding: $space-5;
    }

    &--interactive {
      @include card-interactive;
    }
  }
</style>
