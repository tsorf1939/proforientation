<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
    <div v-if="loading" class="text-center text-gray-400 py-16">Загрузка теста...</div>

    <!-- Тест уже пройден -->
    <div v-else-if="existingResult" class="card text-center py-10">
      <div class="text-5xl mb-4">✅</div>
      <h2 class="text-xl font-bold mb-2">Вы уже прошли этот тест</h2>
      <p class="text-gray-500 mb-6">Хотите посмотреть результат или пройти заново?</p>
      <div class="flex gap-3 justify-center flex-wrap">
        <router-link :to="`/results/${existingResult.result_id}`" class="btn-primary">
          Посмотреть результат
        </router-link>
        <button @click="retake" class="btn-secondary" :disabled="retaking">
          {{ retaking ? 'Подготовка...' : 'Пройти заново' }}
        </button>
      </div>
    </div>

    <template v-else-if="test">
      <!-- Прогресс-бар -->
      <div class="mb-6">
        <div class="flex justify-between text-sm text-gray-500 mb-1">
          <span>Вопрос {{ currentIndex + 1 }} из {{ test.questions.length }}</span>
          <span>{{ Math.round(progress) }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <!-- Вопрос -->
      <div class="card mb-6">
        <h2 class="text-lg font-semibold mb-6">{{ currentQuestion.question_text }}</h2>

        <!-- Текстовый ввод -->
        <div v-if="currentQuestion.question_type === 'text_input'">
          <textarea
            v-model="textAnswer"
            class="w-full p-3 border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 resize-none"
            rows="5"
            placeholder="Введите ваш ответ..."
          ></textarea>
        </div>

        <!-- Одиночный выбор -->
        <div v-else class="space-y-3">
          <label
            v-for="option in currentQuestion.options" :key="option.option_id"
            :class="['flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition',
              selectedOption === option.option_id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-blue-300']"
          >
            <input
              type="radio"
              :value="option.option_id"
              v-model="selectedOption"
              class="text-blue-600"
            />
            <span class="text-gray-800">{{ option.option_text }}</span>
          </label>
        </div>
      </div>

      <p v-if="error" class="text-red-500 text-sm mb-3">{{ error }}</p>

      <div class="flex justify-between">
        <button
          v-if="currentIndex > 0"
          @click="prev"
          class="btn-secondary"
        >Назад</button>
        <div v-else></div>

        <button
          @click="next"
          class="btn-primary"
          :disabled="!canProceed || submitting"
        >
          {{ submitting ? 'Сохраняю...' : currentIndex === test.questions.length - 1 ? 'Завершить' : 'Далее' }}
        </button>
      </div>
    </template>

    <!-- Завершён -->
    <div v-else-if="completed" class="card text-center py-10">
      <div class="text-5xl mb-4">🎉</div>
      <h2 class="text-xl font-bold mb-2">Тест завершён!</h2>
      <p class="text-gray-500 mb-6">Ваши ответы сохранены.</p>
      <router-link :to="`/results/${resultId}`" class="btn-primary">
        Посмотреть результаты
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const test = ref(null)
const loading = ref(true)
const existingResult = ref(null)
const retaking = ref(false)
const currentIndex = ref(0)
const selectedOption = ref(null)
const textAnswer = ref('')
const answers = ref({})
const submitting = ref(false)
const error = ref('')
const completed = ref(false)
const resultId = ref(null)

const currentQuestion = computed(() => test.value?.questions[currentIndex.value])
const progress = computed(() => test.value ? ((currentIndex.value + 1) / test.value.questions.length) * 100 : 0)

const canProceed = computed(() => {
  if (!currentQuestion.value) return false
  if (currentQuestion.value.question_type === 'text_input') return textAnswer.value.trim().length > 0
  return !!selectedOption.value
})

onMounted(async () => {
  const testId = Number(route.params.id)
  const { data: resultsData } = await api.get('/results/')
  const resultsList = resultsData.results || resultsData
  const existing = resultsList.find(r => r.test.test_id === testId && r.status === 'завершено')
  if (existing) {
    existingResult.value = existing
    loading.value = false
    return
  }
  const { data } = await api.get(`/tests/${testId}/`)
  test.value = data
  loading.value = false
})

async function retake() {
  retaking.value = true
  await api.delete(`/results/${existingResult.value.result_id}/delete/`)
  existingResult.value = null
  answers.value = {}
  currentIndex.value = 0
  selectedOption.value = null
  textAnswer.value = ''
  const { data } = await api.get(`/tests/${route.params.id}/`)
  test.value = data
  retaking.value = false
}

function prev() {
  if (currentIndex.value > 0) {
    currentIndex.value--
    const saved = answers.value[currentQuestion.value.question_id]
    if (currentQuestion.value.question_type === 'text_input') {
      textAnswer.value = saved?.answer_text || ''
    } else {
      selectedOption.value = saved?.option_id || null
    }
  }
}

async function next() {
  const q = currentQuestion.value
  if (!canProceed.value) return

  submitting.value = true
  error.value = ''

  let payload
  if (q.question_type === 'text_input') {
    payload = { question_id: q.question_id, answer_text: textAnswer.value.trim() }
    answers.value[q.question_id] = { answer_text: textAnswer.value.trim() }
  } else {
    payload = { question_id: q.question_id, option_id: selectedOption.value }
    answers.value[q.question_id] = { option_id: selectedOption.value }
  }

  try {
    const { data } = await api.post('/tests/answer/', payload)

    if (data.test_completed) {
      resultId.value = data.result_id
      completed.value = true
      test.value = null
      return
    }

    if (currentIndex.value < test.value.questions.length - 1) {
      currentIndex.value++
      const saved = answers.value[currentQuestion.value.question_id]
      if (currentQuestion.value.question_type === 'text_input') {
        textAnswer.value = saved?.answer_text || ''
      } else {
        selectedOption.value = saved?.option_id || null
      }
    }
  } catch (e) {
    const detail = e.response?.data?.detail
    if (detail && detail.includes('уже ответил')) {
      if (currentIndex.value < test.value.questions.length - 1) {
        currentIndex.value++
        const saved = answers.value[currentQuestion.value.question_id]
        if (currentQuestion.value.question_type === 'text_input') {
          textAnswer.value = saved?.answer_text || ''
        } else {
          selectedOption.value = saved?.option_id || null
        }
      }
    } else {
      error.value = detail || 'Ошибка при сохранении ответа.'
    }
  } finally {
    submitting.value = false
  }
}
</script>
