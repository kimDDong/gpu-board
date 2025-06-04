<template>
  <v-card height="100%" class="pa-4" elevation="2">
    <div class="text-caption mb-2 font-weight-bold">GPU 상세 - GPU 별 사용률</div>
    <v-row>
      <v-col
        v-for="(gpu, idx) in gpus"
        :key="gpu.id"
        cols="12"
        sm="2"
        md="2"
      >
        <div class="d-flex justify-space-between align-center mb-1">
          <span class="text-body2 font-weight-bold">GPU {{ gpu.id }}</span>
          <span class="text-body2">{{ gpu.usage }}%</span>
        </div>
        <v-progress-linear
          :model-value="gpu.usage"
          height="18"
          :color="getColor(gpu.usage)"
          striped
          :max="100"
        />
      </v-col>
      <v-col v-if="!gpus.length">
        <v-skeleton-loader type="list-item-avatar"/>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const gpus = ref([]) // [{ id: 0, usage: 12 }, ...]

let intervalId = null
const INTERVAL =200

function getColor(val) {
  if (val >= 90.0) return 'red'       // 위험(빨강)
  if (val >= 80.0) return 'orange'   // 주의(주황)
  return 'primary'
}

async function fetch() {
 try {
    // 예시: [{ id: 0, usage: 23.4 }, ...]
    const res = await axios.get('http://localhost:8000/api/gpu/util_detail')
    gpus.value = res.data.gpus
 } catch (e) {
    gpus.value = []
 }
}

onMounted(() => {
 fetch()
  intervalId = setInterval(fetch, INTERVAL)
})
onUnmounted(() => intervalId && clearInterval(intervalId))
</script>