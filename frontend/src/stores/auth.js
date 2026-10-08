import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))

  const isAuthenticated = computed(() => !!accessToken.value)
  const isStudent = computed(() => user.value?.role === 'student')
  const isTeacher = computed(() => user.value?.role === 'teacher')

  async function login(email, password) {
    const { data } = await api.post('/auth/token/', { email, password })
    accessToken.value = data.access
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    await fetchMe()
  }

  async function fetchMe() {
    const { data } = await api.get('/users/me/')
    user.value = data
  }

  function logout() {
    accessToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function initAuth() {
    if (accessToken.value) {
      try {
        await fetchMe()
      } catch {
        logout()
      }
    }
  }

  async function registerStudent(payload) {
    await api.post('/auth/register/student/', payload)
  }

  async function registerTeacher(payload) {
    await api.post('/auth/register/teacher/', payload)
  }

  return { user, accessToken, isAuthenticated, isStudent, isTeacher, login, logout, initAuth, registerStudent, registerTeacher }
})
