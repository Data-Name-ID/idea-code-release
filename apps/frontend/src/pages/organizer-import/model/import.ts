import * as XLSX from 'xlsx'

import type {
  EventRatingStatus,
  OrganizerHackathonInput,
  OrganizerImportRequest,
  OrganizerMemberInput,
  OrganizerResultInput,
  OrganizerTeamInput,
} from '@shared/types/api'

export interface ParsedImportData {
  payload: OrganizerImportRequest
  warnings: string[]
}

export const EMPTY_IMPORT_PAYLOAD: OrganizerImportRequest = {
  hackathon: {
    external_id: '',
    title: '',
    description: '',
    date: '',
    cover: '',
  },
  teams: [],
  results: [],
}

const SESSION_STORAGE_TOKEN_KEY = 'organizer_api_key'

const STRICT_SHEETS = {
  hackathon: 'hackathon',
  teams: 'teams',
  results: 'results',
} as const

const RESULT_STATUS_VALUES = new Set<EventRatingStatus>([
  'winner',
  'prize_winner',
  'participant',
])

export function getStoredOrganizerApiKey(): string {
  return sessionStorage.getItem(SESSION_STORAGE_TOKEN_KEY) ?? ''
}

export function setStoredOrganizerApiKey(value: string): void {
  if (value.trim() === '') {
    sessionStorage.removeItem(SESSION_STORAGE_TOKEN_KEY)
    return
  }
  sessionStorage.setItem(SESSION_STORAGE_TOKEN_KEY, value)
}

export function clearStoredOrganizerApiKey(): void {
  sessionStorage.removeItem(SESSION_STORAGE_TOKEN_KEY)
}

export function statusFromPlace(place: number | null | undefined): EventRatingStatus {
  if (place === 1) return 'winner'
  if (place === 2 || place === 3) return 'prize_winner'
  return 'participant'
}

export function placeFromStatus(status: EventRatingStatus): number {
  if (status === 'winner') return 1
  if (status === 'prize_winner') return 2
  return 4
}

export function countMembers(payload: OrganizerImportRequest): number {
  return payload.teams.reduce((acc, team) => acc + (team.members?.length ?? 0), 0)
}

export async function parseImportFile(file: File): Promise<ParsedImportData> {
  const extension = file.name.split('.').pop()?.toLowerCase() ?? ''

  if (extension === 'json') {
    return parseJsonImport(await file.text())
  }
  if (extension === 'csv') {
    return parseCsvImport(await file.text())
  }
  if (extension === 'xlsx') {
    return parseXlsxImport(await file.arrayBuffer())
  }

  throw new Error('Поддерживаются только файлы .xlsx, .csv и .json')
}

export function validateImportPayload(payload: OrganizerImportRequest): string[] {
  const errors: string[] = []

  if (payload.hackathon.external_id.trim() === '') errors.push('Хакатон: заполните external_id')
  if (payload.hackathon.title.trim() === '') errors.push('Хакатон: заполните название')
  if (payload.hackathon.date.trim() === '') errors.push('Хакатон: заполните дату')

  payload.teams.forEach((team, index) => {
    if ((team.external_id ?? '').trim() === '') {
      errors.push(`Команда #${index + 1}: заполните external_id`)
    }
    if ((team.name ?? '').trim() === '') {
      errors.push(`Команда #${index + 1}: заполните название`)
    }
    const members = team.members ?? []
    members.forEach((member, memberIndex) => {
      if (hasParticipantIdentity(member) === false) {
        errors.push(
          `Команда #${index + 1}, участник #${memberIndex + 1}: укажите telegram_id или email`,
        )
      }
    })
  })

  payload.results.forEach((result, index) => {
    const hasTeam = (result.team_external_id ?? '').trim() !== ''
    const hasUser = hasParticipantIdentity(result.user)

    if (hasTeam === false && hasUser === false) {
      errors.push(`Результат #${index + 1}: укажите team_external_id или user`)
    }
    if (hasTeam && hasUser) {
      errors.push(`Результат #${index + 1}: укажите только team_external_id или только user`)
    }
    if (result.user != null && hasParticipantIdentity(result.user) === false) {
      errors.push(`Результат #${index + 1}: для user нужен telegram_id или email`)
    }

    const hasStatus = typeof result.status === 'string' && result.status.trim() !== ''
    const hasPlace = typeof result.place === 'number' && Number.isFinite(result.place)

    if (hasStatus === false && hasPlace === false) {
      errors.push(`Результат #${index + 1}: нужен status или place`)
    }
    if (typeof result.place === 'number' && result.place <= 0) {
      errors.push(`Результат #${index + 1}: place должен быть > 0`)
    }
  })

  return errors
}

