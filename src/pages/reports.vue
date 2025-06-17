<template>
  <v-container style="max-width: 1500px;">
    <!-- 기간 선택 (상단 고정) -->
    <v-row class="mb-6">
      <v-col cols="12" md="5">
        <v-menu v-model="startDateMenu" :close-on-content-click="false" transition="scale-transition" offset-y min-width="auto">
          <template #activator="{ props }">
            <v-text-field v-model="selectedStartDate" label="시작 날짜" prepend-icon="mdi-calendar" readonly v-bind="props" hide-details />
          </template>
          <v-date-picker v-model="selectedStartDate" type="string" no-title scrollable
            @update:modelValue="date => { startDateMenu = false; selectedStartDate = formatDateToString(date); }"
            locale="ko-KR" />
        </v-menu>
      </v-col>
      <v-col cols="12" md="5">
        <v-menu v-model="endDateMenu" :close-on-content-click="false" transition="scale-transition" offset-y min-width="auto">
          <template #activator="{ props }">
            <v-text-field v-model="selectedEndDate" label="종료 날짜" prepend-icon="mdi-calendar" readonly v-bind="props" hide-details />
          </template>
          <v-date-picker v-model="selectedEndDate" type="string" no-title scrollable
            @update:modelValue="date => { endDateMenu = false; selectedEndDate = formatDateToString(date); }"
            locale="ko-KR" />
        </v-menu>
      </v-col>
      <v-col cols="12" md="2" class="d-flex align-center">
        <v-btn color="primary" class="mr-2" @click="setThisYear">올해 전체</v-btn>
        <v-btn color="info" @click="reloadAll">새로고침</v-btn>
      </v-col>
    </v-row>

    <!-- 시스템 정보, 전체/개별 사용량, 랭크 등 기존과 동일하게 차트, 테이블 유지 -->
    <SystemInfoCards :sysinfo="sysinfo" />

    <TotalUsageCharts
      :usageLoaded="usageLoaded"
      :cpuUsageChartData="cpuUsageChartData"
      :memoryUsageChartData="memoryUsageChartData"
      :gpuUsageChartData="gpuUsageChartData"
      :cpuLineOptions="cpuLineOptions"
      :memoryLineOptions="memoryLineOptions"
      :gpuLineOptions="gpuLineOptions"
    />

    <IndividualCharts
      :gpuNames="gpuNames"
      :cpuNames="cpuNames"
      :memoryNames="memoryNames"
      :selectedGpuTemps="selectedGpuTemps"
      @update:selectedGpuTemps="val => selectedGpuTemps = val"
      :gpuTempsChartData="gpuTempsChartData"
      :gpuTempLineOptions="gpuTempLineOptions"
      :selectedGpu="selectedGpu"
      @update:selectedGpu="val => selectedGpu = val"
      :gpuDetailChartData="gpuDetailChartData"
      :gpuLineOptions="gpuLineOptions"
      :selectedCpu="selectedCpu"
      @update:selectedCpu="val => selectedCpu = val"
      :cpuDetailChartData="cpuDetailChartData"
      :cpuLineOptions="cpuLineOptions"
      :selectedMemory="selectedMemory"
      @update:selectedMemory="val => selectedMemory = val"
      :memoryDetailChartData="memoryDetailChartData"
      :memoryLineOptions="memoryLineOptions"
    />

    <UserRankTables :userRank="userRank" />
  </v-container>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'
import SystemInfoCards from '@/components/reports/SystemInfoCards.vue'
import TotalUsageCharts from '@/components/reports/TotalUsageCharts.vue'
import IndividualCharts from '@/components/reports/IndividualCharts.vue'
import UserRankTables from '@/components/reports/UserRankTables.vue'

// 날짜 선택 State
const today = new Date()
const thisYear = today.getFullYear()
const selectedStartDate = ref(`${thisYear}-01-01`)
const selectedEndDate = ref(`${thisYear}-12-31`)
const startDateMenu = ref(false)
const endDateMenu = ref(false)

function formatDateToString(date) {
  if (!date) return ''
  if (typeof date === 'string') return date
  if (date instanceof Date) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  return ''
}
function toYYYYMMDD(date) {
  if (!date) return ''
  if (typeof date === 'string') return date.replace(/-/g, '')
  return formatDateToString(date).replace(/-/g, '')
}
function setThisYear() {
  selectedStartDate.value = `${thisYear}-01-01`
  selectedEndDate.value = `${thisYear}-12-31`
}
function reloadAll() {
  fetchAll()
}

