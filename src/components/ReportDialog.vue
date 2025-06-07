<template>
  <v-dialog v-model="model" max-width="1200" persistent>
    <v-card>
      <v-card-title>
        보고서 (월별 히트맵/상태/막대차트)
        <v-spacer/>
        <v-btn icon @click="model=false"><v-icon>mdi-close</v-icon></v-btn>
      </v-card-title>
      <v-card-text>
        <BarSummary />
        <Heatmap resourceType="GPU" />
        <Heatmap resourceType="CPU" />
        <!-- GPU 차트 -->
        <h3 class="mt-5">[GPU]</h3>
        <div v-if="gpuLoaded">
          <BarChart :labels="gpuDates" :data="gpuDaily" title="일별 GPU 사용량"/>
          <BarChart :labels="gpuUsers" :data="gpuUser" title="사용자별 GPU 누적 사용일" color="#6c47ff"/>
          <BarChart :labels="gpuIdleLabels" :data="gpuIdleValues" title="GPU별 유휴 일수" color="#43a047"/>
        </div>
        <div v-else>Loading GPU chart...</div>
        <!-- CPU 차트 -->
        <h3 class="mt-5">[CPU]</h3>
        <div v-if="cpuLoaded">
          <BarChart :labels="cpuDates" :data="cpuDaily" title="일별 CPU 사용량"/>
          <BarChart :labels="cpuUsers" :data="cpuUser" title="사용자별 CPU 누적 사용일" color="#007aff"/>
          <BarChart :labels="cpuIdleLabels" :data="cpuIdleValues" title="CPU별 유휴 일수" color="#bb66aa"/>
        </div>
        <div v-else>Loading CPU chart...</div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import BarSummary from './BarSummary.vue'
import Heatmap from './Heatmap.vue'
import BarChart from './BarChart.vue'
import axios from 'axios'

const model = defineModel()

// GPU
const gpuLoaded = ref(false)
const gpuDates = ref([]), gpuDaily = ref([]), gpuUsers = ref([]), gpuUser = ref([])
const gpuIdleLabels = ref([]), gpuIdleValues = ref([])
// CPU
const cpuLoaded = ref(false)
const cpuDates = ref([]), cpuDaily = ref([]), cpuUsers = ref([]), cpuUser = ref([])
const cpuIdleLabels = ref([]), cpuIdleValues = ref([])

onMounted(async () => {
  // GPU
  const usage = (await axios.get('http://127.0.0.1:5000/api/reports/usage?type=GPU')).data
  gpuDates.value = usage.dates
  gpuDaily.value = usage.daily_usage
  gpuUsers.value = usage.users
  gpuUser.value = usage.user_usage
  const idle = (await axios.get('http://127.0.0.1:5000/api/reports/idle?type=GPU')).data
  gpuIdleLabels.value = idle.map(i => `${i.type}${i.res_id}`)
  gpuIdleValues.value = idle.map(i => i.idle_days)
  gpuLoaded.value = true
  // CPU
  const usage2 = (await axios.get('http://127.0.0.1:5000/api/reports/usage?type=CPU')).data
  cpuDates.value = usage2.dates
  cpuDaily.value = usage2.daily_usage
  cpuUsers.value = usage2.users
  cpuUser.value = usage2.user_usage
  const idle2 = (await axios.get('http://127.0.0.1:5000/api/reports/idle?type=CPU')).data
  cpuIdleLabels.value = idle2.map(i => `${i.type}${i.res_id}`)
  cpuIdleValues.value = idle2.map(i => i.idle_days)
  cpuLoaded.value = true
})
</script>
