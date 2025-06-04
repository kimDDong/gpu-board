<template>
  <v-row>
    <v-col cols="12" md="6">
      <v-card>
        <v-card-title>자원 사용량 보고서</v-card-title>
        <v-card-text>
          <div v-if="usageLoaded">
            <BarChart
              :labels="usageDates"
              :data="usageDaily"
              title="일별 GPU 사용량"
            />
            <BarChart
              :labels="usageUsers"
              :data="usageUser"
              title="사용자별 누적 사용일"
              color="#6c47ff"
            />
            <div class="mt-3 text-caption">
              <strong>전체 GPU 사용일 합계:</strong> {{ usageTotal }}일
            </div>
          </div>
          <div v-else>Loading...</div>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12" md="6">
      <v-card>
        <v-card-title>유휴 시간 보고서</v-card-title>
        <v-card-text>
          <div v-if="idleLoaded">
            <BarChart
              :labels="idleLabels"
              :data="idleValues"
              title="GPU별 유휴 일수"
              color="#43a047"
            />
            <ul class="mt-3 text-caption">
              <li v-for="item in idleData" :key="item.gpu_id">
                GPU {{ item.gpu_id }} ({{ item.user }}) - 유휴 {{ item.idle_days }}일
              </li>
            </ul>
          </div>
          <div v-else>Loading...</div>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import BarChart from '@/components/BarChart.vue'

const usageLoaded = ref(false)
const idleLoaded = ref(false)
const usageDates = ref([])
const usageDaily = ref([])
const usageUsers = ref([])
const usageUser = ref([])
const usageTotal = ref(0)
const idleLabels = ref([])
const idleValues = ref([])
const idleData = ref([])

onMounted(async () => {
  // 사용량
  const usage = (await axios.get('http://127.0.0.1:5000/api/reports/usage')).data
  usageDates.value = usage.dates
  usageDaily.value = usage.daily_usage
  usageUsers.value = usage.users
  usageUser.value = usage.user_usage
  usageTotal.value = usage.total_usage
  usageLoaded.value = true

  // 유휴시간
  const idle = (await axios.get('http://127.0.0.1:5000/api/reports/idle')).data
  idleLabels.value = idle.map(i => `GPU${i.gpu_id}`)
  idleValues.value = idle.map(i => i.idle_days)
  idleData.value = idle
  idleLoaded.value = true
})
</script>
