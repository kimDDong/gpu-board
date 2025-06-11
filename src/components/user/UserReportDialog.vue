<template>
  <v-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    max-width="800"
    persistent
  >
    <v-card>
      <v-card-title>{{ user.name }} 님의 리소스 사용 레포트</v-card-title>
      <v-card-text>
        <div v-if="user">
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
import { onMounted, watch, nextTick, ref } from 'vue'
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