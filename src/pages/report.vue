<template>
  <v-container v-if="user" class="pa-0" style="background: transparent;">

    <!-- 타이틀 -->
    <div class="text-h6 font-weight-bold mb-4">
      {{ user.name }} 님의 리소스 사용 레포트
    </div>

    <!-- 날짜 필터 -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-card class="pa-3" elevation="2">
          <div class="text-caption font-weight-medium mb-1">시작일</div>
          <v-text-field
            v-model="dateRange.start"
            type="date"
            variant="outlined"
            density="comfortable"
            hide-details
            class="date-input"
          />
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card class="pa-3" elevation="2">
          <div class="text-caption font-weight-medium mb-1">종료일</div>
          <v-text-field
            v-model="dateRange.end"
            type="date"
            variant="outlined"
            density="comfortable"
            hide-details
            class="date-input"
          />
        </v-card>
      </v-col>
    </v-row>

    <!-- 사용률 추세 비교 -->
    <v-card class="pa-4 mb-4" elevation="2">
      <div class="text-subtitle-2 mb-2">
        사용률 추세 비교
        <span v-if="dateRange.start && dateRange.end">
          ({{ dateRange.start }} ~ {{ dateRange.end }})
        </span>
      </div>
      <v-row>
        <v-col cols="12" md="4">
          <div class="text-caption mb-1">CPU</div>
          <TrendBar :previous="cpuTrend[0]" :current="cpuTrend[1]" :label="trendLabel" />
        </v-col>
        <v-col cols="12" md="4">
          <div class="text-caption mb-1">GPU</div>
          <TrendBar :previous="gpuTrend[0]" :current="gpuTrend[1]" :label="trendLabel" />
        </v-col>
        <v-col cols="12" md="4">
          <div class="text-caption mb-1">MEM</div>
          <TrendBar :previous="memTrend[0]" :current="memTrend[1]" :label="trendLabel" />
        </v-col>
      </v-row>
    </v-card>

    <!-- GPU 경고 -->
    <v-alert
      type="warning"
      v-if="hasAbnormalUsage(user)"
      class="mb-4"
      prominent
      dense
    >
      ⚠️ GPU 사용률이 5일 이상 90%를 초과했습니다. 리소스 분산이 필요합니다.
    </v-alert>

    <!-- 그래프 카드 -->
    <v-row class="mb-4">
      <v-col cols="12">
        <!-- GPU 전체 그래프 -->
        <v-card class="pa-3 mb-4" elevation="2">
          <div class="text-subtitle-2 mb-1">GPU</div>
          <div class="chart-wrapper-large">
            <canvas ref="gpuCanvas" />
          </div>
        </v-card>
      </v-col>

      <!-- CPU + MEM 그래프 -->
      <v-col cols="12" md="6">
        <v-card class="pa-3" elevation="2">
          <div class="text-subtitle-2 mb-1">CPU</div>
          <div class="chart-wrapper">
            <canvas ref="cpuCanvas" />
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card class="pa-3" elevation="2">
          <div class="text-subtitle-2 mb-1">MEM</div>
          <div class="chart-wrapper">
            <canvas ref="memCanvas" />
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>


<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale } from 'chart.js'
import TrendBar from '@/components/user/TrendBar.vue'

Chart.register(LineController, LineElement, PointElement, LinearScale, Title, CategoryScale)

// === References ===
const route = useRoute()
const user = ref(null)
const cpuCanvas = ref(null)
const gpuCanvas = ref(null)
const memCanvas = ref(null)
const chartInstances = new WeakMap()
const dateRange = ref({ start: '', end: '' })

// === Utils ===
const avg = arr => (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1)
const max = arr => Math.max(...arr)
const min = arr => Math.min(...arr)

const filteredUsage = (usage, timestamps) => {
  if (!dateRange.value.start || !dateRange.value.end) return [timestamps, usage]
  const startDay = parseInt(dateRange.value.start.split('-')[2])
  const endDay = parseInt(dateRange.value.end.split('-')[2])

  const labels = []
  const values = []
  for (let i = 0; i < timestamps.length; i++) {
    const day = parseInt(timestamps[i])
    if (day >= startDay && day <= endDay) {
      labels.push(timestamps[i])
      values.push(usage[i])
    }
  }
  return [labels, values]
}

const hasAbnormalUsage = user => {
  let count = 0
  for (const val of user.gpuUsage) {
    if (val >= 90) count++
    else count = 0
    if (count >= 5) return true
  }
  return false
}

// === Trend 계산 ===
const calcTrend = (arr, type = 'dynamic') => {
  if (!arr || arr.length < 2) return [0, 0]
  const recent30 = arr.slice(-30)
  if (type === 'filtered' && dateRange.value.start && dateRange.value.end) {
    return [avg(recent30), avg(arr)]
  }
  const recent7 = arr.slice(-7)
  return [avg(recent30), avg(recent7)]
}

const cpuTrend = computed(() => {
  if (!user.value) return [0, 0]
  const recent30 = user.value.cpuUsage.slice(-30)
  const [, filtered] = filteredUsage(user.value.cpuUsage, user.value.usageTimestamps)
  return [avg(recent30), avg(filtered)]
})

