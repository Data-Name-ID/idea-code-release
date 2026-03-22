import type {
  RoleResponse,
  SkillResponse,
  UserResponse,
  UserListResponse,
  EventResponse,
  EventListResponse,
  EventRatingResponse,
  TeamResponse,
  TeamListResponse,
  LinkType,
} from '@shared/types/api'

// ─── Roles ────────────────────────────────────────────────

export const MOCK_ROLES: RoleResponse[] = [
  { id: 1, name: 'Designer' },
  { id: 2, name: 'Frontend Developer' },
  { id: 3, name: 'Backend Developer' },
  { id: 4, name: 'ML Engineer' },
  { id: 5, name: 'DevOps Engineer' },
  { id: 6, name: 'Tech Lead' },
  { id: 7, name: 'Product Manager' },
  { id: 8, name: 'QA Engineer' },
]

// ─── Skills ───────────────────────────────────────────────

export const MOCK_SKILLS: SkillResponse[] = [
  { id: 1, name: 'React' },
  { id: 2, name: 'TypeScript' },
  { id: 3, name: 'Figma' },
  { id: 4, name: 'Python' },
  { id: 5, name: 'FastAPI' },
  { id: 6, name: 'PostgreSQL' },
  { id: 7, name: 'PyTorch' },
  { id: 8, name: 'LangChain' },
  { id: 9, name: 'Docker' },
  { id: 10, name: 'Vue.js' },
  { id: 11, name: 'Node.js' },
  { id: 12, name: 'Go' },
  { id: 13, name: 'Kubernetes' },
  { id: 14, name: 'AWS' },
  { id: 15, name: 'GraphQL' },
  { id: 16, name: 'Rust' },
]

// ─── Users ────────────────────────────────────────────────

export const MOCK_USERS: UserResponse[] = [
  {
    id: 1,
    username: 'aleksei_volkov',
    email: 'volkov@binary-wolves.ru',
    name: 'Aleksei Volkov',
    avatar: null,
    description: 'Full-Stack разработчик и Tech Lead с опытом в ML-проектах.',
    location: 'Москва, Россия',
    links: [
      { url: 'https://github.com/aleksei-volkov', label: 'GitHub', type: 'github' as LinkType },
      { url: 'https://t.me/aleksei_volkov', label: 'Telegram', type: 'telegram' as LinkType },
      { url: 'https://twitter.com/aleksei_volkov', label: 'Twitter', type: 'twitter' as LinkType },
    ],
    roles: [
      { id: 6, name: 'Tech Lead' },
      { id: 2, name: 'Frontend Developer' },
      { id: 4, name: 'ML Engineer' },
    ],
    skills: [
      { id: 4, name: 'Python' },
      { id: 5, name: 'FastAPI' },
      { id: 6, name: 'PostgreSQL' },
      { id: 7, name: 'PyTorch' },
      { id: 8, name: 'LangChain' },
      { id: 1, name: 'React' },
      { id: 2, name: 'TypeScript' },
      { id: 9, name: 'Docker' },
    ],
  },
  {
    id: 2,
    username: 'maria_smirnova',
    email: 'smirnova@design.ru',
    name: 'Maria Smirnova',
    avatar: null,
    description: 'UI/UX дизайнер, специализируюсь на продуктовом дизайне.',
    location: 'Санкт-Петербург, Россия',
    links: [
      { url: 'https://github.com/maria-smirnova', label: 'GitHub', type: 'github' as LinkType },
      { url: 'https://t.me/maria_design', label: 'Telegram', type: 'telegram' as LinkType },
    ],
    roles: [
      { id: 1, name: 'Designer' },
      { id: 2, name: 'Frontend Developer' },
    ],
    skills: [
      { id: 3, name: 'Figma' },
      { id: 10, name: 'Vue.js' },
      { id: 2, name: 'TypeScript' },
      { id: 15, name: 'GraphQL' },
    ],
  },
  {
    id: 3,
    username: 'ivan_petrov',
    email: 'petrov@backend.dev',
    name: 'Ivan Petrov',
    avatar: null,
    description: 'Backend-разработчик, фанат распределённых систем и Go.',
    location: 'Казань, Россия',
    links: [
      { url: 'https://github.com/ivan-petrov', label: 'GitHub', type: 'github' as LinkType },
    ],
    roles: [
      { id: 3, name: 'Backend Developer' },
    ],
    skills: [
      { id: 12, name: 'Go' },
      { id: 6, name: 'PostgreSQL' },
      { id: 9, name: 'Docker' },
      { id: 13, name: 'Kubernetes' },
      { id: 14, name: 'AWS' },
    ],
  },
  {
    id: 4,
    username: 'dmitry_kuznetsov',
    email: 'kuznetsov@devops.io',
    name: 'Dmitry Kuznetsov',
    avatar: null,
    description: 'DevOps-инженер, строю надёжную инфраструктуру.',
    location: 'Новосибирск, Россия',
    links: [
      { url: 'https://github.com/dm-kuznetsov', label: 'GitHub', type: 'github' as LinkType },
      { url: 'https://t.me/dm_devops', label: 'Telegram', type: 'telegram' as LinkType },
    ],
    roles: [
      { id: 5, name: 'DevOps Engineer' },
    ],
    skills: [
      { id: 9, name: 'Docker' },
      { id: 13, name: 'Kubernetes' },
      { id: 14, name: 'AWS' },
      { id: 16, name: 'Rust' },
    ],
  },
  {
    id: 5,
    username: 'anna_sokolova',
    email: 'sokolova@product.ru',
    name: 'Anna Sokolova',
    avatar: null,
    description: 'Продуктовый менеджер с фокусом на B2B-продукты.',
    location: 'Москва, Россия',
    links: [
      { url: 'https://t.me/anna_pm', label: 'Telegram', type: 'telegram' as LinkType },
      { url: 'https://instagram.com/anna_sokolova', label: 'Instagram', type: 'instagram' as LinkType },
    ],
    roles: [
      { id: 7, name: 'Product Manager' },
    ],
    skills: [
      { id: 3, name: 'Figma' },
      { id: 15, name: 'GraphQL' },
    ],
  },
]

