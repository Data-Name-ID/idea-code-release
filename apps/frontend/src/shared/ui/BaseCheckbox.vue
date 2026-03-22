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

    input {
      width: 16px;
      height: 16px;
      accent-color: $color-accent;
    }
  }
</style>