export function createJsonTemplateContent(): string {
  return JSON.stringify(
    {
      hackathon: {
        external_id: 'spring-hack-2026',
        title: 'Spring Hack 2026',
        description: 'Открытый городской хакатон',
        date: '2026-04-20T10:00:00Z',
        cover: 'https://example.com/banner.jpg',
      },
      teams: [
        {
          external_id: 'team-alpha',
          name: 'Team Alpha',
          description: 'ML + Product',
          members: [
            { telegram_id: 123456, email: 'alice@example.com', name: 'Alice' },
          ],
        },
      ],
      results: [
        { status: 'winner', place: 1, team_external_id: 'team-alpha', awarded_at: '2026-04-20T18:00:00Z' },
      ],
    },
    null,
    2,
  )
}

export function createCsvTemplateContent(): string {
  return [
    'row_type,external_id,title,description,date,cover,name,member_name,member_email,member_tg_id,status,place,team_external_id,awarded_at,user_name,user_telegram_id,user_email',
    'hackathon,spring-hack-2026,Spring Hack 2026,Открытый городской хакатон,2026-04-20T10:00:00Z,https://example.com/banner.jpg,,,,,,,,,,,',
    'team,team-alpha,,,,,Team Alpha,Alice,alice@example.com,123456,,,,,,,',
    'result,,,,,,,,,,winner,1,team-alpha,2026-04-20T18:00:00Z,,,',
  ].join('\n')
}

export function createXlsxTemplateBlob(): Blob {
  const wb = XLSX.utils.book_new()
  const hackathonRows = [
    ['external_id*', 'title*', 'date*', 'description', 'cover'],
    [
      'spring-hack-2026',
      'Spring Hack 2026',
      '2026-04-20T10:00:00Z',
      'Открытый городской хакатон',
      'https://example.com/banner.jpg',
    ],
  ]
  const teamsRows = [
    [
      'external_id*',
      'name*',
      'description',
      'member_name',
      'member_email',
      'member_tg_id',
    ],
    [
      'team-alpha',
      'Team Alpha',
      'ML + Product',
      'Alice',
      'alice@example.com',
      123456,
    ],
    ['', '', '', 'Bob', '', 789123],
  ]
  const resultsRows = [
    [
      'status',
      'place',
      'team_external_id',
      'awarded_at',
      'user_name',
      'user_email',
      'user_tg_id',
    ],
    ['winner', 1, 'team-alpha', '2026-04-20T18:00:00Z', '', '', ''],
  ]
  const guideRows = [
    ['Поле', 'Правило'],
    ['*', 'Обязательное поле'],
    ['teams.member_email / teams.member_tg_id', 'Хотя бы одно из двух обязательно'],
    ['results.user_email / results.user_tg_id', 'Если результат персональный, одно из двух обязательно'],
  ]

  const hackathonSheet = XLSX.utils.aoa_to_sheet(hackathonRows)
  const teamsSheet = XLSX.utils.aoa_to_sheet(teamsRows)
  const resultsSheet = XLSX.utils.aoa_to_sheet(resultsRows)
  const guideSheet = XLSX.utils.aoa_to_sheet(guideRows)

  styleHeaderRow(hackathonSheet, hackathonRows[0].length)
  styleHeaderRow(teamsSheet, teamsRows[0].length)
  styleHeaderRow(resultsSheet, resultsRows[0].length)
  styleHeaderRow(guideSheet, guideRows[0].length)

  hackathonSheet['!autofilter'] = { ref: `A1:E${hackathonRows.length}` }
  teamsSheet['!autofilter'] = { ref: `A1:F${teamsRows.length}` }
  resultsSheet['!autofilter'] = { ref: `A1:G${resultsRows.length}` }

  hackathonSheet['!cols'] = [{ wch: 20 }, { wch: 24 }, { wch: 22 }, { wch: 36 }, { wch: 36 }]
  teamsSheet['!cols'] = [
    { wch: 20 },
    { wch: 20 },
    { wch: 26 },
    { wch: 18 },
    { wch: 24 },
    { wch: 14 },
  ]
  resultsSheet['!cols'] = [
    { wch: 15 },
    { wch: 8 },
    { wch: 20 },
    { wch: 22 },
    { wch: 18 },
    { wch: 24 },
    { wch: 14 },
  ]
  guideSheet['!cols'] = [{ wch: 34 }, { wch: 64 }]

  XLSX.utils.book_append_sheet(wb, hackathonSheet, STRICT_SHEETS.hackathon)
  XLSX.utils.book_append_sheet(wb, teamsSheet, STRICT_SHEETS.teams)
  XLSX.utils.book_append_sheet(wb, resultsSheet, STRICT_SHEETS.results)
  XLSX.utils.book_append_sheet(wb, guideSheet, 'guide')

  const bytes = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  return new Blob([bytes], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  })
}

