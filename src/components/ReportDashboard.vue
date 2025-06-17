<template>
  <v-container>
    <!-- 시스템 요약 -->
    <v-row>
      <v-col cols="12" md="4">
        <v-card class="pa-3">
          <div class="text-h6 mb-2">System Info</div>
          <div>총 유저수: <b>{{ sysinfo.user_count }}</b></div>
          <div>GPU: <b>{{ sysinfo.gpu_count }}</b> ({{ sysinfo.gpu_models?.join(', ') }})</div>
          <div>CPU: <b>{{ sysinfo.cpu_count }}</b> ({{ sysinfo.cpu_models?.join(', ') }})</div>
          <div>Memory: <b>{{ sysinfo.memory_count }}</b> ({{ sysinfo.memory_total_tb }}TB)</div>
          <div>GPU 사용중: {{ sysinfo.gpu_used }} / CPU 사용중: {{ sysinfo.cpu_used }} / Memory 사용중: {{ sysinfo.memory_used }}
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="8">
        <LineChart v-if="usageLoaded" :chart-data="totalUsageChartData" :options="lineOptions"
          title="전체 자원 사용량 (GPU/CPU/Memory)" />
        <div v-else>Loading...</div>
      </v-col>
    </v-row>

    <!-- 개별 사용량 -->
    <v-row>
      <v-col cols="12" md="4">
        <v-card class="pa-3">
          <div class="d-flex align-center mb-2">
            <div class="text-h6">GPU 개별 사용량</div>
            <v-select :items="gpuNames" v-model="selectedGpu" label="GPU 선택" dense class="ml-4"
              style="max-width:150px" />
          </div>
          <LineChart v-if="gpuDetailChartData" :chart-data="gpuDetailChartData" :options="lineOptions"
            title="GPU 개별 사용량" />
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-3">
          <div class="d-flex align-center mb-2">
            <div class="text-h6">CPU 개별 사용량</div>
            <v-select :items="cpuNames" v-model="selectedCpu" label="CPU 선택" dense class="ml-4"
              style="max-width:150px" />
          </div>
          <LineChart v-if="cpuDetailChartData" :chart-data="cpuDetailChartData" :options="lineOptions"
            title="CPU 개별 사용량" />
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-3">
          <div class="d-flex align-center mb-2">
            <div class="text-h6">Memory 개별 사용량</div>
            <v-select :items="memoryNames" v-model="selectedMemory" label="Memory 선택" dense class="ml-4"
              style="max-width:150px" />
          </div>
          <LineChart v-if="memoryDetailChartData" :chart-data="memoryDetailChartData" :options="lineOptions"
            title="Memory 개별 사용률(%)" />
        </v-card>
      </v-col>
    </v-row>

    <!-- 온도/사용률 -->
    <v-row>
      <v-col cols="12" md="4">
        <v-card class="pa-3">
          <div class="text-h6 mb-2">GPU 온도(°C)</div>
          <ul>
            <li v-for="(t, i) in gpuTemps" :key="i">
              {{ gpuNames[i] }}: <b>{{ t }}°C</b>
            </li>
          </ul>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-3">
          <div class="text-h6 mb-2">CPU 온도(°C)</div>
          <ul>
            <li v-for="(t, i) in cpuTemps" :key="i">
              {{ cpuNames[i] }}: <b>{{ t }}°C</b>
            </li>
          </ul>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-3">
          <div class="text-h6 mb-2">Memory 사용률(%)</div>
          <ul>
            <li v-for="(t, i) in memoryUsages" :key="i">
              {{ memoryNames[i] }}: <b>{{ t }}%</b>
            </li>
          </ul>
        </v-card>
      </v-col>
    </v-row>

    <!-- 사용자 랭크 -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <div class="text-h6 pa-3">사용자 랭크 (누적 사용량)</div>
          <v-table>
            <thead>
              <tr>
                <th>순위</th>
                <th>이름</th>
                <th>GPU 사용일</th>
                <th>CPU 사용일</th>
                <th>Memory 사용일</th>
                <th>리포트</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(u, i) in userRank" :key="u.name">
                <td>{{ i + 1 }}</td>
                <td>{{ u.name }}</td>
                <td>{{ u.gpu }}</td>
                <td>{{ u.cpu }}</td>
                <td>{{ u.memory }}</td>
                <td>
                  <a :href="'/report/user/' + u.name" target="_blank">보고서</a>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'
