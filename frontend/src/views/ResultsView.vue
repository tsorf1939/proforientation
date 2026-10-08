<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">Результаты теста</h1>

    <div v-if="loading" class="text-center text-gray-400 py-12">Загрузка результатов...</div>

    <template v-else>
      <!-- Статус -->
      <div class="card mb-6">
        <div class="flex items-center justify-between">
          <div>
            <div class="font-semibold text-lg">{{ result?.test?.name }}</div>
            <div class="text-sm text-gray-400 mt-1">{{ formatDate(result?.start_date) }}</div>
          </div>
          <span class="bg-green-100 text-green-700 text-sm px-3 py-1 rounded-full">Завершён</span>
        </div>
      </div>

      <!-- ===== КЛИМОВ ===== -->
      <template v-if="testType === 'klimov'">
        <div class="card mb-6 border-l-4 border-blue-500">
          <h2 class="text-lg font-semibold mb-3">Ваш тип по Климову</h2>
          <div class="text-3xl font-bold mb-2" :style="{ color: '#2E4B8F' }">{{ klimovDominant.label }}</div>
          <p class="text-gray-600 text-sm">{{ klimovDominant.description }}</p>
        </div>

        <h3 class="text-base font-semibold mb-3 text-gray-700">Профиль баллов</h3>
        <div class="card mb-6 space-y-2">
          <div v-for="(score, key) in klimovScoreDisplay" :key="key" class="flex items-center gap-3">
            <div class="w-40 text-sm text-gray-600 shrink-0">{{ score.label }}</div>
            <div class="flex-1 bg-gray-100 rounded-full h-3">
              <div class="h-3 rounded-full bg-blue-500 transition-all" :style="{ width: score.pct + '%' }"></div>
            </div>
            <div class="w-8 text-right text-sm font-semibold">{{ score.value }}</div>
          </div>
        </div>

        <h3 class="text-base font-semibold mb-3 text-gray-700">Рекомендованные профессии</h3>
        <div v-if="recommendations.length === 0" class="card text-center text-gray-400 py-8">
          Рекомендации ещё формируются, попробуйте обновить страницу через несколько секунд.
          <button @click="loadRecommendations" class="block mx-auto mt-3 text-blue-600 hover:underline text-sm">Обновить</button>
        </div>
        <div v-else class="space-y-3 mb-6">
          <div
            v-for="(rec, i) in recommendations" :key="rec.recommendation_id"
            class="card hover:shadow-md transition cursor-pointer"
            @click="$router.push(`/careers/${rec.profession.profession_id}`)"
          >
            <div class="flex items-center gap-4">
              <div class="text-2xl font-bold text-gray-200 w-8 text-center">{{ i + 1 }}</div>
              <div class="flex-1">
                <div class="font-semibold">{{ rec.profession.name }}</div>
                <div class="text-sm text-gray-500">{{ rec.profession.category }}</div>
              </div>
              <div class="text-right">
                <div class="text-xl font-bold" :class="matchColor(rec.match_percentage)">{{ rec.match_percentage }}%</div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ===== ТЕМПЕРАМЕНТ ===== -->
      <template v-else-if="testType === 'temperament'">
        <div class="card mb-6 border-l-4 border-purple-500">
          <h2 class="text-lg font-semibold mb-3">Ваш тип темперамента</h2>
          <div class="text-3xl font-bold mb-2" :style="{ color: '#6B21A8' }">{{ temperamentDominant.label }}</div>
          <p class="text-gray-600 text-sm">{{ temperamentDominant.description }}</p>
        </div>

        <h3 class="text-base font-semibold mb-3 text-gray-700">Соотношение типов</h3>
        <div class="card mb-6 space-y-2">
          <div v-for="(score, key) in temperamentScoreDisplay" :key="key" class="flex items-center gap-3">
            <div class="w-36 text-sm text-gray-600 shrink-0">{{ score.label }}</div>
            <div class="flex-1 bg-gray-100 rounded-full h-3">
              <div class="h-3 rounded-full transition-all" :class="score.color" :style="{ width: score.pct + '%' }"></div>
            </div>
            <div class="w-8 text-right text-sm font-semibold">{{ score.value }}</div>
          </div>
        </div>
      </template>

      <!-- ===== БАЛЛЬНОЕ (SCORED) ===== -->
      <template v-else-if="testType === 'scored'">
        <div class="card mb-6 border-l-4 border-orange-500">
          <h2 class="text-lg font-semibold mb-3">Ваш результат</h2>
          <div v-if="!scoredHasProfile" class="text-4xl font-bold text-orange-600 mb-4">{{ totalScore }} баллов</div>
          <p v-if="result?.test?.description" class="text-gray-600 text-sm whitespace-pre-wrap">{{ result.test.description }}</p>
        </div>
        <div v-if="scoredHasProfile" class="card mb-6 space-y-2">
          <h3 class="text-base font-semibold text-gray-700 mb-3">Профиль типов</h3>
          <div v-for="s in scoredProfileDisplay" :key="s.key" class="flex items-center gap-3">
            <div class="w-52 text-sm text-gray-600 shrink-0">{{ s.label }}</div>
            <div class="flex-1 bg-gray-100 rounded-full h-3">
              <div class="h-3 rounded-full bg-orange-500 transition-all" :style="{ width: s.pct + '%' }"></div>
            </div>
            <div class="w-8 text-right text-sm font-semibold">{{ s.value }}</div>
          </div>
        </div>
      </template>

      <!-- ===== РЕФЛЕКСИЯ (REFLECTION) ===== -->
      <template v-else-if="testType === 'reflection'">
        <div class="card mb-6 border-l-4 border-teal-500">
          <h2 class="text-lg font-semibold mb-2">Задание выполнено!</h2>
          <p class="text-gray-600 text-sm">Ваши ответы сохранены.</p>
        </div>
        <div v-if="textAnswers.length" class="space-y-4 mb-6">
          <div v-for="(a, i) in textAnswers" :key="i" class="card">
            <p class="text-sm font-medium text-gray-700 mb-2">{{ a.question_text }}</p>
            <p class="text-gray-900 whitespace-pre-wrap">{{ a.answer_text || '—' }}</p>
          </div>
        </div>
      </template>

      <!-- ===== КАРЬЕРА (default) ===== -->
      <template v-else>
        <h2 class="text-lg font-semibold mb-4">Рекомендованные профессии</h2>

        <div v-if="recommendations.length === 0" class="card text-center text-gray-400 py-8">
          Рекомендации ещё формируются, попробуйте обновить страницу через несколько секунд.
          <button @click="loadRecommendations" class="block mx-auto mt-3 text-blue-600 hover:underline text-sm">Обновить</button>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="(rec, i) in recommendations" :key="rec.recommendation_id"
            class="card hover:shadow-md transition cursor-pointer"
            @click="$router.push(`/careers/${rec.profession.profession_id}`)"
          >
            <div class="flex items-center gap-4">
              <div class="text-3xl font-bold text-gray-200 w-10 text-center">{{ i + 1 }}</div>
              <div class="flex-1">
                <div class="font-semibold text-lg">{{ rec.profession.name }}</div>
                <div class="text-sm text-gray-500">{{ rec.profession.category }}</div>
              </div>
              <div class="text-right">
                <div class="text-2xl font-bold" :class="matchColor(rec.match_percentage)">
                  {{ rec.match_percentage }}%
                </div>
                <div class="text-xs mt-1 px-2 py-0.5 rounded-full" :class="levelClass(rec.recommendation_level)">
                  {{ rec.level_label }}
                </div>
              </div>
            </div>

            <div class="mt-3 bg-gray-100 rounded-full h-2">
              <div
                class="h-2 rounded-full transition-all"
                :class="rec.recommendation_level === 1 ? 'bg-green-500' : rec.recommendation_level === 2 ? 'bg-yellow-400' : 'bg-red-400'"
                :style="{ width: rec.match_percentage + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </template>

      <div class="mt-8 flex gap-3">
        <router-link to="/careers" class="btn-secondary">Каталог профессий</router-link>
        <router-link to="/tests" class="btn-primary">Пройти ещё тест</router-link>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const result = ref(null)
