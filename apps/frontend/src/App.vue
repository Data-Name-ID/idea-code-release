<template>
  <div class="layout">
    <header class="header">
      <h1>Team Monorepo</h1>
      <nav>
        <RouterLink to="/">
          Home
        </RouterLink>
      </nav>
    </header>

    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100dvh;
  display: grid;
  grid-template-rows: auto 1fr;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.header h1 {
  margin: 0;
  font-size: 1.1rem;
}

.content {
  padding: 1.5rem;
}
</style>
