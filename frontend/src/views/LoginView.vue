<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="card w-full max-w-sm">
      <h1 class="text-2xl font-bold mb-6 text-center">Вход</h1>

      <form @submit.prevent="submit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input v-model="form.email" type="email" class="input-field" required />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
          <input v-model="form.password" type="password" class="input-field" required />
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? 'Вхожу...' : 'Войти' }}
        </button>
      </form>

      <p class="text-center text-sm text-gray-500 mt-4">
        Нет аккаунта?
        <router-link to="/auth/register" class="text-blue-600 hover:underline">Зарегистрироваться</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const form = ref({ email: '', password: '' })
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(form.value.email, form.value.password)
    router.push('/dashboard')
  } catch {
    error.value = 'Неверный email или пароль.'
  } finally {
    loading.value = false
  }
}
</script>
