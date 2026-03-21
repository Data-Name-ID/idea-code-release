import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.API_BASE_URL ?? 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})
