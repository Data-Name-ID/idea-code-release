<script setup lang="ts">
  type StatusTone = 'info' | 'error' | 'success'

  withDefaults(
    defineProps<{
      tone?: StatusTone
    }>(),
    {
      tone: 'info',
    },
  )
</script>

<template>
  <p class="base-status" :class="`base-status--${tone}`">
    <slot />
  </p>
</template>

<style scoped lang="scss">
  .base-status {
    @include state-message('info');

    &--error {
      @include state-message('error');
    }

    &--success {
      @include state-message('success');
    }
  }
</style>
