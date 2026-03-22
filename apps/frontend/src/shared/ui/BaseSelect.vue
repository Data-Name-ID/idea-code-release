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
  }
</style>
