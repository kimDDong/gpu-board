<template>
  <v-dialog v-model="model" max-width="1400" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">자원 대시보드 보고서</span>
        <v-spacer/>
        <v-btn icon @click="model=false"><v-icon>mdi-close</v-icon></v-btn>
      </v-card-title>
      <v-card-text>
        <!-- System Info 카드 -->
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

        <!-- 도넛 차트 카드 -->
        <v-row class="mb-6" style="justify-content:center;">
          <v-col cols="12" md="4">
            <v-card class="pa-3" style="border:1.5px solid #e0e0e0;">
              <DonutChart :used="sysinfo.gpu_used || 0" :total="sysinfo.gpu_count || 0" label="GPU" color="#8e24aa"/>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card class="pa-3" style="border:1.5px solid #e0e0e0;">
              <DonutChart :used="sysinfo.cpu_used || 0" :total="sysinfo.cpu_count || 0" label="CPU" color="#1976d2"/>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card class="pa-3" style="border:1.5px solid #e0e0e0;">
              <DonutChart :used="sysinfo.memory_used || 0" :total="sysinfo.memory_count || 0" label="Memory" color="#43a047"/>
            </v-card>
          </v-col>
        </v-row>

        <!-- 전체 사용량 라인차트 카드 -->
        <v-card class="mb-6 pa-4" style="border:1.5px solid #e0e0e0;">
          <LineChart v-if="usageLoaded"
            :chart-data="totalUsageChartData"
            :options="lineOptions"
            title="전체 자원 사용량 (GPU/CPU/Memory)" />
          <div v-else>Loading...</div>
        </v-card>

        <!-- 개별 사용량 라인차트 카드 -->
        <v-row>
          <v-col cols="12" md="4">
            <v-card class="pa-3 mb-2" style="border:1.5px solid #e0e0e0;">
              <div class="d-flex align-center mb-2">
                <div class="text-h6">GPU 개별 사용량</div>
                <v-select :items="gpuNames" v-model="selectedGpu" label="GPU 선택" dense class="ml-4" style="max-width:150px" />
              </div>
              <LineChart v-if="gpuDetailChartData" :chart-data="gpuDetailChartData" :options="lineOptions" title="GPU 개별 사용량" />
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card class="pa-3 mb-2" style="border:1.5px solid #e0e0e0;">
              <div class="d-flex align-center mb-2">
                <div class="text-h6">CPU 개별 사용량</div>
                <v-select :items="cpuNames" v-model="selectedCpu" label="CPU 선택" dense class="ml-4" style="max-width:150px" />
              </div>
              <LineChart v-if="cpuDetailChartData" :chart-data="cpuDetailChartData" :options="lineOptions" title="CPU 개별 사용량" />
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card class="pa-3 mb-2" style="border:1.5px solid #e0e0e0;">
              <div class="d-flex align-center mb-2">
                <div class="text-h6">Memory 개별 사용량</div>
                <v-select :items="memoryNames" v-model="selectedMemory" label="Memory 선택" dense class="ml-4" style="max-width:150px" />
              </div>
              <LineChart v-if="memoryDetailChartData" :chart-data="memoryDetailChartData" :options="lineOptions" title="Memory 개별 사용률(%)" />
            </v-card>
          </v-col>
        </v-row>

        <!-- 온도/사용률 Progress Bar (카드) -->
        <v-row>
          <v-col cols="12" md="4">
            <v-card class="pa-3 mb-4" style="border:1.5px solid #e0e0e0;">
              <div class="text-h6 mb-2">GPU 온도(°C)</div>
              <ul style="list-style:none; padding:0; margin:0;">
                <li v-for="(t, i) in gpuTemps" :key="i" style="margin-bottom:10px;">
                  <div class="d-flex align-center mb-1">
                    <span style="width:85px; display:inline-block;">{{ gpuNames[i] }}</span>
                    <span :style="{ color: getTempColor(t), width:'50px', display:'inline-block'}">
                      <b>{{ t }}°C</b>
                    </span>
                  </div>
                  <v-progress-linear
                    :model-value="t"
                    :color="getTempColor(t)"
                    height="10"
                    :max="100"
                    style="margin-bottom:2px;"
                  />
                </li>
              </ul>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card class="pa-3 mb-4" style="border:1.5px solid #e0e0e0;">
              <div class="text-h6 mb-2">CPU 온도(°C)</div>
              <ul style="list-style:none; padding:0; margin:0;">
                <li v-for="(t, i) in cpuTemps" :key="i" style="margin-bottom:10px;">
                  <div class="d-flex align-center mb-1">
                    <span style="width:85px; display:inline-block;">{{ cpuNames[i] }}</span>
                    <span :style="{ color: getTempColor(t), width:'50px', display:'inline-block'}">
                      <b>{{ t }}°C</b>
                    </span>
                  </div>
                  <v-progress-linear
                    :model-value="t"
                    :color="getTempColor(t)"
                    height="10"
                    :max="100"
                    style="margin-bottom:2px;"
                  />
                </li>
              </ul>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card class="pa-3 mb-4" style="border:1.5px solid #e0e0e0;">
              <div class="text-h6 mb-2">Memory 사용률(%)</div>
              <ul style="list-style:none; padding:0; margin:0;">
                <li v-for="(t, i) in memoryUsages" :key="i" style="margin-bottom:10px;">
                  <div class="d-flex align-center mb-1">
                    <span style="width:85px; display:inline-block;">{{ memoryNames[i] }}</span>
                    <span style="color: #1976d2; width:50px; display:inline-block;">
                      <b>{{ t }}%</b>
                    </span>
                  </div>
                  <v-progress-linear
                    :model-value="t"
                    color="#1976d2"
                    height="10"
                    :max="100"
                    style="margin-bottom:2px;"
                  />
                </li>
              </ul>
            </v-card>
          </v-col>
        </v-row>

        <!-- 랭크 카드 -->
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
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'
import LineChart from './resources/LineChart.vue'
import DonutChart from './resources/DonutChart.vue'

const model = defineModel()
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
const userRank = ref({ usage: [], idle: [] })

const lineOptions = {
  responsive: true,
  plugins: { legend: { display: true } },
  scales: { y: { beginAtZero: true } }
}

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
  gpuTemps.value = status.gpu_temps
  cpuTemps.value = status.cpu_temps
  memoryUsages.value = status.memory_usages
  if (!selectedGpu.value) selectedGpu.value = gpuNames.value[0]
  if (!selectedCpu.value) selectedCpu.value = cpuNames.value[0]
  if (!selectedMemory.value) selectedMemory.value = memoryNames.value[0]
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

const totalUsageChartData = computed(() => ({
  labels: totalUsage.value.dates,
  datasets: [
    {
      label: "GPU 전체 사용량",
      data: totalUsage.value.gpu,
      fill: false,
      tension: 0.4,
      borderColor: "#8e24aa",
      backgroundColor: "#8e24aa"
    },
    {
      label: "CPU 전체 사용량",
      data: totalUsage.value.cpu,
      fill: false,
      tension: 0.4,
      borderColor: "#1976d2",
      backgroundColor: "#1976d2"
    },
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

function getTempColor(t) {
  if (t <= 40) return "#43a047"
  if (t <= 60) return "#ffc107"
  return "#d32f2f"
}
</script>