const recommendations = ref([])
const scores = ref(null)
const textAnswers = ref([])
const loading = ref(true)

const testType = computed(() => result.value?.test?.test_type || 'career')
const totalScore = computed(() => scores.value?.people ?? 0)

const SCORED_DIMENSION_LABELS = {
  people: 'Предметно-действенное',
  intellectual: 'Абстрактно-символическое',
  practical: 'Словесно-логическое',
  aesthetic: 'Наглядно-образное',
  physical: 'Креативность',
}

const SCORED_LABELS_BY_TASK = {
  10: {
    people: 'Экстраверсия',
    intellectual: 'Нейротизм',
    aesthetic: 'Искренность (шкала лжи)',
  },
  14: {
    practical: 'Реалистичный тип',
    intellectual: 'Интеллектуальный тип',
    people: 'Социальный тип',
    administrative: 'Конвенциональный тип',
    physical: 'Предприимчивый тип',
    aesthetic: 'Художественный тип',
  },
  15: {
    people: 'Работа с людьми',
    intellectual: 'Умственный труд',
    practical: 'Практическая деятельность',
    aesthetic: 'Эстетика и искусство',
    physical: 'Подвижная деятельность',
    administrative: 'Планово-экономическая деятельность',
  },
  17: {
    people: 'Престиж',
    practical: 'Материальное благополучие',
    intellectual: 'Творческая деятельность',
  },
}

