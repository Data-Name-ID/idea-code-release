<script setup lang="ts">
  import { computed } from 'vue'
  import type { UserResponse, LinkType } from '@shared/types/api'

  const props = defineProps<{
    user: UserResponse
    hackathonCount?: number | null
    winCount?: number | null
    rank?: number | null
  }>()

  const displayRoles = computed(() => props.user.roles.map((r) => r.name).join(' · '))

  const socialLinks = computed(() =>
    props.user.links.filter((l) =>
      (['github', 'gitlab', 'telegram', 'twitter', 'instagram'] as LinkType[]).includes(l.type),
    ),
  )

  const hasStats = computed(
    () =>
      props.hackathonCount != null || props.winCount != null || props.rank != null,
  )

  const hasContacts = computed(
    () => props.user.email || props.user.location,
  )

  function getIconPath(type: LinkType): string {
    const icons: Record<string, string> = {
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
    }
    return icons[type] ?? ''
  }
</script>

<template>
  <div class="card">
    <!-- Avatar -->
    <div class="avatar-wrap">
      <img v-if="user.avatar" :src="user.avatar" :alt="user.name" class="avatar" />
      <div v-else class="avatar avatar--placeholder" />
    </div>

    <!-- Name & roles -->
    <h1 class="name">{{ user.name }}</h1>
    <p v-if="displayRoles" class="roles">{{ displayRoles }}</p>

    <!-- Description -->
    <p v-if="user.description" class="description">{{ user.description }}</p>

    <!-- Stats -->
    <div v-if="hasStats" class="stats">
      <div v-if="hackathonCount != null" class="stat">
        <span class="stat__value">{{ hackathonCount }}</span>
        <span class="stat__label">Хакатоны</span>
      </div>
      <div v-if="winCount != null" class="stat">
        <span class="stat__value">{{ winCount }}</span>
        <span class="stat__label">Победы</span>
      </div>
      <div v-if="rank != null" class="stat stat--accent">
        <span class="stat__value">{{ rank }}ST</span>
        <span class="stat__label">Рейтинг</span>
      </div>
    </div>

    <!-- Social links -->
    <div v-if="socialLinks.length" class="socials">
      <a
        v-for="link in socialLinks"
        :key="link.url"
        :href="link.url"
        :aria-label="link.label"
        target="_blank"
        rel="noopener noreferrer"
        class="social-btn"
      >
        <svg
          viewBox="0 0 24 24"
          fill="currentColor"
          width="18"
          height="18"
          aria-hidden="true"
        >
          <path :d="getIconPath(link.type)" />
        </svg>
      </a>
    </div>

    <!-- Contacts -->
    <div v-if="hasContacts" class="contacts">
      <p class="contacts__label">КОНТАКТЫ</p>
      <div v-if="user.email" class="contact-row">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
        </svg>
        <span>{{ user.email }}</span>
      </div>
      <div v-if="user.location" class="contact-row">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z" />
        </svg>
        <span>{{ user.location }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
  .card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 24px 16px 28px;
  }

  .avatar-wrap {
    width: 88px;
    height: 88px;
    border-radius: 50%;
    border: 2.5px solid var(--p-accent);
    padding: 3px;
    flex-shrink: 0;
  }

  .avatar {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
    display: block;

    &--placeholder {
      background: #2a2a2a;
    }
  }

  .name {
    margin: 4px 0 0;
    font-size: 22px;
    font-weight: 700;
    color: var(--p-text-primary);
    text-align: center;
  }

  .roles {
    margin: 0;
    font-size: 14px;
    color: var(--p-text-secondary);
    text-align: center;
  }

  .description {
    margin: 0;
    font-size: 14px;
    color: var(--p-text-secondary);
    text-align: center;
    line-height: 1.5;
  }

  .stats {
    display: flex;
    gap: 8px;
    margin-top: 4px;
  }

  .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: 10px 16px;
    border: 1px solid var(--p-border);
    border-radius: 12px;
    min-width: 72px;

    &--accent &__value {
      color: var(--p-accent);
      font-weight: 800;
    }
  }

  .stat__value {
    font-size: 18px;
    font-weight: 700;
    color: var(--p-text-primary);
  }

  .stat__label {
    font-size: 11px;
    color: var(--p-text-secondary);
  }

  .socials {
    display: flex;
    gap: 8px;
    margin-top: 4px;
  }

  .social-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border: 1px solid var(--p-border);
    border-radius: 10px;
    color: var(--p-text-secondary);
    text-decoration: none;
    transition: color 150ms, border-color 150ms;

    &:hover {
      color: var(--p-text-primary);
      border-color: var(--p-accent);
      text-decoration: none;
    }
  }

  .contacts {
    width: 100%;
    padding-top: 20px;
    border-top: 1px solid var(--p-border);
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 4px;
  }

  .contacts__label {
    margin: 0 0 4px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: var(--p-text-secondary);
  }

  .contact-row {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--p-text-primary);
    font-size: 14px;

    svg {
      flex-shrink: 0;
      color: var(--p-text-secondary);
    }
  }
</style>
