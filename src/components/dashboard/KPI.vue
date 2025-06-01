<template>
  <v-row>

    <!-- CPU 사용률 카드 -->
    <v-col>
      <v-card height="100%" elevation="2" class="pa-4 d-flex flex-column align-center justify-center">
        <div class="text-caption mb-2 font-weight-bold">CPU 전체 사용률</div>
        <template v-if="cpuUtil !== null">
          <v-progress-circular :size="100" :width="10" :model-value="cpuUtil" color="primary">
            <span class="text-h6">{{ cpuUtil }}%</span>
          </v-progress-circular>
        </template>
        <template v-else>
          <v-progress-circular indeterminate :size="100" :width="10" >
            <span class="text-h6">%</span>
          </v-progress-circular>
        </template>
      </v-card>
    </v-col>

    <!-- 메모리 사용률 카드 -->
    <v-col>
      <v-card height="100%" elevation="2" class="pa-4 d-flex flex-column align-center justify-center">
        <div class="text-caption mb-2 font-weight-bold">메모리 전체 사용률</div>
        <template v-if="memUtil !== null">
          <v-progress-circular :size="100" :width="10" :model-value="memUtil" color="success">
            <span class="text-h6">{{ memUtil }}%</span>
          </v-progress-circular>
        </template>
        <template v-else>
          <v-progress-circular indeterminate :size="100" :width="10" >
            <span class="text-h6">%</span>
          </v-progress-circular>
        </template>
      </v-card>
    </v-col>

    <!-- GPU 사용률 카드 -->
    <v-col>
      <v-card height="100%" elevation="2" class="pa-4 d-flex flex-column align-center justify-center">
        <div class="text-caption mb-2 font-weight-bold">GPU 전체 사용률</div>
        <template v-if="gpuUtil !== null">
          <v-progress-circular :size="100" :width="10" :model-value="gpuUtil" color="deep-purple accent-4">
            <span class="text-h6">{{ gpuUtil }}%</span>
          </v-progress-circular>
        </template>
        <template v-else>
          <v-progress-circular indeterminate :size="100" :width="10" >
            <span class="text-h6">%</span>
          </v-progress-circular>
        </template>
      </v-card>
    </v-col>

    <!-- 전체 자원 Idle 시간 카드 -->
    <v-col>
      <v-card height="100%" elevation="2" class="pa-4 d-flex flex-column align-center justify-center">
        <div class="text-caption mb-2 font-weight-bold">전체 자원 Idle 시간</div>
        <v-icon size="36" color="grey">mdi-timer-sand</v-icon>
        <div class="mt-1 text-h4">
          <template v-if="idleTime !== null">{{ idleTime }}</template>
          <template v-else>...</template>
        </div>
        <div class="caption text-grey">누적(분)</div>
      </v-card>
    </v-col>

    <!-- 클러스터 정보 카드 -->
    <v-col>
      <v-card height="100%" elevation="2" class="pa-4 d-flex flex-column align-center justify-center">
        <div class="text-caption mb-2 font-weight-bold">클러스터 정보</div>
        <div>
          CPU: <template v-if="cpuCount !== null">{{ cpuCount }}개</template>
               <template v-else>...</template>
        </div>
        <div>
          GPU: <template v-if="gpuCount !== null">{{ gpuCount }}개</template>
               <template v-else>...</template>
        </div>
        <div>
          MEM: <template v-if="totalMem !== null">{{ totalMem }}GB</template>
                 <template v-else>...</template>
        </div>
        <div>
          UPTIME: <template v-if="upTime !== null">{{ upTime }}분</template>
                 <template v-else>...</template>
        </div>
      </v-card>
    </v-col>

  </v-row>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const INTERVAL_MILLIS =2000 //1초마다 갱신

const cpuCount = ref(null)
const gpuCount = ref(null)
const totalMem = ref(null)
const upTime = ref(null)
const cpuUtil = ref(null)
const memUtil = ref(null)
const gpuUtil = ref(null)
const idleTime = ref(null)

// 각각 fetch 함수
async function fetchValue(endpoint, stateRef) {
 try {
    const res = await axios.get(endpoint)
    // 값이 없거나 에러(비정상)라면 null 반환
    stateRef.value = parseFloat(res.data.value)
  } catch (e) {
    stateRef.value = null
  }
}

const fetchHardwareInfo = () => {
 fetchValue('http://localhost:8000/api/cpu/count', cpuCount)
  fetchValue('http://localhost:8000/api/gpu/count', gpuCount)
  fetchValue('http://localhost:8000/api/mem/total', totalMem)
}

const fetchRealtimeInfo = () => {
  fetchValue('http://localhost:8000/api/cpu/util', cpuUtil)
  fetchValue('http://localhost:8000/api/gpu/util', gpuUtil)
  fetchValue('http://localhost:8000/api/mem/util', memUtil)
  fetchValue('http://localhost:8000/api/system/idle_time', idleTime)
  fetchValue('http://localhost:8000/api/system/uptime', upTime)
}

let intervalId = null

onMounted(() => {
  fetchHardwareInfo()    // 하드웨어 정보 최초1회만 불러옴
  fetchRealtimeInfo()    // 실시간 정보 최초1회 즉시
  intervalId = setInterval(fetchRealtimeInfo, INTERVAL_MILLIS) // 이후 실시간 정보만 주기적 갱신
})
onUnmounted(() => {
 if (intervalId) clearInterval(intervalId)
})
</script>

<style scoped>
.caption {
 font-size: 0.85rem;
}
</style>