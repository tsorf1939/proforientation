<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-2">Привет, {{ authStore.user?.profile?.first_name }}!</h1>
    <p class="text-gray-500 mb-8">Твой личный кабинет профориентации</p>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="card text-center">
        <div class="text-3xl font-bold text-blue-600">{{ results.length }}</div>
        <div class="text-gray-500 text-sm mt-1">Пройдено тестов</div>
      </div>
      <div class="card text-center">
        <div class="text-3xl font-bold text-green-600">{{ completedResults }}</div>
        <div class="text-gray-500 text-sm mt-1">Завершено</div>
      </div>
      <div class="card text-center cursor-pointer hover:shadow-md transition" @click="$router.push('/tests')">
        <div class="text-3xl font-bold text-indigo-600">→</div>
        <div class="text-gray-500 text-sm mt-1">Пройти тест</div>
      </div>
    </div>

    <!-- Рекомендации профессий -->
    <div v-if="globalRecs.length > 0" class="mb-8">
      <h2 class="text-lg font-semibold mb-1">Рекомендуемые профессии</h2>
      <p class="text-sm text-gray-400 mb-3">На основе заданий 13–16 (ДДО, Холланд, Йовайша, Профпригодность)</p>
      <div class="space-y-3">
        <div
          v-for="(rec, i) in globalRecs" :key="rec.recommendation_id"
          class="card flex items-center justify-between cursor-pointer hover:shadow-md transition"
          @click="$router.push(`/careers/${rec.profession.profession_id}`)"
        >
          <div class="flex items-center gap-3">
            <span class="text-2xl font-bold text-gray-200 w-8">{{ i + 1 }}</span>
            <div>
              <div class="font-medium">{{ rec.profession.name }}</div>
              <div class="text-sm text-gray-400">{{ rec.profession.category }}</div>
            </div>
          </div>
          <div class="text-right">
            <div :class="['text-sm font-semibold', rec.match_percentage >= 70 ? 'text-green-600' : rec.match_percentage >= 40 ? 'text-yellow-600' : 'text-red-500']">
              {{ rec.match_percentage }}%
            </div>
            <div class="text-xs text-gray-400">{{ rec.level_label }}</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="results.length > 0">
      <h2 class="text-lg font-semibold mb-3">Мои результаты</h2>
      <div class="space-y-3">
        <div
          v-for="result in results" :key="result.result_id"
          class="card flex items-center justify-between cursor-pointer hover:shadow-md transition"
          @click="$router.push(`/results/${result.result_id}`)"
        >
          <div>
            <div class="font-medium">{{ result.test.name }}</div>
            <div class="text-sm text-gray-400">{{ formatDate(result.start_date) }}</div>
          </div>
          <span :class="['text-xs px-2 py-1 rounded-full', result.status === 'завершено' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700']">
            {{ result.status === 'завершено' ? 'Завершён' : 'В процессе' }}
          </span>
        </div>
      </div>
    </div>

    <div v-else class="card text-center text-gray-400 py-12">
      Вы ещё не проходили тесты.
      <router-link to="/tests" class="text-blue-600 ml-1 hover:underline">Начать</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const authStore = useAuthStore()
const results = ref([])
const globalRecs = ref([])

const completedResults = computed(() => results.value.filter(r => r.status === 'завершено').length)

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

onMounted(async () => {
  const [resultsRes, recsRes] = await Promise.all([
    api.get('/results/'),
    api.get('/recommendations/global/'),
  ])
  results.value = resultsRes.data.results || resultsRes.data
  globalRecs.value = recsRes.data.results || recsRes.data
})
</script>
