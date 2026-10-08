<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <button @click="$router.back()" class="text-sm text-gray-500 hover:text-blue-600 mb-4 flex items-center gap-1">
      ← Назад
    </button>

    <div v-if="loading" class="text-center text-gray-400 py-12">Загрузка...</div>

    <template v-else-if="profession">
      <div class="card mb-6">
        <div class="flex items-start justify-between mb-3">
          <h1 class="text-2xl font-bold">{{ profession.name }}</h1>
          <span class="text-yellow-500 text-lg ml-3">{{ '★'.repeat(profession.demand_level) }}</span>
        </div>
        <span class="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-full">{{ profession.category }}</span>

        <p class="text-gray-600 mt-4 leading-relaxed">{{ profession.description }}</p>

        <div v-if="profession.avg_salary" class="mt-4 p-3 bg-gray-50 rounded-lg">
          <span class="text-sm text-gray-500">Средняя зарплата</span>
          <div class="text-xl font-bold text-green-600 mt-1">
            {{ formatSalary(profession.avg_salary) }} ₽ / мес
          </div>
        </div>
      </div>

      <!-- Профиль Холланда -->
      <div v-if="profession.holland_weights" class="card">
        <h2 class="font-semibold mb-4">Профиль по Холланду</h2>
        <div class="space-y-2">
          <div v-for="(label, key) in hollandLabels" :key="key">
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-600">{{ label }}</span>
              <span class="text-gray-500">{{ profession.holland_weights[key] }}/5</span>
            </div>
            <div class="bg-gray-100 rounded-full h-2">
              <div
                class="bg-blue-500 h-2 rounded-full"
                :style="{ width: (profession.holland_weights[key] / 5 * 100) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Где учиться -->
      <div v-if="profession.universities?.length" class="card mt-6">
        <h2 class="font-semibold mb-3">Где учиться</h2>
        <ul class="space-y-2">
          <li
            v-for="uni in profession.universities" :key="uni"
            class="flex items-center gap-2 text-gray-700"
          >
            <span class="text-blue-500 text-lg leading-none">•</span>
            {{ uni }}
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const profession = ref(null)
const loading = ref(true)

const hollandLabels = {
  weight_realistic: 'Реалистичный (практик)',
  weight_investigative: 'Исследовательский (аналитик)',
  weight_artistic: 'Артистичный (творец)',
  weight_social: 'Социальный (помощник)',
  weight_enterprising: 'Предпринимательский (лидер)',
  weight_conventional: 'Конвенциональный (организатор)',
}

function formatSalary(val) {
  return Number(val).toLocaleString('ru-RU')
}

onMounted(async () => {
  const { data } = await api.get(`/careers/${route.params.id}/`)
  profession.value = data
  loading.value = false
})
</script>