// --- 데이터 State ---
const sysinfo = ref({})
const totalUsage = ref({ dates: [], gpu: [], cpu: [], memory: [] })
const usageLoaded = ref(false)
const gpuNames = ref([])
const cpuNames = ref([])
const memoryNames = ref([])
const selectedGpu = ref('')
const selectedGpuTemps = ref([])
const selectedCpu = ref('')
const selectedMemory = ref('')
const gpuDetail = ref({ dates: [], values: [] })
const cpuDetail = ref({ dates: [], values: [] })
const memoryDetail = ref({ dates: [], values: [] })
const userRank = ref({ usage: [], idle: [] })
const gpuTempSeries = ref({})

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
const gpuLineOptions = computed(() => ({
  ...lineOptionsBase,
  plugins: {
    ...lineOptionsBase.plugins,
    tooltip: {
      callbacks: {
        label: ctx => {
          const value = ctx.raw
          const total = sysinfo.value.gpu_count || 1
          const percent = Math.round((value / total) * 100)
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
          const percent = Math.round((value / total) * 100)
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
          const percent = Math.round((value / total) * 100)
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

// -------- fetchAll, 데이터 fetch 함수 --------
async function fetchAll() {
  const start = toYYYYMMDD(selectedStartDate.value)
  const end = toYYYYMMDD(selectedEndDate.value)
  // sysinfo 요청시 end 파라미터 추가!
  sysinfo.value = (await axios.get('http://localhost:8000/api/report/sysinfo', { params: { end } })).data
  const usage = (await axios.get('http://localhost:8000/api/report/total_usage', { params: { start, end } })).data
  totalUsage.value = usage
  usageLoaded.value = true
  await fetchStatus()
  userRank.value = (await axios.get('http://localhost:8000/api/report/rank', { params: { start, end } })).data
  await fetchIndividualDetails()
}
onMounted(fetchAll)
watch([selectedStartDate, selectedEndDate], fetchAll)

async function fetchStatus() {
  const status = (await axios.get('http://localhost:8000/api/report/status')).data
  gpuNames.value = status.gpu_names
  cpuNames.value = status.cpu_names
  memoryNames.value = status.memory_names
  if (!selectedGpu.value) selectedGpu.value = gpuNames.value[0]
  if (!selectedCpu.value) selectedCpu.value = cpuNames.value[0]
  if (!selectedMemory.value) selectedMemory.value = memoryNames.value[0]
  if (!selectedGpuTemps.value.length) selectedGpuTemps.value = [gpuNames.value[0]]
  // 온도(시계열)도 모두 새로 받아옴 (필요시)
  setTimeout(fetchStatus, 3000)
}

async function fetchIndividualDetails() {
  const start = toYYYYMMDD(selectedStartDate.value)
  const end = toYYYYMMDD(selectedEndDate.value)
  if (selectedGpu.value) {
    gpuDetail.value = (await axios.get('http://localhost:8000/api/report/individual_usage', { params: { type: "GPU", name: selectedGpu.value, start, end } })).data
  }
  if (selectedCpu.value) {
    cpuDetail.value = (await axios.get('http://localhost:8000/api/report/individual_usage', { params: { type: "CPU", name: selectedCpu.value, start, end } })).data
  }
  if (selectedMemory.value) {
    memoryDetail.value = (await axios.get('http://localhost:8000/api/report/individual_usage', { params: { type: "Memory", name: selectedMemory.value, start, end } })).data
  }
  // 선택된 GPU 온도들 동시 갱신
  for (const gpu of selectedGpuTemps.value) {
    if (!gpuTempSeries.value[gpu]) {
      const res = await axios.get('http://localhost:8000/api/report/gpu_temp_series', { params: { name: gpu, start, end } })
      gpuTempSeries.value[gpu] = res.data
    }
  }
}
watch([selectedGpu, selectedCpu, selectedMemory, selectedGpuTemps], fetchIndividualDetails)

// ----------- 차트 데이터 -----------
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
const gpuUsageChartData = computed(() => ({
  labels: totalUsage.value.dates,
  datasets: [{
    label: "GPU 전체 사용량",
    data: totalUsage.value.gpu,
    fill: false,
    tension: 0.4,
    borderColor: "#8e24aa",
    backgroundColor: "#8e24aa"
  }]
}))
const cpuUsageChartData = computed(() => ({
  labels: totalUsage.value.dates,
  datasets: [{
    label: "CPU 전체 사용량",
    data: totalUsage.value.cpu,
    fill: false,
    tension: 0.4,
    borderColor: "#1976d2",
    backgroundColor: "#1976d2"
  }]
}))
const memoryUsageChartData = computed(() => ({
  labels: totalUsage.value.dates,
  datasets: [{
    label: "Memory 전체 사용량",
    data: totalUsage.value.memory,
    fill: false,
    tension: 0.4,
    borderColor: "#43a047",
    backgroundColor: "#43a047"
  }]
}))
const gpuDetailChartData = computed(() => ({
  labels: gpuDetail.value.dates,
  datasets: [{
    label: selectedGpu.value + " 사용량",
    data: gpuDetail.value.values,
    fill: false,
    tension: 0.4,
    borderColor: "#8e24aa",
    backgroundColor: "#8e24aa"
  }]
}))
const cpuDetailChartData = computed(() => ({
  labels: cpuDetail.value.dates,
  datasets: [{
    label: selectedCpu.value + " 사용량",
    data: cpuDetail.value.values,
    fill: false,
    tension: 0.4,
    borderColor: "#1976d2",
    backgroundColor: "#1976d2"
  }]
}))
const memoryDetailChartData = computed(() => ({
  labels: memoryDetail.value.dates,
  datasets: [{
    label: selectedMemory.value + " 사용률(%)",
    data: memoryDetail.value.values,
    fill: false,
    tension: 0.4,
    borderColor: "#43a047",
    backgroundColor: "#43a047"
  }]
}))
</script>
