<script setup lang="ts">
  defineOptions({ inheritAttrs: false })

  const model = defineModel<string | null | undefined>({ default: '' })

  withDefaults(
    defineProps<{
      rows?: number
      placeholder?: string
      disabled?: boolean
      name?: string
    }>(),
    {
      rows: 3,
      placeholder: '',
      disabled: false,
      name: undefined,
    },
  )
</script>

<template>
  <textarea
    v-model="model"
    class="base-field base-field--textarea"
    :rows="rows"
    :placeholder="placeholder"
    :disabled="disabled"
    :name="name"
    v-bind="$attrs"
  />
</template>

<style scoped lang="scss">
  .base-field {
    width: 100%;
    @include field-control;

    &--textarea {
      resize: vertical;
      min-height: 96px;
    }
  }
</style>
