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
    name: 'home',
    component: () => import('@pages/home/ui/HomePage.vue'),
    meta: {
      requiresAuth: true,
    },
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