function parseJsonImport(text: string): ParsedImportData {
  const parsed = JSON.parse(text) as Partial<OrganizerImportRequest>
  return { payload: normalizePayload(parsed), warnings: [] }
}

function parseCsvImport(text: string): ParsedImportData {
  const rows = parseCsvRows(text).map((row) => normalizeRecordKeys(row))
  if (rows.length === 0) throw new Error('CSV-файл пустой')

  const payload = structuredClone(EMPTY_IMPORT_PAYLOAD)
  const warnings: string[] = []

  const hackathonRow = rows.find((row) => String(row.row_type ?? '').toLowerCase() === 'hackathon')
  if (hackathonRow) payload.hackathon = parseHackathonRow(hackathonRow)
  else warnings.push('В CSV не найдена строка row_type=hackathon')

  payload.teams = rows
    .filter((row) => String(row.row_type ?? '').toLowerCase() === 'team')
    .map((row) => parseTeamRow(row))

  payload.results = rows
    .filter((row) => String(row.row_type ?? '').toLowerCase() === 'result')
    .map((row) => parseResultRow(row))

  return { payload, warnings }
}

function parseXlsxImport(buffer: ArrayBuffer): ParsedImportData {
  const wb = XLSX.read(buffer, { type: 'array', cellDates: false })
  const sheetMap = new Map(wb.SheetNames.map((name) => [name.trim().toLowerCase(), name]))
  const payload = structuredClone(EMPTY_IMPORT_PAYLOAD)
  const warnings: string[] = []

  const strictHackathon = sheetMap.get('hackathon')
  const strictTeams = sheetMap.get('teams')
  const strictResults = sheetMap.get('results')

  if (strictHackathon && strictTeams && strictResults) {
    const hackathonRows = readSheetRows(wb, strictHackathon)
    if (hackathonRows[0]) payload.hackathon = parseHackathonRow(normalizeRecordKeys(hackathonRows[0]))
    else warnings.push('Лист hackathon пуст')

    payload.teams = mergeTeams(
      readSheetRows(wb, strictTeams).map((row) => parseTeamRow(normalizeRecordKeys(row))),
    )
    payload.results = readSheetRows(wb, strictResults).map((row) => parseResultRow(normalizeRecordKeys(row)))
    return { payload, warnings }
  }

  const allRows = wb.SheetNames.flatMap((sheetName) =>
    readSheetRows(wb, sheetName).map((row) => normalizeRecordKeys(row)),
  )
  if (allRows.length === 0) throw new Error('XLSX-файл пустой')

  const hackathonRow = allRows.find((row) => pickValue(row, ['external_id', 'id']).trim() !== '')
  if (hackathonRow) payload.hackathon = parseHackathonRow(hackathonRow)
  else warnings.push('Не удалось определить хакатон автоматически. Заполните в мастере.')

  payload.teams = mergeTeams(
    allRows
    .filter((row) => pickValue(row, ['team_external_id', 'external_id', 'команда_id']).trim() !== '' && pickValue(row, ['name', 'team_name', 'команда']).trim() !== '')
    .map((row) => parseTeamRow(row))
  )

  payload.results = allRows
    .filter((row) => {
      const hasStatus = pickValue(row, ['status', 'статус']).trim() !== ''
      const hasPlace = pickValue(row, ['place', 'место', 'rank']).trim() !== ''
      const hasTarget =
        pickValue(row, ['team_external_id', 'team_id', 'команда_id']).trim() !== '' ||
        pickValue(row, ['user', 'user_email', 'email', 'user_tg_id', 'telegram_id']).trim() !== ''
      return (hasStatus || hasPlace) && hasTarget
    })
    .map((row) => parseResultRow(row))

  return { payload, warnings }
}

