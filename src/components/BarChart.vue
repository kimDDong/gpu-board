<!-- src/components/BarChart.vue -->
<template>
  <div>
    <h4 v-if="title">{{ title }}</h4>
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { Bar } from 'vue-chartjs'
import { Chart, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { computed } from 'vue'

Chart.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps({
  labels: { type: Array, required: true },
  data: { type: Array, required: true },
  title: { type: String, default: '' },
  color: { type: String, default: '#1976d2' }
})

// Chart data (labels + dataset)
const chartData = computed(() => ({
  labels: props.labels,
  datasets: [{
    label: props.title,
    backgroundColor: props.color,
    data: props.data,
    borderRadius: 6,
    barPercentage: 0.7,
  }]
}))

const chartOptions = {
  responsive: true,
  plugins: {
    legend: { display: false },
    tooltip: { enabled: true },
  },
  scales: {
    x: {
      ticks: { color: '#444' }
    },
    y: {
      beginAtZero: true,
      ticks: { color: '#444' }
    }
  }
}
</script>
