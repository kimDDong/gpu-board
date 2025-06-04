<template>
  <v-card height="100%" class="pa-4" elevation="2">
    <div class="text-caption mb-2 font-weight-bold">GPU 상세 - GPU 별 온도(℃)</div>
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
          <!-- 텍스트 색상도 온도별로 -->
          <span class="text-body2" :style="{color: getColor(gpu.temperature)}">
            {{ gpu.temperature }}℃
          </span>
        </div>
        <v-progress-linear
          :model-value="gpu.temperature"
          height="18"
          :color="getColor(gpu.temperature)"
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

const gpus = ref([])

let intervalId = null
const INTERVAL =1000

// 온도에 따라 색상을 결정하는 함수
function getColor(val) {
 if (val >=100) return 'red'       // 위험(빨강)
  if (val >=80) return 'orange'    // 주의(주황)
  if (val >=50) return 'yellow'    // 정상(노랑)
  return 'green'                     // 저온(초록)
}

async function fetch() {
 try {
    const res = await axios.get('http://localhost:8000/api/gpu/temp_detail')
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