<script setup lang="ts">
  defineOptions({ inheritAttrs: false })

  const model = defineModel<string | number | undefined>({ default: undefined })

  withDefaults(
    defineProps<{
      disabled?: boolean
      name?: string
    }>(),
    {
      disabled: false,
      name: undefined,
    },
  )
</script>

<template>
  <select v-model="model" class="base-field" :disabled="disabled" :name="name" v-bind="$attrs">
    <slot />
  </select>
</template>

<style scoped lang="scss">
  .base-field {
    width: 100%;
    @include field-control;
    min-height: 40px;
    appearance: none;
    background-image:
      linear-gradient(45deg, transparent 50%, $color-text-secondary 50%),
      linear-gradient(135deg, $color-text-secondary 50%, transparent 50%);
    background-position:
      calc(100% - 16px) calc(50% - 2px),
      calc(100% - 11px) calc(50% - 2px);
    background-size: 5px 5px, 5px 5px;
    background-repeat: no-repeat;
    padding-right: 34px;
  }
</style>
