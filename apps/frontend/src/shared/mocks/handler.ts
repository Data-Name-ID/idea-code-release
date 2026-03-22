import type {
  LinkType,
  OrganizerImportRequest,
  OrganizerImportResponse,
  TeamResponse,
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
} from './data'

// Mutable store so PUT changes are reflected within the session
const users: UserResponse[] = MOCK_USERS.map((u) => ({ ...u }))
const teams: TeamResponse[] = MOCK_TEAMS.map((team) => ({
  ...team,
  links: [...team.links],
  users: team.users.map((member) => ({ ...member })),
  events: [...team.events],
}))
const currentUserId = 1
const teamInvites = new Map<
  string,
  { teamId: number; expiresAt: string; usedAt: string | null }
>()

function inferLinkType(url: string): LinkType {
  if (url.includes('github.com')) return 'github'
  if (url.includes('gitlab.com')) return 'gitlab'
  if (url.includes('t.me') || url.includes('telegram')) return 'telegram'
  if (url.includes('twitter.com') || url.includes('x.com')) return 'twitter'
  if (url.includes('instagram.com')) return 'instagram'
  return 'other'
}

function buildTeamList() {
  return teams.map(({ id, name, description, avatar }) => ({ id, name, description, avatar }))
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

    let data = users.map(({ id, username, name, avatar, location, roles, skills }) => ({
      id,
      username,
      name,
      avatar,
      location,
      roles,
      skills,
    }))
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

    let data = buildTeamList()
    if (userId) data = data.filter((t) => teams.find((mt) => mt.id === t.id)?.users.some((u) => u.id === userId))
    if (search) data = data.filter((t) => t.name.toLowerCase().includes(search))
    if (eventId) data = data.filter((t) => teams.find((mt) => mt.id === t.id)?.events.some((e) => e.id === eventId))

    return { total: data.length, limit, offset, data: data.slice(offset, offset + limit) } as T
  }

  // POST /api/teams/
  if (/^\/api\/teams\/?$/.test(pathname) && method === 'POST') {
    const body = JSON.parse(options?.body as string ?? '{}')
    const captain = users.find((user) => user.id === currentUserId) ?? users[0]
    const id = teams.length ? Math.max(...teams.map((team) => team.id)) + 1 : 1

    const newTeam: TeamResponse = {
      id,
      name: body.name ?? `Team ${id}`,
      description: body.description ?? '',
      avatar: body.avatar ?? null,
      location: body.location ?? '',
      links: (body.links ?? []).map((l: { url: string; label: string }) => ({
        ...l,
        type: inferLinkType(l.url),
      })),
      captain_user_id: captain.id,
      users: [
        {
          id: captain.id,
          username: captain.username,
          name: captain.name,
          avatar: captain.avatar,
          location: captain.location,
          roles: captain.roles,
          skills: captain.skills,
        },
      ],
      events: [],
    }
    teams.push(newTeam)
    return newTeam as T
  }

  // POST /api/teams/join-by-invite
  if (/^\/api\/teams\/join-by-invite\/?$/.test(pathname) && method === 'POST') {
    const body = JSON.parse(options?.body as string ?? '{}')
    const token = String(body.token ?? '')
    const invite = teamInvites.get(token)
    if (!invite || invite.usedAt) {
      throw new Error('API 400: Invalid invite link')
    }
    if (new Date(invite.expiresAt).getTime() < Date.now()) {
      throw new Error('API 400: Invite link expired')
    }

    const joinedAt = new Date().toISOString()
    invite.usedAt = joinedAt
    teamInvites.set(token, invite)

    const team = teams.find((item) => item.id === invite.teamId)
    const user = users.find((item) => item.id === currentUserId)
    if (!team || !user) {
      throw new Error('API 404: Team not found')
    }

    if (!team.users.some((member) => member.id === user.id)) {
      team.users.push({
        id: user.id,
        username: user.username,
        name: user.name,
        avatar: user.avatar,
        location: user.location,
        roles: user.roles,
        skills: user.skills,
      })
    }
    return team as T
  }

  // POST /api/teams/:id/invites
  const inviteMatch = pathname.match(/^\/api\/teams\/(\d+)\/invites\/?$/)
  if (inviteMatch && method === 'POST') {
    const teamId = parseInt(inviteMatch[1])
    const team = teams.find((item) => item.id === teamId)
    if (!team) {
      throw new Error('API 404: Team not found')
    }
    if (team.captain_user_id !== currentUserId) {
      throw new Error('API 403: Only captain can create invite links')
    }

    const body = JSON.parse(options?.body as string ?? '{}')
    const expiresInHours = Number(body.expires_in_hours ?? 72)
    const token = `invite-${teamId}-${Date.now()}`
    const expiresAt = new Date(Date.now() + expiresInHours * 60 * 60 * 1000).toISOString()
    teamInvites.set(token, { teamId, expiresAt, usedAt: null })
    return { token, expires_at: expiresAt } as T
  }

  // POST /api/teams/:id/captain/transfer
  const transferMatch = pathname.match(/^\/api\/teams\/(\d+)\/captain\/transfer\/?$/)
  if (transferMatch && method === 'POST') {
    const teamId = parseInt(transferMatch[1])
    const team = teams.find((item) => item.id === teamId)
    if (!team) throw new Error('API 404: Team not found')
    if (team.captain_user_id !== currentUserId) {
      throw new Error('API 403: Only captain can transfer captain role')
    }

    const body = JSON.parse(options?.body as string ?? '{}')
    const newCaptainId = Number(body.new_captain_user_id)
    if (!team.users.some((member) => member.id === newCaptainId)) {
      throw new Error('API 400: New captain must be a team member')
    }
    team.captain_user_id = newCaptainId
    return team as T
  }

  // POST /api/teams/:id/leave
  const leaveMatch = pathname.match(/^\/api\/teams\/(\d+)\/leave\/?$/)
  if (leaveMatch && method === 'POST') {
    const teamId = parseInt(leaveMatch[1])
    const team = teams.find((item) => item.id === teamId)
    if (!team) throw new Error('API 404: Team not found')
    if (team.captain_user_id === currentUserId) {
      throw new Error('API 400: Captain must transfer captain role before leaving')
    }
    team.users = team.users.filter((member) => member.id !== currentUserId)
    return undefined as T
  }

  // DELETE /api/teams/:id/members/:userId
  const removeMemberMatch = pathname.match(/^\/api\/teams\/(\d+)\/members\/(\d+)\/?$/)
  if (removeMemberMatch && method === 'DELETE') {
    const teamId = parseInt(removeMemberMatch[1])
    const memberId = parseInt(removeMemberMatch[2])
    const team = teams.find((item) => item.id === teamId)
    if (!team) throw new Error('API 404: Team not found')
    if (team.captain_user_id !== currentUserId) {
      throw new Error('API 403: Only captain can remove members')
    }
    if (team.captain_user_id === memberId) {
      throw new Error('API 400: Captain cannot be removed')
    }
    team.users = team.users.filter((member) => member.id !== memberId)
    return team as T
  }

  // /api/teams/:id
  const teamMatch = pathname.match(/^\/api\/teams\/(\d+)\/?$/)
  if (teamMatch) {
    const id = parseInt(teamMatch[1])
    const team = teams.find((item) => item.id === id) ?? teams[0]

    if (method === 'GET') {
      return team as T
    }

    if (method === 'PUT') {
      if (team.captain_user_id !== currentUserId) {
        throw new Error('API 403: Only captain can update team profile')
      }

      const body = JSON.parse(options?.body as string ?? '{}')
      team.name = body.name !== undefined ? (body.name ?? team.name) : team.name
      team.description = body.description !== undefined ? (body.description ?? '') : team.description
      team.avatar = body.avatar !== undefined ? body.avatar : team.avatar
      team.location = body.location !== undefined ? (body.location ?? '') : team.location
      team.links = body.links !== undefined
        ? (body.links ?? []).map((l: { url: string; label: string }) => ({
            ...l,
            type: inferLinkType(l.url),
          }))
        : team.links
      return team as T
    }
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
