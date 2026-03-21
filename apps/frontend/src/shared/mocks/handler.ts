import type { UserResponse, UserUpdateRequest, LinkType } from '@shared/types/api'
import {
  MOCK_ROLES,
  MOCK_SKILLS,
  MOCK_USERS,
  MOCK_USERS_LIST,
  MOCK_EVENTS,
  MOCK_EVENTS_LIST,
  MOCK_RATINGS,
  MOCK_TEAMS,
  MOCK_TEAMS_LIST,
} from './data'

// Mutable store so PUT changes are reflected within the session
const users: UserResponse[] = MOCK_USERS.map((u) => ({ ...u }))

function inferLinkType(url: string): LinkType {
  if (url.includes('github.com')) return 'github'
  if (url.includes('gitlab.com')) return 'gitlab'
  if (url.includes('t.me') || url.includes('telegram')) return 'telegram'
  if (url.includes('twitter.com') || url.includes('x.com')) return 'twitter'
  if (url.includes('instagram.com')) return 'instagram'
  return 'other'
}

export function resolveMock<T>(path: string, options?: RequestInit): T {
  const [pathname, search] = path.split('?')
  const method = (options?.method ?? 'GET').toUpperCase()
  const params = new URLSearchParams(search ?? '')

  // GET /api/roles/
  if (/^\/api\/roles\/?$/.test(pathname)) {
    return MOCK_ROLES as T
  }

  // GET /api/skills/
  if (/^\/api\/skills\/?$/.test(pathname)) {
    return MOCK_SKILLS as T
  }

  // GET /api/users/
  if (/^\/api\/users\/?$/.test(pathname) && method === 'GET') {
    const search = params.get('search')?.toLowerCase()
    const roleId = params.get('role_id') ? Number(params.get('role_id')) : null
    const skillId = params.get('skill_id') ? Number(params.get('skill_id')) : null
    const limit = params.get('limit') ? Number(params.get('limit')) : 20
    const offset = params.get('offset') ? Number(params.get('offset')) : 0

    let data = MOCK_USERS_LIST.data
    if (search) data = data.filter((u) => u.name.toLowerCase().includes(search) || u.username.toLowerCase().includes(search))
    if (roleId) data = data.filter((u) => u.roles.some((r) => r.id === roleId))
    if (skillId) data = data.filter((u) => u.skills.some((s) => s.id === skillId))

    return { total: data.length, limit, offset, data: data.slice(offset, offset + limit) } as T
  }

  // POST /api/users/
  if (/^\/api\/users\/?$/.test(pathname) && method === 'POST') {
    const body = JSON.parse(options?.body as string ?? '{}')
    const newUser: UserResponse = {
      id: users.length + 1,
      username: body.username ?? 'new_user',
      email: body.email ?? null,
      name: body.name ?? 'New User',
      avatar: body.avatar ?? null,
      description: body.description ?? '',
      location: body.location ?? '',
      links: (body.links ?? []).map((l: { url: string; label: string }) => ({ ...l, type: inferLinkType(l.url) })),
      roles: (body.role_ids ?? []).flatMap((id: number) => { const r = MOCK_ROLES.find((r) => r.id === id); return r ? [r] : [] }),
      skills: (body.skill_ids ?? []).flatMap((id: number) => { const s = MOCK_SKILLS.find((s) => s.id === id); return s ? [s] : [] }),
    }
    users.push(newUser)
    return newUser as T
  }

  // /api/users/:id
  const userMatch = pathname.match(/^\/api\/users\/(\d+)\/?$/)
  if (userMatch) {
    const id = parseInt(userMatch[1])

    if (method === 'GET') {
      return (users.find((u) => u.id === id) ?? users[0]) as T
    }

    if (method === 'PUT') {
      const body = JSON.parse(options?.body as string ?? '{}') as UserUpdateRequest
      const idx = users.findIndex((u) => u.id === id)
      const base = users[idx] ?? users[0]
      const updated: UserResponse = {
        ...base,
        name: body.name !== undefined ? (body.name ?? base.name) : base.name,
        email: body.email !== undefined ? body.email : base.email,
        avatar: body.avatar !== undefined ? body.avatar : base.avatar,
        location: body.location !== undefined ? (body.location ?? '') : base.location,
        description: body.description !== undefined ? (body.description ?? '') : base.description,
        links: body.links !== undefined
          ? (body.links ?? []).map((l) => ({ ...l, type: inferLinkType(l.url) }))
          : base.links,
        roles: body.role_ids !== undefined
          ? (body.role_ids ?? []).flatMap((rid) => { const r = MOCK_ROLES.find((r) => r.id === rid); return r ? [r] : [] })
          : base.roles,
        skills: body.skill_ids !== undefined
          ? (body.skill_ids ?? []).flatMap((sid) => { const s = MOCK_SKILLS.find((s) => s.id === sid); return s ? [s] : [] })
          : base.skills,
      }
      if (idx !== -1) users[idx] = updated
      return updated as T
    }

    if (method === 'DELETE') {
      return undefined as T
    }
  }

  // GET /api/events/
  if (/^\/api\/events\/?$/.test(pathname) && method === 'GET') {
    const limit = params.get('limit') ? Number(params.get('limit')) : 20
    const offset = params.get('offset') ? Number(params.get('offset')) : 0
    return { ...MOCK_EVENTS_LIST, limit, offset, data: MOCK_EVENTS.slice(offset, offset + limit) } as T
  }

  // GET /api/events/:id/ratings
  const ratingsMatch = pathname.match(/^\/api\/events\/(\d+)\/ratings\/?$/)
  if (ratingsMatch) {
    const eventId = parseInt(ratingsMatch[1])
    const status = params.get('status')
    const base = MOCK_RATINGS[eventId] ?? { event_id: eventId, ratings: [] }
    const ratings = status ? base.ratings.filter((r) => r.status === status) : base.ratings
    return { ...base, ratings } as T
  }

  // GET /api/events/:id
  const eventMatch = pathname.match(/^\/api\/events\/(\d+)\/?$/)
  if (eventMatch && method === 'GET') {
    const id = parseInt(eventMatch[1])
    return (MOCK_EVENTS.find((e) => e.id === id) ?? MOCK_EVENTS[0]) as T
  }

  // GET /api/teams/
  if (/^\/api\/teams\/?$/.test(pathname) && method === 'GET') {
    const userId = params.get('user_id') ? Number(params.get('user_id')) : null
    const search = params.get('search')?.toLowerCase()
    const eventId = params.get('event_id') ? Number(params.get('event_id')) : null
    const limit = params.get('limit') ? Number(params.get('limit')) : 20
    const offset = params.get('offset') ? Number(params.get('offset')) : 0

    let data = MOCK_TEAMS_LIST.data
    if (userId) data = data.filter((t) => MOCK_TEAMS.find((mt) => mt.id === t.id)?.users.some((u) => u.id === userId))
    if (search) data = data.filter((t) => t.name.toLowerCase().includes(search))
    if (eventId) data = data.filter((t) => MOCK_TEAMS.find((mt) => mt.id === t.id)?.events.some((e) => e.id === eventId))

    return { total: data.length, limit, offset, data: data.slice(offset, offset + limit) } as T
  }

  // GET /api/teams/:id
  const teamMatch = pathname.match(/^\/api\/teams\/(\d+)\/?$/)
  if (teamMatch && method === 'GET') {
    const id = parseInt(teamMatch[1])
    return (MOCK_TEAMS.find((t) => t.id === id) ?? MOCK_TEAMS[0]) as T
  }

  throw new Error(`[Mock] Unhandled: ${method} ${pathname}`)
}
