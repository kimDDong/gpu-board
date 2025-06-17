<template>
  <v-card height="100%" class="pa-4" elevation="2">
    <div class="text-caption mb-2 font-weight-bold">GPU 사용률 상세</div>
    <v-row>
      <v-col v-for="(gpu, idx) in GPUS_USAGE" :key="gpu.id" cols="12" sm="2" md="2">
        <div class="d-flex justify-space-between align-center mb-1 small">
          <span class="text-body2 font-weight-bold">CPU {{ gpu.id }}</span>
          <span class="text-body2">{{ gpu.value }}%</span>
        </div>
        <v-progress-linear :model-value="gpu.value" height="18" :color="getColor(gpu.value, 'primary')" striped
          :max="100" />
      </v-col>
      <v-col v-if="!GPUS_USAGE.length">
        <v-skeleton-loader type="list-item-avatar" />
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'

const API_INTERVAL = 1000
const API_URL = 'https://gpu-board.onrender.com/api/gpu/detail/usage'
const WARNING_LEVEL = 80
const DANGER_LEVEL = 90
const GPUS_USAGE = ref([]) // [{ id: 0, usage: 12 }, ...]

let timer = null

function getColor(val, color) {
  if (val >= DANGER_LEVEL) return 'red'       // 위험(빨강)
  if (val >= WARNING_LEVEL) return 'orange'   // 주의(주황)
  return color //'primary'
}


async function fetch() {
  try {
    const res = await axios.get(API_URL)
    GPUS_USAGE.value = res.data.gpus
  } catch (e) {
    GPUS_USAGE.value = []
  }
}

onMounted(() => {
  fetch()
  timer = setInterval(fetch, API_INTERVAL)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.small {
  font-size: 65%;
}
</style>