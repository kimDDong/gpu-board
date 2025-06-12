<template>
  <v-container style="max-width: 1400px;">
    <v-card>
      <v-card-title>
        <span class="text-h5">자원 대시보드 보고서</span>
        <v-spacer/>
      </v-card-title>
      <v-card-text>
        <!-- sysinfo 카드 -->
        <v-row class="mb-6">
          <v-col cols="12" md="3">
            <v-card color="deep-purple lighten-2" class="pa-4 text-white" style="border:1.5px solid #e0e0e0;">
              <div class="d-flex align-center mb-1">
                <v-icon size="32">mdi-account-multiple</v-icon>
                <span class="text-h6 ml-2">총 유저</span>
              </div>
              <div class="text-h3 font-weight-bold">{{ sysinfo.user_count }}</div>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card color="indigo darken-1" class="pa-4 text-white" style="border:1.5px solid #e0e0e0;">
              <div class="d-flex align-center mb-1">
                <v-icon size="32">mdi-nvidia</v-icon>
                <span class="text-h6 ml-2">GPU</span>
              </div>
              <div class="text-h3 font-weight-bold">{{ sysinfo.gpu_count }}</div>
              <div class="text-caption mt-1">모델: {{ sysinfo.gpu_models?.join(', ') }}</div>
              <div class="text-caption">사용중: {{ sysinfo.gpu_used }}/{{ sysinfo.gpu_count }}</div>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card color="cyan darken-2" class="pa-4 text-white" style="border:1.5px solid #e0e0e0;">
              <div class="d-flex align-center mb-1">
                <v-icon size="32">mdi-chip</v-icon>
                <span class="text-h6 ml-2">CPU</span>
              </div>
              <div class="text-h3 font-weight-bold">{{ sysinfo.cpu_count }}</div>
              <div class="text-caption mt-1">모델: {{ sysinfo.cpu_models?.join(', ') }}</div>
              <div class="text-caption">사용중: {{ sysinfo.cpu_used }}/{{ sysinfo.cpu_count }}</div>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card color="green darken-1" class="pa-4 text-white" style="border:1.5px solid #e0e0e0;">
              <div class="d-flex align-center mb-1">
                <v-icon size="32">mdi-memory</v-icon>
                <span class="text-h6 ml-2">메모리</span>
              </div>
              <div class="text-h3 font-weight-bold">{{ sysinfo.memory_total_tb }}TB</div>
              <div class="text-caption mt-1">슬롯: {{ sysinfo.memory_count }}개</div>
              <div class="text-caption">사용중: {{ sysinfo.memory_used }}/{{ sysinfo.memory_count }}</div>
            </v-card>
          </v-col>
        </v-row>

        <!-- 전체 사용량 라인차트 (CPU/Memory 위, GPU 크게) -->
        <v-row class="mb-4">
          <v-col cols="12" md="6">
            <v-card class="pa-4 mb-2" style="border:1.5px solid #e0e0e0;">
              <LineChart v-if="usageLoaded"
                :chart-data="cpuUsageChartData"
                :options="cpuLineOptions"
                title="CPU 전체 사용량" />
              <div v-else>Loading...</div>
            </v-card>
          </v-col>
          <v-col cols="12" md="6">
            <v-card class="pa-4 mb-2" style="border:1.5px solid #e0e0e0;">
              <LineChart v-if="usageLoaded"
                :chart-data="memoryUsageChartData"
                :options="memoryLineOptions"
                title="Memory 전체 사용량" />
              <div v-else>Loading...</div>
            </v-card>
          </v-col>
        </v-row>
        <v-row class="mb-6">
          <v-col cols="12">
            <v-card class="pa-4" style="border:2.5px solid #8e24aa;">
              <LineChart v-if="usageLoaded"
                :chart-data="gpuUsageChartData"
                :options="gpuLineOptions"
                title="GPU 전체 사용량 (크게 표시)" />
              <div v-else>Loading...</div>
            </v-card>
          </v-col>
        </v-row>

        <!-- GPU 온도 여러개 토글 -->
        <v-row>
          <v-col cols="12">
            <v-card class="pa-3 mb-2" style="border:1.5px solid #e0e0e0;">
              <div class="d-flex align-center mb-2">
                <div class="text-h6">GPU 개별 온도(°C)</div>
                <v-select
                  :items="gpuNames"
                  v-model="selectedGpuTemps"
                  label="GPU 선택"
                  multiple
                  dense
                  class="ml-4"
                  style="max-width:350px"
                  chips
                />
              </div>
              <LineChart
                v-if="gpuTempsChartData"
                :chart-data="gpuTempsChartData"
                :options="gpuTempLineOptions"
                title="GPU 온도"
              />
            </v-card>
          </v-col>
        </v-row>

        <!-- 개별 사용량 라인차트(3분할) -->
        <v-row>
          <v-col cols="12" md="4">
            <v-card class="pa-3 mb-2" style="border:1.5px solid #e0e0e0;">
              <div class="d-flex align-center mb-2">
                <div class="text-h6">GPU 개별 사용량</div>
                <v-select :items="gpuNames" v-model="selectedGpu" label="GPU 선택" dense class="ml-4" style="max-width:150px" />
              </div>
              <LineChart v-if="gpuDetailChartData" :chart-data="gpuDetailChartData" :options="gpuLineOptions" title="GPU 개별 사용량" />
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card class="pa-3 mb-2" style="border:1.5px solid #e0e0e0;">
              <div class="d-flex align-center mb-2">
                <div class="text-h6">CPU 개별 사용량</div>
                <v-select :items="cpuNames" v-model="selectedCpu" label="CPU 선택" dense class="ml-4" style="max-width:150px" />
              </div>
              <LineChart v-if="cpuDetailChartData" :chart-data="cpuDetailChartData" :options="cpuLineOptions" title="CPU 개별 사용량" />
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card class="pa-3 mb-2" style="border:1.5px solid #e0e0e0;">
              <div class="d-flex align-center mb-2">
                <div class="text-h6">Memory 개별 사용량</div>
                <v-select :items="memoryNames" v-model="selectedMemory" label="Memory 선택" dense class="ml-4" style="max-width:150px" />
              </div>
              <LineChart v-if="memoryDetailChartData" :chart-data="memoryDetailChartData" :options="memoryLineOptions" title="Memory 개별 사용률(%)" />
            </v-card>
          </v-col>
        </v-row>

        <!-- TOP5 랭크 -->
        <v-row class="mt-6">
          <v-col cols="12" md="6">
            <v-card class="pa-3" style="border:1.5px solid #e0e0e0;">
              <div class="text-h6 mb-2">TOP5 누적 사용량 랭크</div>
              <v-table>
                <thead>
                  <tr>
                    <th>순위</th>
                    <th>이름</th>
                    <th>GPU</th>
                    <th>CPU</th>
                    <th>Memory</th>
                    <th>총합</th>
                    <th>리포트</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(u, i) in userRank.usage" :key="u.name">
                    <td>{{ i+1 }}</td>
                    <td>{{ u.name }}</td>
                    <td>{{ u.gpu }}</td>
                    <td>{{ u.cpu }}</td>
                    <td>{{ u.memory }}</td>
                    <td>{{ u.gpu + u.cpu + u.memory }}</td>
                    <td>
                      <a :href="'/report/user/' + u.name" target="_blank">보고서</a>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-card>
          </v-col>
          <v-col cols="12" md="6">
            <v-card class="pa-3" style="border:1.5px solid #e0e0e0;">
              <div class="text-h6 mb-2">TOP5 누적 유휴시간 랭크</div>
              <v-table>
                <thead>
                  <tr>
                    <th>순위</th>
                    <th>이름</th>
                    <th>유휴시간(일)</th>
                    <th>리포트</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(u, i) in userRank.idle" :key="u.name">
                    <td>{{ i+1 }}</td>
                    <td>{{ u.name }}</td>
                    <td>{{ u.idle }}</td>
                    <td>
                      <a :href="'/report/user/' + u.name" target="_blank">보고서</a>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'
