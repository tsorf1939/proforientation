<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">Каталог профессий</h1>

    <!-- Фильтры -->
    <div class="card mb-6 flex flex-wrap gap-3 items-end">
      <div class="flex-1 min-w-48">
        <label class="block text-sm font-medium text-gray-700 mb-1">Поиск</label>
        <input v-model="search" @input="debouncedLoad" type="text" placeholder="Программист..." class="input-field" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Сфера</label>
        <select v-model="filters.category" @change="loadCareers" class="input-field min-w-36">
          <option value="">Все</option>
          <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Востребованность</label>
        <select v-model="filters.demand_level" @change="loadCareers" class="input-field">
          <option value="">Любая</option>
          <option v-for="n in 5" :key="n" :value="n">{{ '★'.repeat(n) }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="text-center text-gray-400 py-12">Загрузка...</div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="p in professions" :key="p.profession_id"
        class="card hover:shadow-md transition cursor-pointer"
        @click="$router.push(`/careers/${p.profession_id}`)"
      >
        <div class="flex items-start justify-between mb-2">
          <h3 class="font-semibold">{{ p.name }}</h3>
          <span class="text-yellow-500 text-sm ml-2 shrink-0">{{ '★'.repeat(p.demand_level) }}</span>
        </div>
        <span class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">{{ p.category }}</span>
        <div v-if="p.avg_salary" class="text-sm text-gray-500 mt-2">
          от {{ formatSalary(p.avg_salary) }} ₽/мес
        </div>
      </div>
    </div>

    <div v-if="!loading && professions.length === 0" class="text-center text-gray-400 py-12">
      Профессии не найдены.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const professions = ref([])
const loading = ref(true)
const search = ref('')
const filters = ref({ category: '', demand_level: '' })
const categories = ['IT', 'Медицина', 'Образование', 'Инженерия', 'Искусство', 'Психология', 'Право', 'Экономика', 'Медиа', 'Наука', 'Строительство', 'Сервис', 'Бизнес']

let debounceTimer = null
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadCareers, 400)
}

function formatSalary(val) {
  return Number(val).toLocaleString('ru-RU')
}

async function loadCareers() {
  loading.value = true
  const params = {}
  if (search.value) params.search = search.value
  if (filters.value.category) params.category = filters.value.category
  if (filters.value.demand_level) params.demand_level = filters.value.demand_level

  const { data } = await api.get('/careers/', { params })
  professions.value = data.results || data
  loading.value = false
}

onMounted(loadCareers)
</script>