const scoredDimensionLabels = computed(() => {
  const taskNum = result.value?.test?.task_number
  return SCORED_LABELS_BY_TASK[taskNum] || SCORED_DIMENSION_LABELS
})

const scoredHasProfile = computed(() => {
  if (!scores.value) return false
  const keys = ['people', 'intellectual', 'practical', 'aesthetic', 'physical', 'administrative']
  return keys.filter(k => scores.value[k] > 0).length > 1
})

const scoredProfileDisplay = computed(() => {
  if (!scores.value) return []
  const keys = ['people', 'intellectual', 'practical', 'aesthetic', 'physical', 'administrative']
  const nonZero = keys.filter(k => scores.value[k] > 0)
  const max = Math.max(...nonZero.map(k => scores.value[k]), 1)
  return nonZero.map(k => ({
    key: k,
    label: scoredDimensionLabels.value[k] || k,
    value: scores.value[k],
    pct: Math.round((scores.value[k] / max) * 100),
  }))
})

// ── Климов ──────────────────────────────────────────────────────────────────

const KLIMOV_TYPES = {
  people:       { label: 'Человек — Человек (Ч-Ч)', description: 'Вы склонны к деятельности, связанной с воспитанием, обучением, обслуживанием и помощью людям. Профессии: учитель, психолог, врач, социальный работник.' },
  intellectual: { label: 'Человек — Знаковые системы (Ч-З)', description: 'Вы предпочитаете работу с числами, формулами, текстами и кодом. Профессии: программист, экономист, бухгалтер, переводчик.' },
  practical:    { label: 'Человек — Техника (Ч-Т)', description: 'Вас привлекает работа с машинами, приборами и техническими системами. Профессии: инженер, механик, электрик, технолог.' },
  aesthetic:    { label: 'Человек — Художественный образ (Ч-Х)', description: 'Вы тяготеете к художественной деятельности, дизайну и творчеству. Профессии: художник, дизайнер, актёр, архитектор.' },
  physical:     { label: 'Человек — Природа (Ч-П)', description: 'Вам близка работа с живой и неживой природой. Профессии: биолог, ветеринар, агроном, эколог.' },
}

