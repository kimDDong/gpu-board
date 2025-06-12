<template>
  <div>
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)
const props = defineProps({
  chartData: Object,
  options: Object,
  title: String
})
const canvas = ref(null)
let chartInstance = null

function renderChart() {
  if (!props.chartData) return
  if (chartInstance) chartInstance.destroy()
  chartInstance = new Chart(canvas.value, {
    type: 'line',
    data: props.chartData,
    options: {
      ...props.options,
      plugins: {
        ...props.options?.plugins,
        title: {
          display: !!props.title,
          text: props.title
        }
      }
    }
  })
}
onMounted(renderChart)
watch(() => [props.chartData, props.options, props.title], renderChart, { deep: true })
</script>
