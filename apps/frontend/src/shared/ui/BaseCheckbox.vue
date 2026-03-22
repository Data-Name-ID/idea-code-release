<script setup lang="ts">
  const model = defineModel<boolean>({ default: false })

  withDefaults(
    defineProps<{
      disabled?: boolean
    }>(),
    {
      disabled: false,
    },
  )
</script>

<template>
  <label class="base-checkbox">
    <input v-model="model" type="checkbox" :disabled="disabled" />
    <span class="base-checkbox__label">
      <slot />
    </span>
  </label>
</template>

<style scoped lang="scss">
  .base-checkbox {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: $color-text-secondary;
    font-size: 14px;
    cursor: pointer;

    input {
      appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 5px;
      border: 1px solid $color-border-strong;
      background: $color-surface;
      display: grid;
      place-items: center;
      margin: 0;
      transition: border-color $transition-fast, background-color $transition-fast;

      &::after {
        content: '';
        width: 8px;
        height: 8px;
        border-radius: 2px;
        background: $color-text-inverse;
        opacity: 0;
        transform: scale(0.5);
        transition: opacity $transition-fast, transform $transition-fast;
      }

      &:checked {
        border-color: $color-accent-border;
        background: $color-accent;
      }

      &:checked::after {
        opacity: 1;
        transform: scale(1);
      }

      &:focus-visible {
        outline: none;
        box-shadow: 0 0 0 1px $color-accent-border;
      }
    }
  }
</style>
