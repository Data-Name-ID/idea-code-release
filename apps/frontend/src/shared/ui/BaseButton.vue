<script setup lang="ts">
  import { computed, useAttrs } from 'vue'

  type ButtonVariant = 'primary' | 'ghost' | 'danger'
  type ButtonSize = 'sm' | 'md'

  const props = withDefaults(
    defineProps<{
      variant?: ButtonVariant
      size?: ButtonSize
      block?: boolean
      loading?: boolean
      type?: 'button' | 'submit' | 'reset'
    }>(),
    {
      variant: 'primary',
      size: 'md',
      block: false,
      loading: false,
      type: 'button',
    },
  )

  const attrs = useAttrs()
  const isDisabled = computed(() => Boolean(props.loading || attrs.disabled))
</script>

<template>
  <button
    v-bind="attrs"
    :type="props.type"
    class="base-button"
    :class="[
      `base-button--${props.variant}`,
      `base-button--${props.size}`,
      { 'base-button--block': props.block },
    ]"
    :disabled="isDisabled"
  >
    <span v-if="props.loading" class="base-button__spinner" aria-hidden="true" />
    <slot />
  </button>
</template>

<style scoped lang="scss">
  .base-button {
    @include button-base;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;

    &--md {
      min-height: 36px;
      padding: 8px 12px;
    }

    &--sm {
      min-height: 32px;
      padding: 6px 10px;
      font-size: 13px;
    }

    &--primary {
      background: $color-accent;
      color: $color-text-inverse;

      &:hover:not(:disabled) {
        background: color-mix(in srgb, $color-accent 90%, white 10%);
      }
    }

    &--ghost {
      background: transparent;
      border-color: $color-border;
      color: $color-text-primary;

      &:hover:not(:disabled) {
        border-color: $color-accent-border;
        color: $color-accent;
        background: $color-accent-soft;
      }
    }

    &--danger {
      background: $color-danger;
      color: $color-text-primary;

      &:hover:not(:disabled) {
        background: color-mix(in srgb, $color-danger 90%, white 10%);
      }
    }

    &--block {
      width: 100%;
    }
  }

  .base-button__spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.22);
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