function parseHackathonRow(row: Record<string, unknown>): OrganizerHackathonInput {
  return {
    external_id: pickValue(row, ['external_id', 'id', 'внешний_id']),
    title: pickValue(row, ['title', 'name', 'название']),
    description: pickValue(row, ['description', 'desc', 'описание']),
    date: pickValue(row, ['date', 'event_date', 'дата']),
    cover: pickValue(row, ['cover', 'image', 'banner', 'обложка']),
  }
}

function parseTeamRow(row: Record<string, unknown>): OrganizerTeamInput {
  const membersFromSerialized = parseMembers(pickValue(row, ['members', 'users', 'participants', 'участники']))
  const memberFromColumns = parseMemberFromRow(row, [
    ['member_telegram_id', 'member_tg_id', 'telegram_id', 'tg_id'],
    ['member_email', 'email', 'почта'],
    ['member_username', 'username', 'логин'],
    ['member_name', 'name', 'имя'],
    ['member_avatar', 'avatar', 'аватар'],
  ])

  return {
    external_id: pickValue(row, ['external_id', 'team_external_id', 'id', 'команда_id']),
    name: pickValue(row, ['name', 'team_name', 'команда', 'название']),
    description: pickValue(row, ['description', 'desc', 'описание']),
    members: [...membersFromSerialized, ...(memberFromColumns ? [memberFromColumns] : [])],
  }
}

function parseResultRow(row: Record<string, unknown>): OrganizerResultInput {
  const statusText = pickValue(row, ['status', 'статус']).toLowerCase()
  const placeText = pickValue(row, ['place', 'место', 'rank'])
  const placeNum = placeText === '' ? null : Number(placeText)
  const parsedStatus = RESULT_STATUS_VALUES.has(statusText as EventRatingStatus)
    ? (statusText as EventRatingStatus)
    : placeNum !== null && Number.isFinite(placeNum)
      ? statusFromPlace(placeNum)
      : null

  const resolvedPlace =
    placeNum !== null && Number.isFinite(placeNum)
      ? placeNum
      : parsedStatus
        ? placeFromStatus(parsedStatus)
        : null

  const userField = parseSingleMember(pickValue(row, ['user', 'participant', 'участник']))
  const userColumns = parseMemberFromRow(row, [
    ['user_telegram_id', 'user_tg_id', 'telegram_id', 'tg_id'],
    ['user_email', 'email', 'почта'],
    ['user_username', 'username', 'логин'],
    ['user_name', 'name', 'имя'],
    ['user_avatar', 'avatar', 'аватар'],
  ]) ?? normalizeMember({
    telegram_id: toNullableNumber(pickValue(row, ['user_telegram_id', 'telegram_id', 'tg_id'])),
    email: toNullableString(pickValue(row, ['user_email', 'email', 'почта'])),
    username: toNullableString(pickValue(row, ['user_username', 'username', 'логин'])),
    name: toNullableString(pickValue(row, ['user_name', 'name', 'имя'])) ?? '',
    avatar: toNullableString(pickValue(row, ['user_avatar', 'avatar', 'аватар'])),
  })

  return {
    status: parsedStatus,
    place: resolvedPlace,
    awarded_at: pickValue(row, ['awarded_at', 'award_date', 'дата_награды']) || null,
    team_external_id: pickValue(row, ['team_external_id', 'team_id', 'команда_id']) || null,
    user: hasParticipantIdentity(userField) ? userField : hasParticipantIdentity(userColumns) ? userColumns : null,
  }
}

