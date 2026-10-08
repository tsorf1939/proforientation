<template>
  <nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
      <router-link to="/dashboard" class="text-blue-600 font-bold text-lg">
        ПрофОриентация
      </router-link>

      <div class="flex items-center gap-4">
        <router-link to="/tests" class="text-gray-600 hover:text-blue-600 text-sm font-medium">Тесты</router-link>
        <router-link to="/careers" class="text-gray-600 hover:text-blue-600 text-sm font-medium">Профессии</router-link>
        <router-link v-if="authStore.isTeacher" to="/teacher" class="text-gray-600 hover:text-blue-600 text-sm font-medium">Отчёты</router-link>
        <button @click="logout" class="text-sm text-red-500 hover:text-red-700 font-medium">Выйти</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

function logout() {
  authStore.logout()
  router.push('/auth/login')
}
</script>
