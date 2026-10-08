<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-10">
    <div class="card w-full max-w-md">
      <h1 class="text-2xl font-bold mb-6 text-center">Регистрация</h1>

      <!-- Выбор роли -->
      <div class="flex gap-2 mb-6">
        <button
          v-for="r in roles" :key="r.value"
          @click="role = r.value"
          :class="['flex-1 py-2 rounded-lg text-sm font-medium border transition',
            role === r.value ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 text-gray-600 hover:border-blue-400']"
        >{{ r.label }}</button>
      </div>

      <form @submit.prevent="submit" class="space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Имя</label>
            <input v-model="form.first_name" type="text" class="input-field" required />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Фамилия</label>
            <input v-model="form.last_name" type="text" class="input-field" required />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input v-model="form.email" type="email" class="input-field" required />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
          <input v-model="form.password" type="password" class="input-field" required minlength="6" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Школа</label>
          <select v-model="form.school_id" class="input-field">
            <option value="">— не указана —</option>
            <option v-for="s in schools" :key="s.school_id" :value="s.school_id">
              {{ s.name }}{{ s.city ? ` (${s.city})` : '' }}
            </option>
          </select>
        </div>

        <template v-if="role === 'student'">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Класс</label>
            <select v-model="form.grade" class="input-field">
              <option value="">— не указан —</option>
              <option v-for="g in 11" :key="g" :value="g">{{ g }} класс</option>
            </select>
          </div>
        </template>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

        <button type="submit" class="btn-primary w-full mt-2" :disabled="loading">
          {{ loading ? 'Регистрирую...' : 'Зарегистрироваться' }}
        </button>
      </form>

      <p class="text-center text-sm text-gray-500 mt-4">
        Уже есть аккаунт?
        <router-link to="/auth/login" class="text-blue-600 hover:underline">Войти</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const authStore = useAuthStore()
const router = useRouter()

const role = ref('student')
const roles = [
  { value: 'student', label: 'Учащийся' },
  { value: 'teacher', label: 'Учитель' },
]

const schools = ref([])

const form = ref({
  email: '', password: '',
  first_name: '', last_name: '',
  grade: '',
  school_id: '',
})

const error = ref('')
const loading = ref(false)

onMounted(async () => {
  try {
    const { data } = await api.get('/schools/')
    schools.value = data.results || data
  } catch {
    schools.value = []
  }
})

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const payload = { ...form.value }
    if (!payload.school_id) delete payload.school_id
    if (role.value === 'student') {
      if (!payload.grade) delete payload.grade
      await authStore.registerStudent(payload)
    } else {
      delete payload.grade
      await authStore.registerTeacher(payload)
    }
    await authStore.login(form.value.email, form.value.password)
    router.push('/dashboard')
  } catch (e) {
    const data = e.response?.data
    error.value = data
      ? Object.values(data).flat().join(' ')
      : 'Ошибка регистрации.'
  } finally {
    loading.value = false
  }
}
</script>