const gpuTrend = computed(() => {
  if (!user.value) return [0, 0]
  const recent30 = user.value.gpuUsage.slice(-30)
  const [, filtered] = filteredUsage(user.value.gpuUsage, user.value.usageTimestamps)
  return [avg(recent30), avg(filtered)]
})

const memTrend = computed(() => {
  if (!user.value) return [0, 0]
  const recent30 = user.value.memUsage.slice(-30)
  const [, filtered] = filteredUsage(user.value.memUsage, user.value.usageTimestamps)
  return [avg(recent30), avg(filtered)]
})

const trendLabel = computed(() => {
  if (dateRange.value.start && dateRange.value.end) {
    const start = new Date(dateRange.value.start)
    const end = new Date(dateRange.value.end)
    const days = Math.floor((end - start) / (1000 * 60 * 60 * 24)) + 1
    return `${dateRange.value.start} ~ ${dateRange.value.end} (${days}일)`
  }
  return '최근 7일'
})

// === Chart Rendering ===
const renderGradientChart = async (canvas, labels, values) => {
  await nextTick()
  if (!canvas || !values) return

  const ctx = canvas.getContext('2d')
  if (chartInstances.has(canvas)) chartInstances.get(canvas).destroy()

  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: '사용률',
        data: values,
        borderWidth: 2,
        fill: false,
        tension: 0.4,
        pointRadius: 2,
        borderColor: ctx => {
          const chart = ctx.chart
          const { ctx: context, chartArea } = chart
          if (!chartArea) return '#ccc'
          const gradient = context.createLinearGradient(0, chartArea.bottom, 0, chartArea.top)
          gradient.addColorStop(0, '#12c2e9')
          gradient.addColorStop(0.5, '#f9d423')
          gradient.addColorStop(1, '#ff0033')
          return gradient
        }
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: true,
          callbacks: {
            label: ctx => {
              const value = ctx.raw
              const percent = Math.round((value / 100) * 100)
              return `사용률: ${percent}% (${value}/100)`
            }
          }
        }
      },
      scales: {
        x: {
          display: true,
          ticks: { color: '#888', font: { size: 10 } },
          grid: { display: false }
        },
        y: { display: false }
      }
    }
  })

  chartInstances.set(canvas, chart)
}

// === User 데이터 Fetch 및 Chart 렌더링 ===
const fetchUser = async () => {
  try {
    const id = route.query.id
    const res = await fetch(`http://localhost:5002/api/users/${id}/report`)
    if (!res.ok) {
      const err = await res.text()
      throw new Error(`서버 오류: ${res.status} - ${err}`)
    }
    const data = await res.json()
    user.value = {
      gpuUsage: data.gpu || [],
      cpuUsage: data.cpu || [],
      memUsage: data.mem || [],
      usageTimestamps: data.timestamps || []
    }
  } catch (err) {
    console.error('사용자 정보 로딩 실패:', err)
    user.value = null
  }
}

// === 공통 업데이트 함수 ===
const updateAllCharts = async () => {
  if (!user.value) return
  await nextTick()
  const [cpuLabels, cpuValues] = filteredUsage(user.value.cpuUsage, user.value.usageTimestamps)
  const [gpuLabels, gpuValues] = filteredUsage(user.value.gpuUsage, user.value.usageTimestamps)
  const [memLabels, memValues] = filteredUsage(user.value.memUsage, user.value.usageTimestamps)

  renderGradientChart(cpuCanvas.value, cpuLabels, cpuValues)
  renderGradientChart(gpuCanvas.value, gpuLabels, gpuValues)
  renderGradientChart(memCanvas.value, memLabels, memValues)
}

// === Watchers ===
watch(user, updateAllCharts)
watch(dateRange, updateAllCharts, { deep: true })

// === Init ===
onMounted(fetchUser)
</script>


<style scoped>
/* 레이아웃: 그래프 행 */
.chart-row {
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 12px;
}

/* 공통 그래프 wrapper */
.chart-wrapper,
.chart-wrapper-large {
  position: relative;
  width: 100%;
}

.chart-wrapper {
  height: 120px;
}
.chart-wrapper-large {
  height: 180px;
}

/* 높이 variation 클래스 */
.chart-wrapper.tall {
  height: 200px;
}
.chart-wrapper.big {
  height: 220px;
}
.chart-wrapper.huge {
  height: 320px;
}

/* 그래프 캔버스 공통 스타일 */
.chart-wrapper canvas,
.chart-wrapper-large canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}

/* 그래프 내부 설명 텍스트 (좌상단) */
.chart-wrapper small,
.chart-wrapper-large small {
  position: absolute;
  top: 6px;
  left: 8px;
  font-size: 12px;
  color: #888;
}

/* 섹션 제목용 클래스 */
.chart-section-title {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 12px;
}

/* 카드 배경 제거용 (타이틀 카드 등에서 사용) */
::v-deep(.nobg-card) {
  background-color: transparent !important;
  box-shadow: none !important;
}

/* 날짜 입력 칸 스타일 조정 */
.date-input input {
  height: 36px;
  padding: 4px 8px;
  font-size: 14px;
}
</style>