function parseMembers(value: string): OrganizerMemberInput[] {
  if (value.trim() === '') return []

  try {
    const parsed = JSON.parse(value)
    if (Array.isArray(parsed)) {
      return parsed.map((entry) => normalizeMember(entry)).filter((item) => hasParticipantIdentity(item))
    }
  } catch {
    // fallback below
  }

  return value
    .split(';')
    .map((chunk) => parseSingleMember(chunk))
    .filter((item) => hasParticipantIdentity(item))
}

function parseSingleMember(value: string): OrganizerMemberInput {
  const trimmed = value.trim()
  if (trimmed === '') return { name: '' }

  try {
    return normalizeMember(JSON.parse(trimmed))
  } catch {
    // fallback below
  }

  const member: OrganizerMemberInput = { name: '' }
  trimmed
    .split('|')
    .map((item) => item.trim())
    .filter((item) => item !== '')
    .forEach((item) => {
      const [rawKey, ...rest] = item.split(/[:=]/)
      const key = normalizeKey(rawKey)
      const valuePart = rest.join('=').trim()
      if (valuePart === '') return

      if (key === 'telegram_id' || key === 'telegramid' || key === 'tg_id') member.telegram_id = Number(valuePart)
      else if (key === 'email') member.email = valuePart
      else if (key === 'username') member.username = valuePart
      else if (key === 'name') member.name = valuePart
      else if (key === 'avatar') member.avatar = valuePart
    })

  return normalizeMember(member)
}

function normalizePayload(payload: Partial<OrganizerImportRequest>): OrganizerImportRequest {
  return {
    hackathon: {
      external_id: String(payload.hackathon?.external_id ?? ''),
      title: String(payload.hackathon?.title ?? ''),
      description: String(payload.hackathon?.description ?? ''),
      date: String(payload.hackathon?.date ?? ''),
      cover: String(payload.hackathon?.cover ?? ''),
    },
    teams: (payload.teams ?? []).map((team) => ({
      external_id: String(team.external_id ?? ''),
      name: String(team.name ?? ''),
      description: String(team.description ?? ''),
      members: (team.members ?? []).map((member) => normalizeMember(member)),
    })),
    results: (payload.results ?? []).map((result) => ({
      status: result.status ?? null,
      place: typeof result.place === 'number' ? result.place : null,
      awarded_at: result.awarded_at ?? null,
      team_external_id: result.team_external_id ?? null,
      user: result.user ? normalizeMember(result.user) : null,
    })),
  }
}

function normalizeMember(member: unknown): OrganizerMemberInput {
  const source = (member ?? {}) as Record<string, unknown>
  return {
    telegram_id: toNullableNumber(source.telegram_id),
    email: toNullableString(source.email),
    username: toNullableString(source.username),
    name: String(source.name ?? ''),
    avatar: toNullableString(source.avatar),
  }
}

function hasParticipantIdentity(member: OrganizerMemberInput | null | undefined): boolean {
  if (member == null) return false
  return typeof member.telegram_id === 'number' || (member.email ?? '').trim() !== ''
}

function parseMemberFromRow(
  row: Record<string, unknown>,
  aliases: [string[], string[], string[], string[], string[]],
): OrganizerMemberInput | null {
  const [telegramAliases, emailAliases, usernameAliases, nameAliases, avatarAliases] = aliases
  const member = normalizeMember({
    telegram_id: toNullableNumber(pickValue(row, telegramAliases)),
    email: toNullableString(pickValue(row, emailAliases)),
    username: toNullableString(pickValue(row, usernameAliases)),
    name: toNullableString(pickValue(row, nameAliases)) ?? '',
    avatar: toNullableString(pickValue(row, avatarAliases)),
  })

  return hasParticipantIdentity(member) ? member : null
}

