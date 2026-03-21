<script setup lang="ts">
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
</script>

<template>
  <section class="home">
    <h2>Frontend Bootstrapped</h2>
    <p>
      API base URL:
      <code>{{ apiBaseUrl }}</code>
    </p>
  </section>
</template>

<style scoped>
.home {
  max-width: 720px;
  display: grid;
  gap: 0.75rem;
}

h2 {
  margin: 0;
}

code {
  padding: 0.125rem 0.375rem;
  border-radius: 0.375rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}
</style>