export const MOCK_USERS_LIST: UserListResponse = {
  total: MOCK_USERS.length,
  limit: 20,
  offset: 0,
  data: MOCK_USERS.map(({ id, username, name, avatar, location, roles, skills }) => ({
    id,
    username,
    name,
    avatar,
    location,
    roles,
    skills,
  })),
}

// ─── Events ───────────────────────────────────────────────

export const MOCK_EVENTS: EventResponse[] = [
  {
    id: 1,
    title: 'Hackathon Prod 2024',
    description: '48-часовой продуктовый хакатон для команд до 5 человек.',
    date: '2024-10-15T10:00:00Z',
    cover: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&q=80',
    is_verify: true,
  },
  {
    id: 2,
    title: 'Digital Sprint Challenge',
    description: 'Соревнование по быстрому прототипированию цифровых продуктов.',
    date: '2024-08-20T10:00:00Z',
    cover: 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&q=80',
    is_verify: true,
  },
  {
    id: 3,
    title: 'Startup Weekend MSK',
    description: 'Трёхдневный интенсив для создания стартапов с нуля.',
    date: '2024-06-08T10:00:00Z',
    cover: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=600&q=80',
    is_verify: true,
  },
  {
    id: 4,
    title: 'Innopolis Hack Spring',
    description: 'Университетский хакатон с фокусом на EdTech и AI-решения.',
    date: '2024-05-03T10:00:00Z',
    cover: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=600&q=80',
    is_verify: true,
  },
]

export const MOCK_EVENTS_LIST: EventListResponse = {
  total: MOCK_EVENTS.length,
  limit: 20,
  offset: 0,
  data: MOCK_EVENTS,
}

// ─── Ratings ──────────────────────────────────────────────
// team_ids: 1=Binary Wolves, 2=Neural Nomads, 3=Code Pirates

export const MOCK_RATINGS: Record<number, EventRatingResponse> = {
  1: {
    event_id: 1,
    ratings: [
      { user_id: 1, status: 'winner', place: 1, team_id: 1, awarded_at: '2024-10-15T22:00:00Z' },
      { user_id: 2, status: 'prize_winner', place: 2, team_id: 2, awarded_at: '2024-10-15T22:05:00Z' },
      { user_id: 3, status: 'participant', place: 4, team_id: null, awarded_at: '2024-10-15T22:10:00Z' },
    ],
  },
  2: {
    event_id: 2,
    ratings: [
      { user_id: 3, status: 'winner', place: 1, team_id: null, awarded_at: '2024-08-20T20:00:00Z' },
      { user_id: 1, status: 'prize_winner', place: 2, team_id: 2, awarded_at: '2024-08-20T20:05:00Z' },
      { user_id: 4, status: 'participant', place: 4, team_id: null, awarded_at: '2024-08-20T20:10:00Z' },
    ],
  },
  3: {
    event_id: 3,
    ratings: [
      { user_id: 4, status: 'winner', place: 1, team_id: 3, awarded_at: '2024-06-08T18:00:00Z' },
      { user_id: 5, status: 'prize_winner', place: 2, team_id: null, awarded_at: '2024-06-08T18:05:00Z' },
      { user_id: 1, status: 'participant', place: 4, team_id: 3, awarded_at: '2024-06-08T18:10:00Z' },
    ],
  },
  4: {
    event_id: 4,
    ratings: [
      { user_id: 1, status: 'winner', place: 1, team_id: 1, awarded_at: '2024-05-03T19:00:00Z' },
      { user_id: 2, status: 'participant', place: 4, team_id: null, awarded_at: '2024-05-03T19:05:00Z' },
      { user_id: 5, status: 'participant', place: 5, team_id: null, awarded_at: '2024-05-03T19:10:00Z' },
    ],
  },
}

// ─── Teams ────────────────────────────────────────────────

const _users = MOCK_USERS // shorthand

export const MOCK_TEAMS: TeamResponse[] = [
  {
    id: 1,
    name: 'Binary Wolves',
    description: 'Команда Full-Stack и ML разработчиков.',
    users: [_users[0], _users[1], _users[2], _users[3], _users[4]].map(
      ({ id, username, name, avatar, location, roles, skills }) => ({
        id, username, name, avatar, location, roles, skills,
      }),
    ),
    events: [MOCK_EVENTS[0], MOCK_EVENTS[3]],
  },
  {
    id: 2,
    name: 'Neural Nomads',
    description: 'ML-инженеры и дата-сайентисты.',
    users: [_users[0], _users[1], _users[2], _users[4]].map(
      ({ id, username, name, avatar, location, roles, skills }) => ({
        id, username, name, avatar, location, roles, skills,
      }),
    ),
    events: [MOCK_EVENTS[0], MOCK_EVENTS[1]],
  },
  {
    id: 3,
    name: 'Code Pirates',
    description: 'Backend и DevOps энтузиасты.',
    users: [_users[0], _users[1], _users[2], _users[3]].map(
      ({ id, username, name, avatar, location, roles, skills }) => ({
        id, username, name, avatar, location, roles, skills,
      }),
    ),
    events: [MOCK_EVENTS[2]],
  },
]

export const MOCK_TEAMS_LIST: TeamListResponse = {
  total: MOCK_TEAMS.length,
  limit: 20,
  offset: 0,
  data: MOCK_TEAMS.map(({ id, name, description }) => ({ id, name, description })),
}