import LineChart from '@/components/resources/LineChart.vue'

// ----- 상태 선언
const sysinfo = ref({})
const totalUsage = ref({ dates: [], gpu: [], cpu: [], memory: [] })
const usageLoaded = ref(false)
const gpuNames = ref([])
const cpuNames = ref([])
const memoryNames = ref([])
const selectedGpu = ref('')
const selectedGpuTemps = ref([])  // 여러개!
const selectedCpu = ref('')
const selectedMemory = ref('')
const gpuDetail = ref({ dates: [], values: [] })
const cpuDetail = ref({ dates: [], values: [] })
const memoryDetail = ref({ dates: [], values: [] })
const userRank = ref({ usage: [], idle: [] })
const gpuTempSeries = ref({}) // { gpu_name: {dates:[], temps:[]} ... }

// 색상 팔레트
function getColor(idx) {
  const colors = [
    "#e53935", "#43a047", "#fbc02d", "#1e88e5", "#8e24aa", "#00acc1", "#fb8c00", "#d81b60", "#3949ab", "#388e3c"
  ]
  return colors[idx % colors.length]
}

const lineOptionsBase = {
  responsive: true,
  plugins: { legend: { display: true } },
  scales: { y: { beginAtZero: true } }
}

// ----- 툴팁 옵션(퍼센트 표시)
const gpuLineOptions = computed(() => ({
  ...lineOptionsBase,
  plugins: {
    ...lineOptionsBase.plugins,
    tooltip: {
      callbacks: {
        label: ctx => {
          const value = ctx.raw
          const total = sysinfo.value.gpu_count || 1
          const percent = Math.round((value/total)*100)
          return `사용률: ${percent}% (${value}/${total}개)`
        }
      }
    }
  }
}))
const cpuLineOptions = computed(() => ({
  ...lineOptionsBase,
  plugins: {
    ...lineOptionsBase.plugins,
    tooltip: {
      callbacks: {
        label: ctx => {
          const value = ctx.raw
          const total = sysinfo.value.cpu_count || 1
          const percent = Math.round((value/total)*100)
          return `사용률: ${percent}% (${value}/${total}개)`
        }
      }
    }
  }
}))
const memoryLineOptions = computed(() => ({
  ...lineOptionsBase,
  plugins: {
    ...lineOptionsBase.plugins,
    tooltip: {
      callbacks: {
        label: ctx => {
          const value = ctx.raw
          const total = sysinfo.value.memory_count || 1
          const percent = Math.round((value/total)*100)
          return `사용률: ${percent}% (${value}/${total}슬롯)`
        }
      }
    }
  }
}))
const gpuTempLineOptions = {
  ...lineOptionsBase,
  plugins: {
    ...lineOptionsBase.plugins,
    tooltip: {
      callbacks: {
        label: ctx => `${ctx.dataset.label}: ${ctx.raw} °C`
      }
    }
  }
}

