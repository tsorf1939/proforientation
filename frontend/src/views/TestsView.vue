<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">Тесты профориентации</h1>

    <div v-if="loading" class="text-gray-400 text-center py-12">Загрузка...</div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="test in tests" :key="test.test_id"
        class="card hover:shadow-md transition"
      >
        <div class="flex items-start justify-between mb-2">
          <h2 class="font-semibold text-lg">{{ test.name }}</h2>
          <span v-if="completedMap[test.test_id]" class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full ml-2 shrink-0">
            ✓ Пройден
          </span>
        </div>
        <p class="text-gray-500 text-sm mb-4 line-clamp-2">{{ test.description }}</p>
        <div class="flex items-center justify-between text-sm text-gray-400 mb-4">
          <span>{{ test.questions_count }} вопросов</span>
          <span v-if="test.duration_minutes">~{{ test.duration_minutes }} мин</span>
        </div>

        <div v-if="completedMap[test.test_id]" class="flex gap-2">
          <button
            @click="$router.push(`/results/${completedMap[test.test_id].result_id}`)"
            class="btn-primary flex-1 text-sm"
          >Результаты</button>
          <button
            @click="$router.push(`/tests/${test.test_id}`)"
            class="btn-secondary flex-1 text-sm"
          >Пройти заново</button>
        </div>
        <button
          v-else
          @click="$router.push(`/tests/${test.test_id}`)"
          class="btn-primary w-full"
        >Начать</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const tests = ref([])
const completedMap = ref({})
const loading = ref(true)

onMounted(async () => {
  const [testsRes, resultsRes] = await Promise.all([
    api.get('/tests/'),
    api.get('/results/'),
  ])
  tests.value = testsRes.data.results || testsRes.data
  const resultsList = resultsRes.data.results || resultsRes.data
  completedMap.value = Object.fromEntries(
    resultsList
      .filter(r => r.status === 'завершено')
      .map(r => [r.test.test_id, r])
  )
  loading.value = false
})
</script>
