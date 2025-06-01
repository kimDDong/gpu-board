<template>
  <v-card height="100%" class="pa-4" elevation="2">
    <div class="text-caption mb-2 font-weight-bold">
      CPU 전체 사용률 실시간 모니터링 (Smoothie Chart)
    </div>
    <canvas ref="smoothieCanvas" width="700" height="270"></canvas>
  </v-card>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { SmoothieChart, TimeSeries } from 'smoothie'
import axios from 'axios'

const INTERVAL_MILLIS =250 //1초마다 갱신

const smoothieCanvas = ref(null)
let chart = null
let series = null
let timer = null

onMounted(() => {
  // 차트 및 시리즈 준비
   series = new TimeSeries()
   chart = new SmoothieChart({
     grid: { strokeStyle: '#333', fillStyle: '#000', lineWidth: 1, millisPerLine: 1000, verticalSections: 6 },
     labels: { fillStyle: '#333', fontSize: 14 },
     tooltip:true,tooltipLine:{strokeStyle:'#bbbbbb'},
    //  timestampFormatter:SmoothieChart.timeFormatter,
     millisPerPixel:100,
     minValue: 0,
     maxValue: 100
   })
  chart.addTimeSeries(series, {
     strokeStyle: 'rgb(54,162,235)',
     fillStyle: 'rgba(54,162,235,0.2)',
     lineWidth: 2,
     interpolation:'linear'
   })
  chart.streamTo(smoothieCanvas.value, 100)
  
   //2초마다 데이터 fetch & append
   const fetchAndAppend = async () => {
     try {
       const res = await axios.get('http://localhost:8000/api/cpu/util')
       const now = Date.now()
       series.append(now, res.data.value)
     } catch (e) { /* ignore error */ }
  }
  timer = setInterval(fetchAndAppend, INTERVAL_MILLIS)
  fetchAndAppend() // 최초1회 즉시 실행
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
  font-size: 10px;
  pointer-events: none;
}
</style>