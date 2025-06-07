<!-- src/components/BarChart.vue -->
<template>
  <div>
    <h4>{{ title }}</h4>
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script>
import { Bar, mixins } from 'vue-chartjs'
const { reactiveProp } = mixins

export default {
  name: 'BarChart',
  extends: Bar,
  mixins: [reactiveProp],
  props: {
    labels: { type: Array, required: true },
    data: { type: Array, required: true },
    title: { type: String, default: '' },
    color: { type: String, default: '#1976d2' }
  },
  computed: {
    datacollection() {
      return {
        labels: this.labels,
        datasets: [{
          label: this.title,
          backgroundColor: this.color,
          data: this.data
        }]
      }
    }
  },
  data() {
    return {
      chartOptions: {
        responsive: true,
        legend: { display: false },
        scales: {
          xAxes: [{ ticks: { fontColor: '#444' } }],
          yAxes: [{ ticks: { beginAtZero: true, fontColor: '#444' } }]
        }
      }
    }
  },
  mounted() {
    this.renderChart(this.datacollection, this.chartOptions)
  },
  watch: {
    datacollection: {
      handler(val) {
        this.renderChart(val, this.chartOptions)
      },
      deep: true
    }
  }
}
</script>
