import type {
  ApplicationStatus,
  LinkType,
  OrganizerImportRequest,
  OrganizerImportResponse,
  ParticipationApplicationResponse,
  PreferredTeamFormat,
  UserResponse,
  UserUpdateRequest,
} from '@shared/types/api'
import {
  MOCK_ROLES,
  MOCK_SKILLS,
  MOCK_USERS,
  MOCK_EVENTS,
  MOCK_EVENTS_LIST,
  MOCK_RATINGS,
  MOCK_TEAMS,
  MOCK_TEAMS_LIST,
} from './data'

// Mutable store so PUT changes are reflected within the session
const users: UserResponse[] = MOCK_USERS.map((u) => ({ ...u }))
const applications: ParticipationApplicationResponse[] = []

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
    const location = params.get('location')?.toLowerCase()
    const roleId = params.get('role_id') ? Number(params.get('role_id')) : null
    const skillId = params.get('skill_id') ? Number(params.get('skill_id')) : null
    const openToTeamup = params.get('open_to_teamup')
    const limit = params.get('limit') ? Number(params.get('limit')) : 20
    const offset = params.get('offset') ? Number(params.get('offset')) : 0

    let data = users.map(({ id, username, name, avatar, location, roles, skills, open_to_teamup }) => ({
      id, username, name, avatar, location, roles, skills, open_to_teamup,
    }))
    if (search) data = data.filter((u) => u.name.toLowerCase().includes(search) || u.username.toLowerCase().includes(search))
    if (location) data = data.filter((u) => u.location.toLowerCase().includes(location))
    if (roleId) data = data.filter((u) => u.roles.some((r) => r.id === roleId))
    if (skillId) data = data.filter((u) => u.skills.some((s) => s.id === skillId))
    if (openToTeamup !== null) {
      const resolved = openToTeamup === 'true'
      data = data.filter((u) => u.open_to_teamup === resolved)
    }
    data = data.slice().sort((a, b) => b.id - a.id)

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
      open_to_teamup: body.open_to_teamup ?? true,
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
        open_to_teamup: body.open_to_teamup !== undefined ? (body.open_to_teamup ?? base.open_to_teamup) : base.open_to_teamup,
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

  // POST /api/participation-applications/
  if (/^\/api\/participation-applications\/?$/.test(pathname) && method === 'POST') {
    const body = JSON.parse((options?.body as string) ?? '{}')
    const event = MOCK_EVENTS.find((item) => item.id === Number(body.event_id))
    if (!event) {
      throw new Error('API 400: Event does not exist')
    }
    const me = users[0]
    const skills = (body.skill_ids ?? []).flatMap((skillId: number) => {
      const skill = MOCK_SKILLS.find((item) => item.id === skillId)
      return skill ? [skill] : []
    })
    const nowIso = new Date().toISOString()
    const application: ParticipationApplicationResponse = {
      id: applications.length + 1,
      applicant_user_id: me.id,
      event_id: event.id,
      comment: body.comment ?? '',
      desired_role: body.desired_role ?? '',
      preferred_team_format: (body.preferred_team_format ?? 'team') as PreferredTeamFormat,
      status: 'pending',
      skills,
      applicant: {
        id: me.id,
        username: me.username,
        name: me.name,
        avatar: me.avatar,
        location: me.location,
        roles: me.roles,
        skills: me.skills,
        open_to_teamup: me.open_to_teamup,
      },
      created_at: nowIso,
      updated_at: nowIso,
    }
    applications.unshift(application)
    return application as T
  }

  // GET /api/participation-applications/
  if (/^\/api\/participation-applications\/?$/.test(pathname) && method === 'GET') {
    const eventId = params.get('event_id') ? Number(params.get('event_id')) : null
    const status = params.get('status') as ApplicationStatus | null
    const applicantUserId = params.get('applicant_user_id') ? Number(params.get('applicant_user_id')) : null
    const limit = params.get('limit') ? Number(params.get('limit')) : 20
    const offset = params.get('offset') ? Number(params.get('offset')) : 0

    let data = applications.slice()
    if (eventId !== null) data = data.filter((item) => item.event_id === eventId)
    if (status !== null) data = data.filter((item) => item.status === status)
    if (applicantUserId !== null) data = data.filter((item) => item.applicant_user_id === applicantUserId)

    return { total: data.length, limit, offset, data: data.slice(offset, offset + limit) } as T
  }

  // PATCH /api/participation-applications/:id/status
  const statusMatch = pathname.match(/^\/api\/participation-applications\/(\d+)\/status\/?$/)
  if (statusMatch && method === 'PATCH') {
    const id = Number(statusMatch[1])
    const body = JSON.parse((options?.body as string) ?? '{}')
    const item = applications.find((entry) => entry.id === id)
    if (!item) throw new Error('API 404: Not Found')
    item.status = body.status as ApplicationStatus
    item.updated_at = new Date().toISOString()
    return item as T
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

  // POST /api/public/organizer/import
  if (/^\/api\/public\/organizer\/import\/?$/.test(pathname) && method === 'POST') {
    const body = JSON.parse((options?.body as string) ?? '{}') as OrganizerImportRequest
    const hackathon = body.hackathon
    const teams = body.teams ?? []
    const results = body.results ?? []

    const hasHackathon =
      typeof hackathon?.external_id === 'string' &&
      hackathon.external_id.trim().length > 0 &&
      typeof hackathon?.title === 'string' &&
      hackathon.title.trim().length > 0

    const response: OrganizerImportResponse = {
      hackathons: {
        created: hasHackathon ? 1 : 0,
        updated: 0,
        skipped: hasHackathon ? 0 : 1,
        errors: hasHackathon ? 0 : 1,
      },
      teams: {
        created: teams.length,
        updated: 0,
        skipped: 0,
        errors: 0,
      },
      results: {
        created: results.length,
        updated: 0,
        skipped: 0,
        errors: 0,
      },
      errors: hasHackathon
        ? []
        : [
            {
              entity: 'hackathon',
              key: '',
              detail: 'Hackathon external_id and title are required',
            },
          ],
    }

    return response as T
  }

  throw new Error(`[Mock] Unhandled: ${method} ${pathname}`)
}