function mergeTeams(teams: OrganizerTeamInput[]): OrganizerTeamInput[] {
  const map = new Map<string, OrganizerTeamInput>()

  teams.forEach((team) => {
    const key = team.external_id.trim()
    if (key === '') return

    const existing = map.get(key)
    if (!existing) {
      map.set(key, {
        external_id: key,
        name: team.name,
        description: team.description,
        members: [...(team.members ?? [])],
      })
      return
    }

    if ((existing.name ?? '').trim() === '' && (team.name ?? '').trim() !== '') existing.name = team.name
    if ((existing.description ?? '').trim() === '' && (team.description ?? '').trim() !== '') {
      existing.description = team.description
    }
    existing.members = [...(existing.members ?? []), ...(team.members ?? [])]
  })

  return [...map.values()]
}

function styleHeaderRow(sheet: XLSX.WorkSheet, columnCount: number): void {
  for (let col = 0; col < columnCount; col += 1) {
    const address = XLSX.utils.encode_cell({ c: col, r: 0 })
    const cell = sheet[address]
    if (!cell) continue
    ;(cell as XLSX.CellObject & { s?: unknown }).s = {
      font: { bold: true, color: { rgb: 'FFFFFFFF' } },
      fill: { patternType: 'solid', fgColor: { rgb: 'FF6B2B' } },
      alignment: { horizontal: 'center', vertical: 'center' },
    }
  }
}

function parseCsvRows(text: string): Record<string, string>[] {
  const normalized = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n')
  const rows: string[][] = []
  let cell = ''
  let row: string[] = []
  let inQuotes = false

  for (let index = 0; index < normalized.length; index += 1) {
    const char = normalized[index]
    const next = normalized[index + 1]

    if (char === '"') {
      if (inQuotes && next === '"') {
        cell += '"'
        index += 1
      } else {
        inQuotes = inQuotes === false
      }
      continue
    }

    if (char === ',' && inQuotes === false) {
      row.push(cell)
      cell = ''
      continue
    }

    if (char === '\n' && inQuotes === false) {
      row.push(cell)
      rows.push(row)
      row = []
      cell = ''
      continue
    }

    cell += char
  }

  row.push(cell)
  rows.push(row)

  const [headers, ...body] = rows
  if (headers == null || headers.every((value) => value.trim() === '')) return []

  return body
    .filter((line) => line.some((value) => value.trim() !== ''))
    .map((line) => {
      const result: Record<string, string> = {}
      headers.forEach((header, index) => {
        result[header] = line[index]?.trim() ?? ''
      })
      return result
    })
}

function readSheetRows(workbook: XLSX.WorkBook, sheetName: string): Record<string, unknown>[] {
  const sheet = workbook.Sheets[sheetName]
  if (sheet == null) return []
  return XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, { defval: '' })
}

function normalizeRecordKeys(row: Record<string, unknown>): Record<string, unknown> {
  return Object.entries(row).reduce<Record<string, unknown>>((acc, [key, value]) => {
    acc[normalizeKey(key)] = value
    return acc
  }, {})
}

function normalizeKey(value: string): string {
  return value.toLowerCase().replace(/[^a-zа-я0-9]+/gi, '_').replace(/^_+|_+$/g, '')
}

function pickValue(row: Record<string, unknown>, aliases: string[]): string {
  for (const alias of aliases.map((item) => normalizeKey(item))) {
    if (alias in row) return String(row[alias] ?? '').trim()
  }
  return ''
}

function toNullableString(value: unknown): string | null {
  const normalized = String(value ?? '').trim()
  return normalized === '' ? null : normalized
}

function toNullableNumber(value: unknown): number | null {
  const num = Number(String(value ?? '').trim())
  return Number.isFinite(num) ? num : null
}