// ----- API 호출
async function fetchAll() {
  sysinfo.value = (await axios.get('http://127.0.0.1:5000/api/report/sysinfo')).data
  const usage = (await axios.get('http://127.0.0.1:5000/api/report/total_usage')).data
  totalUsage.value = usage
  usageLoaded.value = true
  await fetchStatus()
  userRank.value = (await axios.get('http://127.0.0.1:5000/api/report/rank')).data
  fetchIndividualDetails()
}
onMounted(fetchAll)

async function fetchStatus() {
  const status = (await axios.get('http://127.0.0.1:5000/api/report/status')).data
  gpuNames.value = status.gpu_names
  cpuNames.value = status.cpu_names
  memoryNames.value = status.memory_names
  if (!selectedGpu.value) selectedGpu.value = gpuNames.value[0]
  if (!selectedCpu.value) selectedCpu.value = cpuNames.value[0]
  if (!selectedMemory.value) selectedMemory.value = memoryNames.value[0]
  if (!selectedGpuTemps.value.length) selectedGpuTemps.value = [gpuNames.value[0]]
  setTimeout(fetchStatus, 3000)
}
async function fetchIndividualDetails() {
  if (selectedGpu.value) {
    gpuDetail.value = (await axios.get('http://127.0.0.1:5000/api/report/individual_usage', { params: { type: "GPU", name: selectedGpu.value } })).data
  }
  if (selectedCpu.value) {
    cpuDetail.value = (await axios.get('http://127.0.0.1:5000/api/report/individual_usage', { params: { type: "CPU", name: selectedCpu.value } })).data
  }
  if (selectedMemory.value) {
    memoryDetail.value = (await axios.get('http://127.0.0.1:5000/api/report/individual_usage', { params: { type: "Memory", name: selectedMemory.value } })).data
  }
}
watch(selectedGpu, fetchIndividualDetails)
watch(selectedCpu, fetchIndividualDetails)
watch(selectedMemory, fetchIndividualDetails)

