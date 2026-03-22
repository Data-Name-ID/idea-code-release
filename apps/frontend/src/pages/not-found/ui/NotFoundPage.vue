<template>
  <div class="not-found">
    <h2>404 — Страница не найдена</h2>
    <RouterLink to="/profile">Вернуться в профиль</RouterLink>
  </div>
</template>

<style scoped lang="scss">
  .not-found {
    @include page-root;
    @include flex-center;
    flex-direction: column;
    gap: 16px;

    h2 {
      margin: 0;
      font-size: 22px;
      font-weight: 700;
    }

    a {
      color: $color-accent;
      font-size: 14px;
      text-decoration: none;

      &:hover { text-decoration: underline; }
    }
  }
</style>
