<template>

  <v-card height="100%" elevation="2" class="pa-4 d-flex flex-column align-center justify-center">
    <div class="text-caption mb-2 font-weight-bold">클러스터 정보</div>
    <div>
      CPU: <template v-if="CPU_COUNT !== null">{{ CPU_COUNT }}개</template>
      <template v-else>...</template>
    </div>
    <div>
      GPU: <template v-if="GPU_COUNT !== null">{{ GPU_COUNT }}개</template>
      <template v-else>...</template>
    </div>
    <div>
      MEM: <template v-if="TOTAL_MEM !== null">{{ TOTAL_MEM }}GB</template>
      <template v-else>...</template>
    </div>
    <div>
      UPTIME: <template v-if="UPTIME !== null">{{ UPTIME }}분</template>
      <template v-else>...</template>
    </div>
  </v-card>

</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'

const API_INTERVAL = 1000
const API_URL_CPU_COUNT = 'http://localhost:8000/api/cpu/count'
const API_URL_GPU_COUNT = 'http://localhost:8000/api/gpu/count'
const API_URL_MEM_TOTAL = 'http://localhost:8000/api/mem/total'
const API_URL_UPTIME = 'http://localhost:8000/api/system/uptime'

const CPU_COUNT = ref(null)
const GPU_COUNT = ref(null)
const TOTAL_MEM = ref(null)
const UPTIME = ref(null)
let timer = null

// 각각 fetch 함수
async function fetchValue(endpoint, stateRef) {
  try {
    const res = await axios.get(endpoint)
    stateRef.value = parseFloat(res.data.value)
  } catch (e) {
    stateRef.value = null
  }
}

const fetchHWInfo = () => {
  fetchValue(API_URL_CPU_COUNT, CPU_COUNT)
  fetchValue(API_URL_GPU_COUNT, GPU_COUNT)
  fetchValue(API_URL_MEM_TOTAL, TOTAL_MEM)
}

async function fetchUptime() {
  fetchValue(API_URL_UPTIME, UPTIME)
}

onMounted(() => {
  fetchHWInfo()
  fetchUptime()
  timer = setInterval(fetchUptime, API_INTERVAL)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.caption {
  font-size: 0.85rem;
}
</style>