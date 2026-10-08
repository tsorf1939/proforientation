import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', component: () => import('@/views/HomeView.vue'), meta: { public: true } },
  { path: '/auth/login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  { path: '/auth/register', component: () => import('@/views/RegisterView.vue'), meta: { public: true } },
  { path: '/dashboard', component: () => import('@/views/DashboardView.vue') },
  { path: '/tests', component: () => import('@/views/TestsView.vue') },
  { path: '/tests/:id', component: () => import('@/views/TestWizardView.vue') },
  { path: '/results/:resultId', component: () => import('@/views/ResultsView.vue') },
  { path: '/careers', component: () => import('@/views/CareersView.vue') },
  { path: '/careers/:id', component: () => import('@/views/CareerDetailView.vue') },
  { path: '/teacher', component: () => import('@/views/TeacherDashboardView.vue'), meta: { role: 'teacher' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return '/auth/login'
  }
  if (to.meta.role === 'teacher' && !auth.isTeacher) {
    return '/dashboard'
  }
})

export default router
