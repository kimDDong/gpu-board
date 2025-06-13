<template>
  <v-card height="100%" class="pa-4" elevation="2">
    <div class="text-caption mb-2 font-weight-bold">
      GPU별 실시간 사용률 모니터링 (Smoothie Chart)
    </div>
    <canvas ref="smoothieCanvas" width="800" height="150"></canvas>
  </v-card>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { SmoothieChart, TimeSeries } from 'smoothie'
import axios from 'axios'

const API_INTERVAL = 500
const API_URL = 'http://localhost:8000/api/gpu/detail/usage'

const smoothieCanvas = ref(null)
let chart = null
let gpuSeries = []
let timer

// GPU별 구분 색상들 (개수 >6 사용시 순환)
const GPU_COLORS = [
  'rgb(244, 67, 54)',    // red
  'rgb(33, 150, 243)',   // blue
  'rgb(76, 175, 80)',    // green
  'rgb(255, 193, 7)',    // amber
  'rgb(156,39,176)',     // purple
  'rgb(255,87,34)',      // orange
  'rgb(63,81,181)',      // indigo
  'rgb(139,195,74)',     // lime-green
  'rgb(0,150,136)',      // teal
  'rgb(205,220,57)',     // lime
]

// 시리즈: {id, TimeSeries}
function makeSeriesArr(gpuArr) {
  return gpuArr.map((g, idx) => ({
    id: g.id,
    series: new TimeSeries(),
    color: GPU_COLORS[idx % GPU_COLORS.length]
  }))
}

onMounted(async () => {
  // 첫 fetch로 GPU 개수 파악 및 시리즈 생성
  let initialGpus = []
  try {
    const res = await axios.get(API_URL)
    initialGpus = res.data.gpus
    gpuSeries = makeSeriesArr(initialGpus)
  } catch (e) {
    gpuSeries = []
  }

  // 차트 생성 및 각각 TimeSeries 추가
  chart = new SmoothieChart({
    grid: { strokeStyle: '#333', fillStyle: '#000', lineWidth: 0.5, millisPerLine: 1000, verticalSections: 6 },
    labels: { fillStyle: '#333', fontSize: 14 },
    tooltip: true,
    tooltipLine: { strokeStyle: '#bbb' },
    tooltipFormatter: SmoothieChart.tooltipFormatter,
    millisPerPixel: 100,
    minValue: 0,
    maxValue: 100,
  })

  gpuSeries.forEach((s, idx) => {
    chart.addTimeSeries(s.series, {
      strokeStyle: s.color,
      fillStyle: s.color.replace('rgb', 'rgba').replace(')', ',0.2)'),
      lineWidth: 2,
      tooltipLabel: 'GPU ' + s.id + ':',
      interpolation: 'linear',
      // displayLine: true
    })
  })

  chart.streamTo(smoothieCanvas.value, 500)

  const fetch = async () => {
    try {
      const res = await axios.get(API_URL)
      const now = Date.now()
      // 시리즈와 response가 항상 같은 순서라고 가정
      for (let i = 0; i < gpuSeries.length; ++i) {
        const val = res.data.gpus[i] ? res.data.gpus[i].value : 0
        gpuSeries[i].series.append(now, val)
      }
    } catch (e) { }
  }

  fetch()
  timer = setInterval(fetch, API_INTERVAL)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
  if (chart) chart.stop()
})
</script>

<style>
div.smoothie-chart-tooltip {
  background: #444;
  padding: 1em;
  margin-top: 20px;
  font-family: consolas;
  color: white;
  font-size: 14px;
  text-shadow: 1px 1px 0px black;
  pointer-events: none;
}
</style>