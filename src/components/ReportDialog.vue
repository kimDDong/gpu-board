<template>
  <v-dialog v-model="model" max-width="1300" persistent>
    <v-card v-if="ready">
      <v-card-title class="justify-space-between text-h5 font-weight-bold">
        전체 보고서
        <v-btn icon @click="close"><v-icon>mdi-close</v-icon></v-btn>
      </v-card-title>
      <v-card-text>
        <!-- 날짜 설정 -->
        <v-row align="center" class="mb-5">
          <v-col cols="12">
            <v-menu v-model="menu" :close-on-content-click="false">
              <template #activator="{ props }">
                <v-text-field
                  v-bind="props"
                  v-model="dateRangeText"
                  label="시작 ~ 종료 기간 설정"
                  readonly
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </template>
              <v-date-picker
                v-model="dateRange"
                range
                @update:model-value="onDateRangePicked"
              />
            </v-menu>
          </v-col>
        </v-row>
        <v-card class="mb-4" color="grey-lighten-3" flat>
          <v-card-text class="text-center text-h6 font-weight-medium" style="height:64px;display:flex;align-items:center;justify-content:center;">
            SYS INFO: OS {{ sysinfo.os }} | CPU {{ sysinfo.cpu }} | MEM {{ sysinfo.mem }} | GPU {{ sysinfo.gpu }}
          </v-card-text>
        </v-card>
        <v-row class="mb-4">
          <v-col cols="12">
            <LineChart
              :labels="periodDates"
              :datasets="[
                { label: 'CPU 사용량', data: periodStats.cpu, borderColor: '#1976d2' },
                { label: 'Memory 사용량', data: periodStats.mem, borderColor: '#009688' },
                { label: 'GPU 전체 사용량', data: periodStats.gpu_total, borderColor: '#43a047' }
              ]"
              :title="'전체 사용량(기간별)'"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="10">
            <v-card class="mb-3">
              <v-card-title class="py-2">GPU 개별 사용량</v-card-title>
              <v-card-text>
                <LineChart
                  :labels="periodDates"
                  :datasets="checkedGpuDatasets"
                  :title="'GPU별 사용량'"
                />
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="2" class="d-flex flex-column align-end">
            <div style="min-width:120px;">
              <div class="font-weight-medium mb-1">체크박스 (옵션)</div>
              <v-checkbox-group v-model="checkedGpus" :mandatory="false" column dense>
                <v-checkbox
                  v-for="gpu in gpus"
                  :key="gpu.id"
                  :label="gpu.name"
                  :value="gpu.id"
                  hide-details
                  density="compact"
                />
              </v-checkbox-group>
            </div>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="10">
            <v-card class="mb-3">
              <v-card-title class="py-2">GPU 개별 온도</v-card-title>
              <v-card-text>
                <v-row>
                  <v-col v-for="gpu in filteredGpus" :key="gpu.id" cols="6" md="3">
                    <v-card outlined>
                      <v-card-title>{{ gpu.name }}</v-card-title>
                      <v-card-text>
                        <div class="text-h6">{{ gpu.temp }} ℃</div>
                        <v-progress-linear :model-value="gpu.temp" :max="100" color="red" height="12" />
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="2" class="d-flex flex-column align-end">
            <div style="min-width:120px;">
              <div class="font-weight-medium mb-1">체크박스 (옵션)</div>
              <v-checkbox-group v-model="checkedGpus" :mandatory="false" column dense>
                <v-checkbox
                  v-for="gpu in gpus"
                  :key="gpu.id"
                  :label="gpu.name"
                  :value="gpu.id"
                  hide-details
                  density="compact"
                />
              </v-checkbox-group>
            </div>
          </v-col>
        </v-row>
        <v-row class="mt-4">
          <v-col cols="6">
            <v-card>
              <v-card-title>사용자 GPU 누적 사용 랭크</v-card-title>
              <v-card-text>
                <v-table>
                  <thead><tr><th>순위</th><th>사용자</th><th>누적 사용량</th></tr></thead>
                  <tbody>
                    <tr v-for="(u,idx) in userRank" :key="u.name">
                      <td>{{ idx+1 }}</td><td>{{ u.name }}</td><td>{{ u.usage }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6">
            <v-card>
              <v-card-title>사용자 GPU 유휴시간 랭크</v-card-title>
              <v-card-text>
                <v-table>
                  <thead><tr><th>순위</th><th>사용자</th><th>누적 유휴시간</th></tr></thead>
                  <tbody>
                    <tr v-for="(u,idx) in userIdleRank" :key="u.name">
                      <td>{{ idx+1 }}</td><td>{{ u.name }}</td><td>{{ u.idle }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card-text>
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
import LineChart from './LineChart.vue'

const model = defineModel()
const ready = ref(false)
const menu = ref(false)
const today = new Date()
const dateRange = ref([today, today])
const dateRangeText = ref('')

const sysinfo = ref({})
const gpus = ref([])
const checkedGpus = ref([])
const userRank = ref([])
const userIdleRank = ref([])
const periodDates = ref([])
const periodStats = ref({ cpu: [], mem: [], gpu_total: [], gpu: [], gpu_labels: [] })

const filteredGpus = computed(() =>
  Array.isArray(gpus.value)
    ? gpus.value.filter(g => checkedGpus.value.includes(g.id))
    : []
)

function dateToStr(dt) {
  return dt.toISOString().slice(0,10)
}
function onDateRangePicked([start, end]) {
  dateRangeText.value = `${dateToStr(start)} ~ ${dateToStr(end)}`
  fetchPeriodStats()
}

async function fetchAll() {
  const sysRes = await axios.get('/api/sysinfo')
  sysinfo.value = sysRes.data || {}

  const gpuRes = await axios.get('/api/gpus')
  gpus.value = Array.isArray(gpuRes.data) ? gpuRes.data : []
  checkedGpus.value = gpus.value.map(g => g.id)

  const urRes = await axios.get('/api/user_rank')
  userRank.value = Array.isArray(urRes.data) ? urRes.data : []
  const uiRes = await axios.get('/api/user_idle_rank')
  userIdleRank.value = Array.isArray(uiRes.data) ? uiRes.data : []

  await fetchPeriodStats()
  ready.value = true
}

async function fetchPeriodStats() {
  const [start, end] = dateRange.value
  const params = new URLSearchParams({ start: dateToStr(start), end: dateToStr(end) })
  checkedGpus.value.forEach(id => params.append('gpus', id))
  const res = await axios.get(`/api/period_stats?${params}`)
  periodDates.value = res.data.dates || []
  periodStats.value = {
    cpu: res.data.cpu || [],
    mem: res.data.mem || [],
    gpu_total: res.data.gpu_total || [],
    gpu: res.data.gpu || [],
    gpu_labels: res.data.gpu_labels || []
  }
}

const checkedGpuDatasets = computed(() =>
  (checkedGpus.value ?? []).map((id, idx) => {
    const label = periodStats.value.gpu_labels?.[idx] || `GPU ${id}`
    const data = periodStats.value.gpu?.[idx] || []
    return {
      label,
      data,
      borderColor: ['#6c47ff','#ff6f61','#43a047','#fbc02d'][idx % 4],
      tension: 0.4
    }
  })
)

setInterval(() => {
  if (!gpus.value || !Array.isArray(gpus.value)) return
  gpus.value.forEach(g => { g.temp = 50 + Math.floor(Math.random()*35) })
}, 3000)

function close() { model.value = false }

onMounted(fetchAll)
watch(dateRange, fetchPeriodStats, { deep: true })
watch(checkedGpus, fetchPeriodStats, { deep: true })
</script>
