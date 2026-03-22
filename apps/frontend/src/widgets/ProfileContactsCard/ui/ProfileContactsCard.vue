<script setup lang="ts">
  import { computed } from 'vue'

  import type { LinkResponse, LinkType } from '@shared/types/api'

  const props = withDefaults(
    defineProps<{
      title?: string
      email?: string | null
      location?: string | null
      links?: LinkResponse[]
      emptyText?: string
    }>(),
    {
      title: 'Контакты и ссылки',
      email: null,
      location: null,
      links: () => [],
      emptyText: 'Контактные данные не заполнены',
    },
  )

  const hasData = computed(
    () => Boolean(props.email) || Boolean(props.location) || props.links.length > 0,
  )

  const SOCIAL_ICONS: Record<LinkType, string> = {
    github:
      'M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.341-3.369-1.341-.454-1.155-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0 1 12 6.836a9.59 9.59 0 0 1 2.504.337c1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z',
    gitlab:
      'M22.65 14.39L12 22.13 1.35 14.39a.84.84 0 0 1-.3-.94l1.22-3.78 2.44-7.51A.42.42 0 0 1 4.82 2a.43.43 0 0 1 .58 0 .42.42 0 0 1 .11.18l2.44 7.49h8.1l2.44-7.51A.42.42 0 0 1 18.6 2a.43.43 0 0 1 .58 0 .42.42 0 0 1 .11.18l2.44 7.51 1.22 3.78a.84.84 0 0 1-.3.92z',
    telegram:
      'M9.78 18.65l.28-4.23 7.68-6.92c.34-.31-.07-.46-.52-.19L7.74 13.3 3.64 12c-.88-.25-.89-.86.2-1.3l15.97-6.16c.73-.33 1.43.18 1.15 1.3l-2.72 12.81c-.19.91-.74 1.13-1.5.71L12.6 16.3l-1.99 1.93c-.23.23-.42.42-.83.42z',
    twitter:
      'M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.747l7.73-8.835L1.254 2.25H8.08l4.259 5.629L18.244 2.25zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77z',
    instagram:
      'M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z',
    other:
      'M10 18a8 8 0 100-16 8 8 0 000 16zM4.332 8.027a6.012 6.012 0 011.912-2.706C6.512 5.73 6.974 6 7.5 6A1.5 1.5 0 019 7.5V8a2 2 0 004 0 2 2 0 011.523-1.943A5.977 5.977 0 0116 10c0 .34-.028.675-.083 1H15a2 2 0 00-2 2v2.197A5.973 5.973 0 0110 16v-2a2 2 0 00-2-2 2 2 0 01-2-2 2 2 0 00-1.668-1.973z',
  }

  function getIconPath(type: LinkType): string {
    return SOCIAL_ICONS[type] ?? SOCIAL_ICONS.other
  }
</script>

<template>
  <section class="contacts-card">
    <header class="contacts-card__header">
      <h3 class="contacts-card__title">{{ title }}</h3>
    </header>

    <div v-if="hasData" class="contacts-card__body">
      <div v-if="email" class="contact-row">
        <span class="contact-row__label">Email</span>
        <span class="contact-row__value">{{ email }}</span>
      </div>
      <div v-if="location" class="contact-row">
        <span class="contact-row__label">Локация</span>
        <span class="contact-row__value">{{ location }}</span>
      </div>

      <div v-if="links.length" class="links">
        <a
          v-for="link in links"
          :key="link.url"
          :href="link.url"
          :aria-label="link.label"
          target="_blank"
          rel="noopener noreferrer"
          class="link-pill"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14" aria-hidden="true">
            <path :d="getIconPath(link.type)" />
          </svg>
          <span>{{ link.label }}</span>
        </a>
      </div>
    </div>

    <div v-else class="empty">
      <p>{{ emptyText }}</p>
    </div>
  </section>
</template>

<style scoped lang="scss">
  .contacts-card {
    @include flex-column(12px);
  }

  .contacts-card__title {
    margin: 0;
    font-size: 17px;
    font-weight: 700;
  }

  .contacts-card__body {
    @include flex-column(10px);
  }

  .contact-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    border: 1px solid $color-border;
    border-radius: $radius-lg;
    padding: 10px 12px;
  }

  .contact-row__label {
    font-size: 12px;
    color: $color-text-secondary;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .contact-row__value {
    font-size: 14px;
    font-weight: 500;
    text-align: right;
  }

  .links {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .link-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: 1px solid $color-border;
    border-radius: $radius-full;
    color: $color-text-primary;
    text-decoration: none;
    padding: 6px 10px;
    font-size: 13px;
    transition: border-color $transition-fast, color $transition-fast;

    &:hover {
      border-color: $color-accent;
      color: $color-accent;
      text-decoration: none;
    }
  }

  .empty {
    padding: 12px 0;
    color: $color-text-secondary;
    font-size: 14px;
  }
</style>
