<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">Панель учителя</h1>

    <!-- Вкладки -->
    <div class="flex gap-2 mb-6 flex-wrap">
      <button
        @click="tab = 'my-students'; loadMyStudents()"
        :class="tabClass('my-students')"
      >Мои ученики</button>
      <button
        @click="tab = 'stats'; loadReport()"
        :class="tabClass('stats')"
      >Статистика класса</button>
      <button
        @click="tab = 'students'; loadStudents()"
        :class="tabClass('students')"
      >Карточки учеников</button>
    </div>

    <!-- ── Вкладка: Мои ученики ───────────────────────────────────────── -->
    <template v-if="tab === 'my-students'">
      <!-- Добавление по email -->
      <div class="card mb-6">
        <h2 class="font-semibold mb-3">Добавить ученика по email</h2>
        <div class="flex gap-2">
          <input
            v-model="addEmail"
            type="email"
            placeholder="email@example.com"
            class="input-field flex-1"
            @keyup.enter="addStudent"
          />
          <button @click="addStudent" class="btn-primary shrink-0" :disabled="addLoading">
            {{ addLoading ? 'Добавляю...' : 'Добавить' }}
          </button>
        </div>
        <p v-if="addError" class="text-red-500 text-sm mt-2">{{ addError }}</p>
        <p v-if="addSuccess" class="text-green-600 text-sm mt-2">{{ addSuccess }}</p>
      </div>

      <!-- Список учеников -->
      <div v-if="myStudentsLoading" class="text-center text-gray-400 py-12">Загрузка...</div>
      <div v-else-if="myStudents.length === 0" class="card text-center text-gray-400 py-12">
        Вы ещё не добавили ни одного ученика.
      </div>
      <div v-else class="space-y-3">
        <div v-for="s in myStudents" :key="s.student_id" class="card flex items-center justify-between gap-3">
          <div>
            <div class="font-medium">{{ s.full_name }}</div>
            <div class="text-sm text-gray-400">
              {{ s.grade ? `${s.grade} класс` : 'Класс не указан' }} · {{ s.email }}
            </div>
          </div>
          <button @click="removeStudent(s.student_id)" class="text-red-400 hover:text-red-600 text-sm shrink-0">
            Удалить
          </button>
        </div>
      </div>
    </template>

    <!-- ── Вкладка: Статистика ───────────────────────────────────────── -->
    <template v-else-if="tab === 'stats'">
      <div class="card mb-6 flex gap-4 items-end flex-wrap">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Класс</label>
          <select v-model="grade" class="input-field">
            <option value="">Все классы</option>
            <option v-for="g in 11" :key="g" :value="g">{{ g }} класс</option>
          </select>
        </div>
        <button @click="loadReport" class="btn-primary">Сформировать отчёт</button>
      </div>

      <div v-if="loading" class="text-center text-gray-400 py-12">Загрузка...</div>

      <template v-else-if="report">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div class="card text-center">
            <div class="text-3xl font-bold text-blue-600">{{ report.total_students }}</div>
            <div class="text-gray-500 text-sm mt-1">Всего учащихся</div>
          </div>
          <div class="card text-center">
            <div class="text-3xl font-bold text-green-600">{{ report.students_tested }}</div>
            <div class="text-gray-500 text-sm mt-1">Прошли тест</div>
          </div>
          <div class="card text-center">
            <div class="text-3xl font-bold text-indigo-600">
              {{ report.total_students > 0 ? Math.round(report.students_tested / report.total_students * 100) : 0 }}%
            </div>
            <div class="text-gray-500 text-sm mt-1">Охват</div>
          </div>
          <div class="card text-center">
            <div class="text-3xl font-bold text-orange-500">{{ report.top_professions.length }}</div>
            <div class="text-gray-500 text-sm mt-1">Популярных профессий</div>
          </div>
        </div>

        <div class="card mb-6">
          <h2 class="font-semibold mb-4">Топ профессий по рекомендациям</h2>
          <div v-if="report.top_professions.length === 0" class="text-gray-400 text-sm">Нет данных</div>
          <div v-else class="space-y-3">
            <div v-for="(item, i) in report.top_professions" :key="i" class="flex items-center gap-3">
              <span class="text-gray-400 w-5 text-sm">{{ i + 1 }}</span>
              <span class="flex-1 text-sm font-medium">{{ item.name }}</span>
              <div class="w-32 bg-gray-100 rounded-full h-2">
                <div class="bg-blue-500 h-2 rounded-full" :style="{ width: (item.count / maxCount * 100) + '%' }"></div>
              </div>
              <span class="text-sm text-gray-500 w-8 text-right">{{ item.count }}</span>
            </div>
          </div>
        </div>

        <div v-if="Object.keys(report.holland_distribution).length > 0" class="card">
          <h2 class="font-semibold mb-4">Интересы по сферам</h2>
          <div class="space-y-2">
            <div v-for="(count, category) in report.holland_distribution" :key="category" class="flex items-center gap-3">
              <span class="text-sm text-gray-600 w-32 shrink-0">{{ category }}</span>
              <div class="flex-1 bg-gray-100 rounded-full h-3">
                <div class="bg-indigo-400 h-3 rounded-full" :style="{ width: (count / maxCategoryCount * 100) + '%' }"></div>
              </div>
              <span class="text-sm text-gray-500 w-6 text-right">{{ count }}</span>
            </div>
          </div>
        </div>
      </template>
    </template>

    <!-- ── Вкладка: Карточки учеников ───────────────────────────────── -->
    <template v-else-if="tab === 'students'">
      <div class="card mb-4 flex gap-4 items-end">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Класс</label>
          <select v-model="grade" @change="loadStudents" class="input-field">
            <option value="">Все классы</option>
            <option v-for="g in 11" :key="g" :value="g">{{ g }} класс</option>
          </select>
        </div>
      </div>

      <div v-if="studentsLoading" class="text-center text-gray-400 py-12">Загрузка...</div>
      <div v-else-if="students.length === 0" class="card text-center text-gray-400 py-12">
        Нет учеников{{ grade ? ` в ${grade} классе` : '' }}.
      </div>
      <div v-else class="space-y-3">
        <div v-for="s in students" :key="s.student_id" class="card">
          <div class="flex items-center justify-between">
            <div>
              <div class="font-medium">{{ s.full_name }}</div>
              <div class="text-sm text-gray-400">
                {{ s.grade ? `${s.grade} класс` : 'Класс не указан' }} · {{ s.email }}
              </div>
              <div class="text-sm text-gray-500 mt-1">
                Пройдено заданий: <span class="font-semibold text-gray-700">{{ s.completed_tests.length }}</span>
              </div>
              <div v-if="s.top_recommendations.length" class="text-sm text-gray-500 mt-1">
                Топ профессии:
                <span v-for="(r, i) in s.top_recommendations" :key="i" class="ml-1">
                  {{ r.name }} ({{ r.match_percentage }}%){{ i < s.top_recommendations.length - 1 ? ',' : '' }}
                </span>
              </div>
            </div>
            <button @click="openStudent(s.student_id)" class="btn-secondary text-sm shrink-0">
              Подробнее
            </button>
          </div>
        </div>
      </div>

      <!-- Детали ученика (модальное окно) -->
      <div v-if="selectedStudent" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4" @click.self="selectedStudent = null">
        <div class="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-bold">{{ selectedStudent.full_name }}</h2>
            <button @click="selectedStudent = null" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
          </div>
          <div class="text-sm text-gray-500 mb-4">
            {{ selectedStudent.grade ? `${selectedStudent.grade} класс` : 'Класс не указан' }} · {{ selectedStudent.email }}
          </div>

          <h3 class="font-semibold mb-2">Пройденные задания ({{ selectedStudent.tests.length }})</h3>
          <div v-if="selectedStudent.tests.length === 0" class="text-gray-400 text-sm mb-4">Нет завершённых тестов</div>
          <div v-else class="space-y-2 mb-6">
            <div v-for="t in selectedStudent.tests" :key="t.result_id" class="bg-gray-50 rounded-lg p-3">
              <div class="font-medium text-sm">{{ t.test_name }}</div>
              <div class="text-xs text-gray-400 mt-1">Сумма баллов: {{ t.total_score }}</div>
            </div>
          </div>

          <h3 class="font-semibold mb-2">Рекомендации профессий</h3>
          <div v-if="selectedStudent.global_recommendations.length === 0" class="text-gray-400 text-sm">
            Рекомендации появятся после прохождения заданий 12–15
          </div>
          <div v-else class="space-y-2">
            <div v-for="(r, i) in selectedStudent.global_recommendations" :key="i"
                 class="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2">
              <span class="text-sm font-medium">{{ i + 1 }}. {{ r.name }}</span>
              <span :class="['text-sm font-semibold', r.match_percentage >= 70 ? 'text-green-600' : r.match_percentage >= 40 ? 'text-yellow-600' : 'text-red-500']">
                {{ r.match_percentage }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'

const grade = ref('')
const report = ref(null)
const loading = ref(false)
const tab = ref('my-students')

const students = ref([])
const studentsLoading = ref(false)
const selectedStudent = ref(null)

const myStudents = ref([])
const myStudentsLoading = ref(false)
const addEmail = ref('')
const addLoading = ref(false)
const addError = ref('')
const addSuccess = ref('')

function tabClass(name) {
  return [
    'px-4 py-2 rounded-lg text-sm font-medium border transition',
    tab.value === name
      ? 'bg-blue-600 text-white border-blue-600'
      : 'border-gray-300 text-gray-600 hover:border-blue-400',
  ]
}

const maxCount = computed(() =>
  report.value ? Math.max(...report.value.top_professions.map(p => p.count), 1) : 1
)
const maxCategoryCount = computed(() =>
  report.value ? Math.max(...Object.values(report.value.holland_distribution), 1) : 1
)

async function loadMyStudents() {
  myStudentsLoading.value = true
  const { data } = await api.get('/teachers/my-students/')
  myStudents.value = data
  myStudentsLoading.value = false
}

async function addStudent() {
  addError.value = ''
  addSuccess.value = ''
  if (!addEmail.value) return
  addLoading.value = true
  try {
    const { data } = await api.post('/teachers/students/', { email: addEmail.value })
    myStudents.value.push(data)
    addSuccess.value = `Ученик ${data.full_name} добавлен.`
    addEmail.value = ''
  } catch (e) {
    addError.value = e.response?.data?.detail || 'Ошибка при добавлении.'
  } finally {
    addLoading.value = false
  }
}

async function removeStudent(studentId) {
  await api.delete(`/teachers/students/${studentId}/`)
  myStudents.value = myStudents.value.filter(s => s.student_id !== studentId)
}

async function loadReport() {
  loading.value = true
  const params = {}
  if (grade.value) params.grade = grade.value
  const { data } = await api.get('/reports/class/', { params })
  report.value = data
  loading.value = false
}

async function loadStudents() {
  studentsLoading.value = true
  const params = {}
  if (grade.value) params.grade = grade.value
  const { data } = await api.get('/reports/students/', { params })
  students.value = data
  studentsLoading.value = false
}

async function openStudent(studentId) {
  const { data } = await api.get(`/reports/students/${studentId}/`)
  selectedStudent.value = data
}

onMounted(() => loadMyStudents())
</script>