// GPU 온도 여러개 토글!
watch(selectedGpuTemps, async (gpus) => {
  for (const gpu of gpus) {
    if (!gpuTempSeries.value[gpu]) {
      const res = await axios.get('http://127.0.0.1:5000/api/report/gpu_temp_series', { params: { name: gpu } })
      gpuTempSeries.value[gpu] = res.data
    }
  }
}, { immediate: true })

// 여러 GPU 온도 데이터셋
const gpuTempsChartData = computed(() => {
  if (!selectedGpuTemps.value.length) return null
  const datasets = selectedGpuTemps.value.map((gpu, i) => {
    const hist = gpuTempSeries.value[gpu]
    if (!hist) return null
    return {
      label: gpu + " 온도(°C)",
      data: hist.temps,
      fill: false,
      tension: 0.2,
      borderColor: getColor(i),
      backgroundColor: getColor(i),
      pointBackgroundColor: hist.temps.map(t => t < 40 ? "#43a047" : (t < 60 ? "#fbc02d" : "#e53935")),
      pointBorderColor: hist.temps.map(t => t < 40 ? "#43a047" : (t < 60 ? "#fbc02d" : "#e53935")),
    }
  }).filter(Boolean)
  return { labels: gpuTempSeries.value[selectedGpuTemps.value[0]]?.dates ?? [], datasets }
})

// ----- 차트 데이터 computed
const gpuUsageChartData = computed(() => ({
  labels: totalUsage.value.dates,
  datasets: [
    {
      label: "GPU 전체 사용량",
      data: totalUsage.value.gpu,
      fill: false,
      tension: 0.4,
      borderColor: "#8e24aa",
      backgroundColor: "#8e24aa"
    }
  ]
}))
const cpuUsageChartData = computed(() => ({
  labels: totalUsage.value.dates,
  datasets: [
    {
      label: "CPU 전체 사용량",
      data: totalUsage.value.cpu,
      fill: false,
      tension: 0.4,
      borderColor: "#1976d2",
      backgroundColor: "#1976d2"
    }
  ]
}))
const memoryUsageChartData = computed(() => ({
  labels: totalUsage.value.dates,
  datasets: [
    {
      label: "Memory 전체 사용량",
      data: totalUsage.value.memory,
      fill: false,
      tension: 0.4,
      borderColor: "#43a047",
      backgroundColor: "#43a047"
    }
  ]
}))
const gpuDetailChartData = computed(() => ({
  labels: gpuDetail.value.dates,
  datasets: [
    {
      label: selectedGpu.value + " 사용량",
      data: gpuDetail.value.values,
      fill: false,
      tension: 0.4,
      borderColor: "#8e24aa",
      backgroundColor: "#8e24aa"
    }
  ]
}))
const cpuDetailChartData = computed(() => ({
  labels: cpuDetail.value.dates,
  datasets: [
    {
      label: selectedCpu.value + " 사용량",
      data: cpuDetail.value.values,
      fill: false,
      tension: 0.4,
      borderColor: "#1976d2",
      backgroundColor: "#1976d2"
    }
  ]
}))
const memoryDetailChartData = computed(() => ({
  labels: memoryDetail.value.dates,
  datasets: [
    {
      label: selectedMemory.value + " 사용률(%)",
      data: memoryDetail.value.values,
      fill: false,
      tension: 0.4,
      borderColor: "#43a047",
      backgroundColor: "#43a047"
    }
  ]
}))
</script>