import LineChart from './resources/LineChart.vue'

const sysinfo = ref({})
const totalUsage = ref({ dates: [], gpu: [], cpu: [], memory: [] })
const usageLoaded = ref(false)
const gpuNames = ref([])
const cpuNames = ref([])
const memoryNames = ref([])
const selectedGpu = ref('')
const selectedCpu = ref('')
const selectedMemory = ref('')
const gpuDetail = ref({ dates: [], values: [] })
const cpuDetail = ref({ dates: [], values: [] })
const memoryDetail = ref({ dates: [], values: [] })
const gpuTemps = ref([])
const cpuTemps = ref([])
const memoryUsages = ref([])
const userRank = ref([])

const lineOptions = {
  responsive: true,
  plugins: { legend: { display: true } },
  scales: { y: { beginAtZero: true } }
}

// 시스템 정보, 자원명 목록 등 불러오기
async function fetchAll() {
  // 시스템 요약
  sysinfo.value = (await axios.get('https://gpu-board.onrender.com/api/report/sysinfo')).data

  // 전체 사용량
  const usage = (await axios.get('https://gpu-board.onrender.com/api/report/total_usage')).data
  totalUsage.value = usage
  usageLoaded.value = true

  // 이름 목록, 온도/사용률
  const status = (await axios.get('https://gpu-board.onrender.com/api/report/status')).data
  gpuNames.value = status.gpu_names
  cpuNames.value = status.cpu_names
  memoryNames.value = status.memory_names
  gpuTemps.value = status.gpu_temps
  cpuTemps.value = status.cpu_temps
  memoryUsages.value = status.memory_usages
  selectedGpu.value = gpuNames.value[0]
  selectedCpu.value = cpuNames.value[0]
  selectedMemory.value = memoryNames.value[0]

  // 랭크
  userRank.value = (await axios.get('https://gpu-board.onrender.com/api/report/rank')).data
  fetchIndividualDetails()
}

onMounted(fetchAll)

async function fetchIndividualDetails() {
  if (selectedGpu.value) {
    gpuDetail.value = (await axios.get('https://gpu-board.onrender.com/api/report/individual_usage', { params: { type: "GPU", name: selectedGpu.value } })).data
  }
  if (selectedCpu.value) {
    cpuDetail.value = (await axios.get('https://gpu-board.onrender.com/api/report/individual_usage', { params: { type: "CPU", name: selectedCpu.value } })).data
  }
  if (selectedMemory.value) {
    memoryDetail.value = (await axios.get('https://gpu-board.onrender.com/api/report/individual_usage', { params: { type: "Memory", name: selectedMemory.value } })).data
  }
}

watch(selectedGpu, fetchIndividualDetails)
watch(selectedCpu, fetchIndividualDetails)
watch(selectedMemory, fetchIndividualDetails)

const totalUsageChartData = computed(() => ({
  labels: totalUsage.value.dates,
  datasets: [
    { label: "GPU 전체 사용량", data: totalUsage.value.gpu, fill: false, tension: 0.4 },
    { label: "CPU 전체 사용량", data: totalUsage.value.cpu, fill: false, tension: 0.4 },
    { label: "Memory 전체 사용량", data: totalUsage.value.memory, fill: false, tension: 0.4 }
  ]
}))
const gpuDetailChartData = computed(() => ({
  labels: gpuDetail.value.dates,
  datasets: [
    { label: selectedGpu.value + " 사용량", data: gpuDetail.value.values, fill: false, tension: 0.4 }
  ]
}))
const cpuDetailChartData = computed(() => ({
  labels: cpuDetail.value.dates,
  datasets: [
    { label: selectedCpu.value + " 사용량", data: cpuDetail.value.values, fill: false, tension: 0.4 }
  ]
}))
const memoryDetailChartData = computed(() => ({
  labels: memoryDetail.value.dates,
  datasets: [
    { label: selectedMemory.value + " 사용률(%)", data: memoryDetail.value.values, fill: false, tension: 0.4 }
  ]
}))
</script>
