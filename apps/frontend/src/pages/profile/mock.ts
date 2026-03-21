import type { UserResponse } from '@shared/types/api'
import type { ActivityItem } from '@widgets/ActivityFeed/ui/ActivityFeed.vue'
import type { TeamEntry } from '@widgets/TeamsCard/ui/TeamsCard.vue'

export const MOCK_USER: UserResponse = {
  id: 1,
  username: 'aleksei_volkov',
  email: 'волков@binary-wolves.ru',
  name: 'Aleksei Volkov',
  avatar: null,
  description: 'Full-Stack разработчик и Tech Lead с опытом в ML-проектах.',
  location: 'Москва, Россия',
  links: [
    { url: 'https://github.com/aleksei-volkov', label: 'GitHub', type: 'github' },
    { url: 'https://t.me/aleksei_volkov', label: 'Telegram', type: 'telegram' },
    { url: 'https://twitter.com/aleksei_volkov', label: 'Twitter', type: 'twitter' },
  ],
  roles: [
    { id: 1, name: 'Tech Lead' },
    { id: 2, name: 'Full-Stack Developer' },
    { id: 3, name: 'ML Engineer' },
  ],
  skills: [
    { id: 1, name: 'Python' },
    { id: 2, name: 'FastAPI' },
    { id: 3, name: 'PostgreSQL' },
    { id: 4, name: 'PyTorch' },
    { id: 5, name: 'LangChain' },
    { id: 6, name: 'React' },
    { id: 7, name: 'TypeScript' },
    { id: 8, name: 'Docker' },
  ],
}

export const MOCK_HACKATHON_COUNT = 9
export const MOCK_WIN_COUNT = 4
export const MOCK_RANK = 1

export const MOCK_ACTIVITY: ActivityItem[] = [
  {
    event: {
      id: 1,
      title: 'Hackathon Prod 2024',
      description: '',
      date: '2024-10-15T10:00:00Z',
      cover: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&q=80',
      is_verify: true,
    },
    status: 'winner',
    teamName: 'Binary Wolves',
  },
  {
    event: {
      id: 2,
      title: 'Digital Sprint Challenge',
      description: '',
      date: '2024-08-20T10:00:00Z',
      cover: 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&q=80',
      is_verify: true,
    },
    status: 'prize_winner',
    teamName: 'Neural Nomads',
  },
  {
    event: {
      id: 3,
      title: 'Startup Weekend MSK',
      description: '',
      date: '2024-06-08T10:00:00Z',
      cover: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=600&q=80',
      is_verify: true,
    },
    status: 'participant',
    teamName: 'Code Pirates',
  },
  {
    event: {
      id: 4,
      title: 'Innopolis Hack Spring',
      description: '',
      date: '2024-05-03T10:00:00Z',
      cover: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=600&q=80',
      is_verify: true,
    },
    status: 'winner',
    teamName: 'Binary Wolves',
  },
]

export const MOCK_TEAMS: TeamEntry[] = [
  {
    id: 1,
    name: 'Binary Wolves',
    role: 'Tech Lead',
    isActive: true,
    winCount: 7,
    memberCount: 5,
  },
  {
    id: 2,
    name: 'Neural Nomads',
    role: 'ML Engineer',
    isActive: true,
    winCount: 4,
    memberCount: 4,
  },
  {
    id: 3,
    name: 'Code Pirates',
    role: 'Fullstack Developer',
    isActive: false,
    winCount: 2,
    memberCount: 6,
  },
]
