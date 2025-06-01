<template>
  <v-row>
    <v-col cols="12" md="6">
      <v-card>
        <v-card-title>자원 사용량 보고서</v-card-title>
        <v-card-text>
          <v-chart :labels="usage.labels" :series="usage.usage" chart-title="GPU 사용량"/>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12" md="6">
      <v-card>
        <v-card-title>유휴 시간 보고서</v-card-title>
        <v-card-text>
          <v-chart :labels="idle.labels" :series="idle.idle" chart-title="GPU 유휴시간"/>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import axios from 'axios'
// 심플 바차트 컴포넌트 (직접 만드세요)
import VChart from '../components/BarChart.vue'

export default {
  components: { VChart },
  data() {
    return {
      usage: { labels: [], usage: [] },
      idle: { labels: [], idle: [] }
    }
  },
  mounted() {
    axios.get('http://localhost:5000/api/reports/usage')
      .then(res => { this.usage = res.data })
    axios.get('http://localhost:5000/api/reports/idle')
      .then(res => { this.idle = res.data })
  }
}
</script>
