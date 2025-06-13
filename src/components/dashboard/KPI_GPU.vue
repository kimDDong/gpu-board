<template>
  <v-card height="100%" elevation="2" class="pa-4 d-flex flex-column align-center justify-center">
    <div class="text-caption mb-2 font-weight-bold">GPU 전체 사용률</div>
    <template v-if="gpu !== null">
      <v-progress-circular :size="100" :width="10" :model-value="gpu"
        :color="getColor(gpu.usage, 'deep-purple accent-4')">
        <span class="text-h6">{{ gpu }}%</span>
      </v-progress-circular>
    </template>
    <template v-else>
      <v-progress-circular indeterminate :size="100" :width="10">
        <span class="text-h6">%</span>
      </v-progress-circular>
    </template>
  </v-card>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'

const API_INTERVAL = 2000
const API_URL = 'http://localhost:8000/api/gpu/usage'
const WARNING_LEVEL = 80
const DANGER_LEVEL = 90

const gpu = ref(null)
let timer = null

function getColor(val, color) {
  if (val >= WARNING_LEVEL) return 'red'       // 위험(빨강)
  if (val >= DANGER_LEVEL) return 'orange'   // 주의(주황)
  return color //'primary'
}

async function fetch() {
  try {
    const res = await axios.get(API_URL)
    gpu.value = res.data.value
  } catch (e) {
    gpu.value = null
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
.caption {
  font-size: 0.85rem;
}
</style>