<template>
  <div>
    <div style="height: 260px">
      <canvas ref="canvas"></canvas>
    </div>
    <div class="text-center font-weight-bold mt-2">{{ title }}</div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps({
  labels: Array,
  data: Array,
  title: String,
  color: { type: String, default: '#1976d2' }
})

const chart = ref(null)
const canvas = ref(null)

function draw() {
  if (chart.value) {
    chart.value.destroy()
  }
  chart.value = new Chart(canvas.value, {
    type: 'bar',
    data: {
      labels: props.labels,
      datasets: [{
        label: props.title,
        data: props.data,
        backgroundColor: props.color,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  })
}

onMounted(draw)
watch(() => [props.labels, props.data], draw)
</script>