const klimovDominant = computed(() => {
  if (!scores.value) return { label: '—', description: '' }
  const s = scores.value
  const keys = ['people', 'intellectual', 'practical', 'aesthetic', 'physical']
  const top = keys.reduce((a, b) => (s[a] >= s[b] ? a : b))
  return KLIMOV_TYPES[top] || { label: '—', description: '' }
})

const klimovScoreDisplay = computed(() => {
  if (!scores.value) return []
  const s = scores.value
  const keys = ['people', 'intellectual', 'practical', 'aesthetic', 'physical']
  const max = Math.max(...keys.map(k => s[k]), 1)
  return keys.map(k => ({
    key: k,
    label: KLIMOV_TYPES[k]?.label.split(' (')[0] || k,
    value: s[k],
    pct: Math.round((s[k] / max) * 100),
  }))
})

// ── Темперамент ──────────────────────────────────────────────────────────────

const TEMPERAMENT_TYPES = {
  people:       { label: 'Холерик', description: 'Энергичный, решительный, вспыльчивый. Быстро включается в работу, горит идеями, но может терять терпение и не доводить начатое до конца. Силён в кризисных ситуациях, требующих стремительных решений.', color: 'bg-red-500' },
  intellectual: { label: 'Сангвиник', description: 'Жизнерадостный, общительный, гибкий. Легко адаптируется к новым условиям, быстро переключается между задачами. Хорош в работе с людьми и в динамичной обстановке.', color: 'bg-yellow-400' },
  practical:    { label: 'Флегматик', description: 'Спокойный, методичный, надёжный. Медленно раскачивается, но доводит дело до конца. Отличается высокой устойчивостью к стрессу, хорошо справляется с монотонной, детальной работой.', color: 'bg-green-500' },
  aesthetic:    { label: 'Меланхолик', description: 'Чувствительный, глубокий, вдумчивый. Богатый внутренний мир, склонность к анализу и рефлексии. Хорошо проявляет себя в творческой, аналитической и индивидуальной работе.', color: 'bg-blue-400' },
}

const temperamentDominant = computed(() => {
  if (!scores.value) return { label: '—', description: '' }
  const s = scores.value
  const keys = ['people', 'intellectual', 'practical', 'aesthetic']
  const top = keys.reduce((a, b) => (s[a] >= s[b] ? a : b))
  return TEMPERAMENT_TYPES[top] || { label: '—', description: '' }
})

const temperamentScoreDisplay = computed(() => {
  if (!scores.value) return []
  const s = scores.value
  const keys = ['people', 'intellectual', 'practical', 'aesthetic']
  const max = Math.max(...keys.map(k => s[k]), 1)
  return keys.map(k => ({
    key: k,
    label: TEMPERAMENT_TYPES[k]?.label || k,
    value: s[k],
    pct: Math.round((s[k] / max) * 100),
    color: TEMPERAMENT_TYPES[k]?.color || 'bg-gray-400',
  }))
})

// ── Утилиты ──────────────────────────────────────────────────────────────────

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

function matchColor(pct) {
  if (pct >= 70) return 'text-green-600'
  if (pct >= 40) return 'text-yellow-600'
  return 'text-red-500'
}

function levelClass(level) {
  if (level === 1) return 'bg-green-100 text-green-700'
  if (level === 2) return 'bg-yellow-100 text-yellow-700'
  return 'bg-red-100 text-red-700'
}

async function loadRecommendations() {
  const { data } = await api.get(`/results/${route.params.resultId}/recommendations/`)
  recommendations.value = data.results || data
}

onMounted(async () => {
  const { data: resultData } = await api.get(`/results/${route.params.resultId}/`)
  result.value = resultData
  const type = resultData.test?.test_type

  if (type === 'reflection') {
    const { data: answersData } = await api.get(`/results/${route.params.resultId}/answers/`)
    textAnswers.value = answersData.answers || []
  } else {
    const { data: scoresData } = await api.get(`/results/${route.params.resultId}/scores/`)
    scores.value = scoresData.scores
    if (type === 'career' || type === 'klimov') {
      await loadRecommendations()
    }
  }

  loading.value = false
})
</script>
