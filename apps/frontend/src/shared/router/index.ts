import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import { authState, ensureSessionInitialized } from '@shared/auth/session'

const routes: RouteRecordRaw[] = [
  {
    path: '/auth',
    name: 'auth',
    component: () => import('@pages/auth/ui/AuthPage.vue'),
    meta: {
      guestOnly: true,
    },
  },
  {
    path: '/',
    redirect: '/profile',
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@pages/profile/ui/ProfilePage.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/profile/edit',
    name: 'profile-edit',
    component: () => import('@pages/profile-edit/ui/ProfileEditPage.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/users/:id',
    name: 'user',
    component: () => import('@pages/user/ui/UserPage.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/teams/:id',
    name: 'team',
    component: () => import('@pages/team/ui/TeamPage.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/events/:id',
    name: 'event',
    component: () => import('@pages/event/ui/EventPage.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/teammates',
    name: 'teammates',
    component: () => import('@pages/teammates/ui/TeammatesPage.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/applications',
    name: 'applications',
    component: () => import('@pages/applications/ui/ApplicationsPage.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/organizer/import',
    name: 'organizer-import',
    component: () => import('@pages/organizer-import/ui/OrganizerImportPage.vue'),
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@pages/not-found/ui/NotFoundPage.vue'),
    meta: {
      requiresAuth: true,
    },
  },
]

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to) => {
  await ensureSessionInitialized()

  const isAuthenticated = authState.isAuthenticated.value
  const requiresAuth = to.meta.requiresAuth === true
  const guestOnly = to.meta.guestOnly === true

  if (requiresAuth && !isAuthenticated) {
    return { name: 'auth' }
  }

  if (guestOnly && isAuthenticated) {
    return { name: 'profile' }
  }

  return true
})
