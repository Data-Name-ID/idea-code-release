import type { EventRatingStatus } from '@shared/types/api'

const longDateFmt = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
})

const shortDateFmt = new Intl.DateTimeFormat('ru-RU', {
  month: 'short',
  year: 'numeric',
})

export function formatDateLong(iso: string): string {
  return longDateFmt.format(new Date(iso))
}

export function formatDateShort(iso: string): string {
  return shortDateFmt.format(new Date(iso))
}

export function initials(name: string): string {
  return name
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0])
    .join('')
    .toUpperCase()
}

export function ratingStatusLabel(status: EventRatingStatus | null): string | null {
  if (status === 'winner') return '1-е место'
  if (status === 'prize_winner') return '2-е место'
  return null
}
