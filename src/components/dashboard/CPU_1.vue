<template>
  <v-card height="100%" class="pa-4" elevation="2">
    <div class="text-caption mb-2 font-weight-bold">CPU 상세 - 코어 별 사용률</div>
    <v-row>
      <v-col
        v-for="(core, idx) in cpuCores"
        :key="core.id"
        cols="12"
        sm="2"
        md="2"
      >
        <div class="d-flex justify-space-between align-center mb-1">
          <span class="text-body2 font-weight-bold">코어 {{ core.id }}</span>
          <span class="text-body2">{{ core.usage }}%</span>
        </div>
        <v-progress-linear
          :model-value="core.usage"
          height="18"
          :color="getColor(core.usage)"
          striped
          :max="100"
        />
      </v-col>
      <v-col v-if="!cpuCores.length">
        <v-skeleton-loader type="list-item-avatar"/>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const cpuCores = ref([]) // [{ id: 0, usage: 12 }, ...]

const INTERVAL =2000


function getColor(val) {
  if (val >= 90.0) return 'red'       // 위험(빨강)
  if (val >= 80.0) return 'orange'   // 주의(주황)
  return 'primary'
}

async function fetch() {
 try {
    // 예시: [{ id: 0, usage: 23.4 }, ...]
    const res = await axios.get('http://localhost:8000/api/cpu/core_util')
    cpuCores.value = res.data.cores   // 백엔드 반환 shape: {cores: [ {id, usage} ]}
 } catch (e) {
    cpuCores.value = []
 }
}

let intervalId = null

onMounted(() => {
 fetch()
  intervalId = setInterval(fetch, INTERVAL)
})
onUnmounted(() => intervalId && clearInterval(intervalId))
</script>