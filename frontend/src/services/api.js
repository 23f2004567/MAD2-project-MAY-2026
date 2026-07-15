/**
 * services/api.js — Central Axios instance for all API communication.
 *
 * - Base URL points to the Flask backend.
 * - JWT token is injected automatically into every request via an interceptor.
 * - 401 responses auto-redirect to /login (token expired / invalid).
 */

import axios from 'axios'
import router from '../router/index.js'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('pp_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: handle 401 globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('pp_token')
      localStorage.removeItem('pp_user')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default api
