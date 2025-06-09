<template>
  <v-dialog v-model="model" max-width="1200" persistent>
    <v-card>
      <v-card-title>
        보고서 (현황/히트맵/막대차트)
        <v-spacer/>
        <v-btn icon @click="model=false"><v-icon>mdi-close</v-icon></v-btn>
      </v-card-title>
      <v-card-text>
        <BarSummary />
        <Heatmap resourceType="GPU" />
        <Heatmap resourceType="CPU" />
        <div v-if="barLoaded">
          <BarChart
            :labels="usageDates"
            :data="usageDaily"
            title="일별 GPU 사용량"
          />
          <BarChart
            :labels="usageUsers"
            :data="usageUser"
            title="GPU 사용자별 누적 사용일"
            color="#6c47ff"
          />
          <BarChart
            :labels="usageDatesCPU"
            :data="usageDailyCPU"
            title="일별 CPU 사용량"
            color="#1976d2"
          />
          <BarChart
            :labels="usageUsersCPU"
            :data="usageUserCPU"
            title="CPU 사용자별 누적 사용일"
            color="#009688"
          />
          <BarChart
            :labels="idleLabelsGPU"
            :data="idleValuesGPU"
            title="GPU별 유휴 일수"
            color="#43a047"
          />
          <BarChart
            :labels="idleLabelsCPU"
            :data="idleValuesCPU"
            title="CPU별 유휴 일수"
            color="#ffc107"
          />
        </div>
        <div v-else>Loading chart...</div>
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

const usageDates = ref([])
const usageDaily = ref([])
const usageUsers = ref([])
const usageUser = ref([])
const idleLabelsGPU = ref([])
const idleValuesGPU = ref([])
// CPU
const usageDatesCPU = ref([])
const usageDailyCPU = ref([])
const usageUsersCPU = ref([])
const usageUserCPU = ref([])
const idleLabelsCPU = ref([])
const idleValuesCPU = ref([])

const barLoaded = ref(false)

onMounted(async () => {
  // GPU 사용량
  const usage = (await axios.get('http://127.0.0.1:5000/api/reports/usage?type=GPU')).data
  usageDates.value = usage.dates
  usageDaily.value = usage.daily_usage
  usageUsers.value = usage.users
  usageUser.value = usage.user_usage
  // CPU 사용량
  const usageCPU = (await axios.get('http://127.0.0.1:5000/api/reports/usage?type=CPU')).data
  usageDatesCPU.value = usageCPU.dates
  usageDailyCPU.value = usageCPU.daily_usage
  usageUsersCPU.value = usageCPU.users
  usageUserCPU.value = usageCPU.user_usage
  // GPU 유휴
  const idleGPU = (await axios.get('http://127.0.0.1:5000/api/reports/idle?type=GPU')).data
  idleLabelsGPU.value = idleGPU.map(i => `GPU${i.res_id}`)
  idleValuesGPU.value = idleGPU.map(i => i.idle_days)
  // CPU 유휴
  const idleCPU = (await axios.get('http://127.0.0.1:5000/api/reports/idle?type=CPU')).data
  idleLabelsCPU.value = idleCPU.map(i => `CPU${i.res_id}`)
  idleValuesCPU.value = idleCPU.map(i => i.idle_days)
  barLoaded.value = true
})
</script>
