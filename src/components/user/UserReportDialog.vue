<template>
  <v-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    max-width="900"
    persistent
  >
    <v-card>
      <v-card-title>{{ user.name }} 님의 리소스 사용 레포트</v-card-title>
      <v-card-text>
        <div v-if="user">
        <!-- 추세 분석 카드 -->
        <v-card variant="outlined" class="pa-4 mb-4">
          <div class="text-subtitle-2 mb-2">사용률 추세 비교 (이전 7일 vs 최근 7일)</div>
          <v-row>
            <v-col cols="4">
              <div class="text-caption mb-1">CPU</div>
              <trend-bar :previous="cpuTrend[0]" :current="cpuTrend[1]" />
            </v-col>
            <v-col cols="4">
              <div class="text-caption mb-1">GPU</div>
              <trend-bar :previous="gpuTrend[0]" :current="gpuTrend[1]" />
            </v-col>
            <v-col cols="4">
              <div class="text-caption mb-1">MEM</div>
              <trend-bar :previous="memTrend[0]" :current="memTrend[1]" />
            </v-col>
          </v-row>
        </v-card>

          <!-- 평균 요약 -->
          <v-row class="mb-4">
            <!-- 평균/최소/최대 사용률 카드 -->
            <v-col cols="4">
              <v-card variant="outlined" class="pa-3">
                <div class="text-subtitle-2">CPU 사용률</div>
                <div class="text-body-2">평균: {{ avg(user.cpuUsage) }}%</div>
                <div class="text-body-2">최대: {{ max(user.cpuUsage) }}%</div>
                <div class="text-body-2">최소: {{ min(user.cpuUsage) }}%</div>
              </v-card>
            </v-col>
            <!-- 평균/최소/최대 사용률 카드 -->
            <v-col cols="4">
              <v-card variant="outlined" class="pa-3">
                <div class="text-subtitle-2">GPU 사용률</div>
                <div class="text-body-2">평균: {{ avg(user.gpuUsage) }}%</div>
                <div class="text-body-2">최대: {{ max(user.gpuUsage) }}%</div>
                <div class="text-body-2">최소: {{ min(user.gpuUsage) }}%</div>
              </v-card>
            </v-col>
            <!-- 평균/최소/최대 사용률 카드 -->
            <v-col cols="4">
              <v-card variant="outlined" class="pa-3">
                <div class="text-subtitle-2">MEM 사용률</div>
                <div class="text-body-2">평균: {{ avg(user.memUsage) }}%</div>
                <div class="text-body-2">최대: {{ max(user.memUsage) }}%</div>
                <div class="text-body-2">최소: {{ min(user.memUsage) }}%</div>
              </v-card>
            </v-col>
          </v-row>
          <!-- 경고 메시지 -->
          <v-alert
            type="warning"
            v-if="hasAbnormalUsage(user)"
            class="mb-4"
            prominent
            dense
          >
            ⚠️ GPU 사용률이 5일 이상 90%를 초과했습니다. 리소스 분산이 필요합니다.
          </v-alert>

          <!-- 차트 -->
          <div class="chart-row">
            <div class="chart-wrapper">
              <canvas ref="cpuCanvas" />
              <small>CPU</small>
            </div>
            <div class="chart-wrapper">
              <canvas ref="gpuCanvas" />
              <small>GPU</small>
            </div>
            <div class="chart-wrapper">
              <canvas ref="memCanvas" />
              <small>MEM</small>
            </div>
          </div>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="emit('update:visible', false)">닫기</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { onMounted, watch, nextTick, ref, computed } from 'vue'
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale } from 'chart.js'

Chart.register(LineController, LineElement, PointElement, LinearScale, Title, CategoryScale)

const props = defineProps({
  visible: Boolean,
  user: Object
})
const emit = defineEmits(['update:visible'])

const cpuCanvas = ref(null)
const gpuCanvas = ref(null)
const memCanvas = ref(null)
const chartInstances = new WeakMap()

const avg = (arr) => (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1)
const max = (arr) => Math.max(...arr)
const min = (arr) => Math.min(...arr)
const hasAbnormalUsage = (user) => {
  if (!user?.gpuUsage) return false
  let overCount = 0
  for (let val of user.gpuUsage) {
    if (val >= 90) overCount++
    else overCount = 0
    if (overCount >= 5) return true
  }
  return false
}

const calcTrend = (arr) => {
  if (!arr || arr.length < 14) return [0, 0]
  const prev7 = arr.slice(-14, -7)
  const recent7 = arr.slice(-7)
  return [avg(prev7), avg(recent7)]
}

const cpuTrend = computed(() => calcTrend(props.user?.cpuUsage))
const gpuTrend = computed(() => calcTrend(props.user?.gpuUsage))
const memTrend = computed(() => calcTrend(props.user?.memUsage))


const renderGradientChart = async (canvas, labels, values) => {
  await nextTick()
  if (!canvas || !values) return
  const ctx = canvas.getContext('2d')
  if (chartInstances.has(canvas)) {
    chartInstances.get(canvas).destroy()
  }
  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: '사용률',
          data: values,
          borderWidth: 2,
          fill: false,
          tension: 0.4,
          pointRadius: 0,
          borderColor: (ctx) => {
            const chart = ctx.chart
            const { ctx: context, chartArea } = chart
            if (!chartArea) return '#ccc'
            const gradient = context.createLinearGradient(0, chartArea.bottom, 0, chartArea.top)
            gradient.addColorStop(0, '#12c2e9')
            gradient.addColorStop(0.5, '#f9d423')
            gradient.addColorStop(1, '#ff0033')
            return gradient
          }
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales: {
        x: { display: true, ticks: { color: '#888', font: { size: 10 } }, grid: { display: false } },
        y: { display: false }
      }
    }
  })
  chartInstances.set(canvas, chart)
}

watch(
  () => props.visible,
  async (val) => {
    if (val && props.user) {
      await nextTick()
      renderGradientChart(cpuCanvas.value, props.user.usageTimestamps, props.user.cpuUsage)
      renderGradientChart(gpuCanvas.value, props.user.usageTimestamps, props.user.gpuUsage)
      renderGradientChart(memCanvas.value, props.user.usageTimestamps, props.user.memUsage)
    }
  }
)
</script>

<style scoped>
.chart-row {
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 12px;
}
.chart-wrapper {
  flex: 1;
  height: 100px;
  position: relative;
}
.chart-wrapper canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}
.chart-wrapper small {
  position: absolute;
  top: 4px;
  left: 6px;
  font-size: 11px;
  color: #aaa;
}
</style>
