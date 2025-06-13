<template>

  <v-card height="100%" elevation="2" class="pa-4 d-flex flex-column align-center justify-center">
    <div class="text-caption mb-2 font-weight-bold">클러스터 정보</div>
    <div>
      CPU: <template v-if="cpucnt !== null">{{ cpucnt }}개</template>
      <template v-else>...</template>
    </div>
    <div>
      GPU: <template v-if="gpucnt !== null">{{ gpucnt }}개</template>
      <template v-else>...</template>
    </div>
    <div>
      MEM: <template v-if="totalmem !== null">{{ totalmem }}GB</template>
      <template v-else>...</template>
    </div>
    <div>
      UPTIME: <template v-if="uptime !== null">{{ uptime }}분</template>
      <template v-else>...</template>
    </div>
  </v-card>

</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API_URL_CPU_COUNT = 'http://localhost:8000/api/cpu/count'
const API_URL_GPU_COUNT = 'http://localhost:8000/api/gpu/count'
const API_URL_MEM_TOTAL = 'http://localhost:8000/api/mem/total'
const API_URL_UPTIME = 'http://localhost:8000/api/system/uptime'

const cpucnt = ref(null)
const gpucnt = ref(null)
const totalmem = ref(null)
const uptime = ref(null)

// 각각 fetch 함수
async function fetchValue(endpoint, stateRef) {
  try {
    const res = await axios.get(endpoint)
    stateRef.value = parseFloat(res.data.value)
  } catch (e) {
    stateRef.value = null
  }
}

const fetch = () => {
  fetchValue(API_URL_CPU_COUNT, cpucnt)
  fetchValue(API_URL_GPU_COUNT, gpucnt)
  fetchValue(API_URL_MEM_TOTAL, totalmem)
  fetchValue(API_URL_UPTIME, uptime)
}

onMounted(() => {
  fetch()
})
</script>

<style scoped>
.caption {
  font-size: 0.85rem;
}
</style>