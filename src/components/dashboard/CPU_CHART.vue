<template>
  <v-card height="100%" class="pa-4" elevation="2">
    <div class="text-caption mb-2 font-weight-bold">
      CPU 전체 사용률 실시간 모니터링 (Smoothie Chart)
    </div>
    <canvas ref="smoothieCanvas" width="800" height="150"></canvas>
  </v-card>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { SmoothieChart, TimeSeries } from 'smoothie'
import axios from 'axios'

const API_INTERVAL = 500
const API_URL = 'http://localhost:8000/api/cpu/usage'
const smoothieCanvas = ref(null)

let chart = null
let series = null
let timer = null

onMounted(() => {
  series = new TimeSeries()
  chart = new SmoothieChart({
    grid: { strokeStyle: '#333', fillStyle: '#000', lineWidth: 1, millisPerLine: 1000, verticalSections: 6 },
    labels: { fillStyle: '#333', fontSize: 14 },
    tooltip: true, tooltipLine: { strokeStyle: '#bbbbbb' },
    //  timestampFormatter:SmoothieChart.timeFormatter,
    millisPerPixel: 100,
    minValue: 0,
    maxValue: 100
  })
  chart.addTimeSeries(series, {
    strokeStyle: 'rgb(54,162,235)',
    fillStyle: 'rgba(54,162,235,0.2)',
    lineWidth: 2,
    interpolation: 'linear'
  })
  chart.streamTo(smoothieCanvas.value, 500)

  const fetch = async () => {
    try {
      const res = await axios.get(API_URL)
      const now = Date.now()
      series.append(now, res.data.value)
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