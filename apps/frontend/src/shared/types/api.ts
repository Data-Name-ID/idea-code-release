// ─── Links ────────────────────────────────────────────────

export type LinkType = 'telegram' | 'github' | 'gitlab' | 'twitter' | 'instagram' | 'other'

export interface LinkResponse {
  url: string
  label: string
  type: LinkType
}

export interface LinkRequest {
  url: string
  label: string
}

export interface OkResponse<T> {
  status: string
  data: T | null
}

export interface PaginatedResponse<T> {
  total: number
  limit: number
  offset: number
  data: T[]
}

// ─── Roles & Skills ───────────────────────────────────────

export interface RoleResponse {
  id: number
  name: string
}

export interface SkillResponse {
  id: number
  name: string
}

// ─── User ─────────────────────────────────────────────────

export interface UserResponse {
  id: number
  username: string
  email: string | null
  name: string
  avatar: string | null
  description: string
  location: string
  links: LinkResponse[]
  roles: RoleResponse[]
  skills: SkillResponse[]
  open_to_teamup: boolean
}

export interface UserShortResponse {
  id: number
  username: string
  name: string
  avatar: string | null
  location: string
  roles: RoleResponse[]
  skills: SkillResponse[]
  open_to_teamup: boolean
}

export interface UserListResponse {
  total: number
  limit: number
  offset: number
  data: UserShortResponse[]
}

export interface UserCreateRequest {
  username: string
  name: string
  email?: string | null
  avatar?: string | null
  description?: string
  location?: string
  links?: LinkRequest[]
  role_ids?: number[]
  skill_ids?: number[]
  open_to_teamup?: boolean
}

export interface UserUpdateRequest {
  name?: string | null
  email?: string | null
  avatar?: string | null
  description?: string | null
  location?: string | null
  links?: LinkRequest[] | null
  role_ids?: number[] | null
  skill_ids?: number[] | null
  open_to_teamup?: boolean | null
}

export interface UsersListParams {
  limit?: number
  offset?: number
  search?: string
  location?: string
  role_id?: number
  skill_id?: number
  open_to_teamup?: boolean
}

// ─── Events ───────────────────────────────────────────────

export type EventRatingStatus = 'winner' | 'prize_winner' | 'participant'

export interface EventResponse {
  id: number
  title: string
  description: string
  date: string // ISO 8601 datetime string
  cover: string | null
  is_verify: boolean
}

export interface EventListResponse {
  total: number
  limit: number
  offset: number
  data: EventResponse[]
}

export interface EventParticipationCreateRequest {
  title: string
  description?: string
  date: string
  cover?: string | null
  team_id?: number | null
}

export interface EventRatingEntryResponse {
  user_id: number
  status: EventRatingStatus
  place: number | null
  team_id: number | null
  awarded_at: string | null
}

export interface EventRatingResponse {
  event_id: number
  ratings: EventRatingEntryResponse[]
}

// ─── Teams ────────────────────────────────────────────────

export interface TeamShortResponse {
  id: number
  name: string
  description: string
}

export interface TeamResponse {
  id: number
  name: string
  description: string
  users: UserShortResponse[]
  events: EventResponse[]
}

export interface TeamListResponse {
  total: number
  limit: number
  offset: number
  data: TeamShortResponse[]
}

export interface TeamCreateRequest {
  name: string
  description?: string
  user_ids?: number[]
}

// ─── Participation Applications ───────────────────────────

export type ApplicationStatus = 'pending' | 'approved' | 'rejected'
export type PreferredTeamFormat = 'solo' | 'team'

export interface ParticipationApplicationResponse {
  id: number
  applicant_user_id: number
  event_id: number
  comment: string
  desired_role: string
  preferred_team_format: PreferredTeamFormat
  status: ApplicationStatus
  skills: SkillResponse[]
  applicant: UserShortResponse | null
  created_at: string
  updated_at: string
}

export interface ParticipationApplicationCreateRequest {
  event_id: number
  comment?: string
  desired_role?: string
  preferred_team_format?: PreferredTeamFormat
  skill_ids?: number[]
}

export interface ParticipationApplicationStatusUpdateRequest {
  status: ApplicationStatus
}

export interface ParticipationApplicationListParams {
  limit?: number
  offset?: number
  event_id?: number
  status?: ApplicationStatus
  applicant_user_id?: number
}

export interface ParticipationApplicationListResponse {
  total: number
  limit: number
  offset: number
  data: ParticipationApplicationResponse[]
}

export interface TeamsListParams {
  limit?: number
  offset?: number
  search?: string
  event_id?: number
  user_id?: number
}

// ─── Auth ─────────────────────────────────────────────────

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: UserResponse
}

export interface RefreshResponse {
  access_token: string
  token_type: string
  expires_in: number
}

// ─── Organizer Import ────────────────────────────────────

export interface OrganizerMemberInput {
  telegram_id?: number | null
  email?: string | null
  username?: string | null
  name?: string
  avatar?: string | null
}

export interface OrganizerHackathonInput {
  external_id: string
  title: string
  description?: string
  date: string
  cover?: string | null
}

export interface OrganizerTeamInput {
  external_id: string
  name: string
  description?: string
  members?: OrganizerMemberInput[]
}

export interface OrganizerResultInput {
  status?: EventRatingStatus | null
  place?: number | null
  awarded_at?: string | null
  team_external_id?: string | null
  user?: OrganizerMemberInput | null
}

export interface OrganizerImportRequest {
  hackathon: OrganizerHackathonInput
  teams: OrganizerTeamInput[]
  results: OrganizerResultInput[]
}

export interface OrganizerImportCounters {
  created: number
  updated: number
  skipped: number
  errors: number
}

export interface OrganizerImportError {
  entity: string
  key: string
  detail: string
}

export interface OrganizerImportResponse {
  hackathons: OrganizerImportCounters
  teams: OrganizerImportCounters
  results: OrganizerImportCounters
  errors: OrganizerImportError[]
}
