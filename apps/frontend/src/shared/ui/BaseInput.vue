<script setup lang="ts">
  defineOptions({ inheritAttrs: false })

  const model = defineModel<string | number | null | undefined>({ default: '' })

  withDefaults(
    defineProps<{
      type?: string
      placeholder?: string
      disabled?: boolean
      required?: boolean
      name?: string
      autocomplete?: string
    }>(),
    {
      type: 'text',
      placeholder: '',
      disabled: false,
      required: false,
      name: undefined,
      autocomplete: undefined,
    },
  )
</script>

<template>
  <input
    v-model="model"
    class="base-field"
    :type="type"
    :placeholder="placeholder"
    :disabled="disabled"
    :required="required"
    :name="name"
    :autocomplete="autocomplete"
    v-bind="$attrs"
  />
</template>

<style scoped lang="scss">
  .base-field {
    width: 100%;
    @include field-control;
    min-height: 40px;
  }
</style>
