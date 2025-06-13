<template>
  <div>
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, Tooltip, CategoryScale, Legend } from 'chart.js'

Chart.register(LineController, LineElement, PointElement, LinearScale, Title, Tooltip, CategoryScale, Legend)

const props = defineProps({
  chartData: Object,
  options: Object,
  title: String
})

const canvas = ref(null)
let chartInstance = null

function fixLabels(data) {
  if (!data || !data.labels) return data
  // 모든 label을 문자열로 강제 변환 (중요!)
  const labels = data.labels.map(l => typeof l === 'string' ? l : String(l))
  return { ...data, labels }
}

function renderChart() {
  if (chartInstance) chartInstance.destroy()
  if (!props.chartData || !canvas.value) return

  // x축 label 너무 많으면 자동 skip
  const labelCount = props.chartData.labels?.length || 0
  const useAutoSkip = labelCount > 16

  const options = {
    ...props.options,
    plugins: {
      ...props.options?.plugins,
      title: { display: !!props.title, text: props.title || '', color: "#fff", font: { size: 18 } },
      legend: { labels: { color: "#fff", font: { size: 13 } } }
    },
    scales: {
      x: {
        type: 'category',
        title: { display: true, text: '날짜', color: '#fff', font: { size: 14 } },
        ticks: {
          color: '#fff',
          autoSkip: useAutoSkip,   // 16개 이상일 땐 자동 skip, 아니면 무조건 다 보여줌
          maxTicksLimit: 16,
          maxRotation: 45,
          minRotation: 20,
          font: { size: 12 }
        },
        grid: { color: '#444' }
      },
      y: {
        beginAtZero: true,
        ticks: { color: '#fff', font: { size: 12 } },
        grid: { color: '#444' }
      }
    }
  }

  chartInstance = new Chart(canvas.value, {
    type: 'line',
    data: fixLabels(props.chartData),
    options
  })
}

// 데이터, 옵션 바뀔 때마다 다시 그림
watch(() => props.chartData, renderChart, { deep: true })
watch(() => props.options, renderChart, { deep: true })
onMounted(renderChart)
onBeforeUnmount(() => { if (chartInstance) chartInstance.destroy() })
</script>

<style scoped>
/* 필요시 스타일 */
</style>
