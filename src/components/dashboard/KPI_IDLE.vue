<template>
  <v-card height="100%" elevation="2" class="pa-4 d-flex flex-column align-center justify-center">
    <div class="text-caption mb-2 font-weight-bold">전체 자원 Idle 시간</div>
    <v-icon size="36" color="grey">mdi-timer-sand</v-icon>
    <div class="mt-1 text-h4">
      <template v-if="IDLETIME !== null">{{ IDLETIME }}</template>
      <template v-else>...</template>
    </div>
    <div class="caption text-grey">누적(분)</div>
  </v-card>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'

const API_INTERVAL = 1000
const API_URL = 'https://gpu-board.onrender.com:8000/api/system/idletime'
const IDLETIME = ref(null)

let timer = null

async function fetch() {
  try {
    const res = await axios.get(API_URL)
    IDLETIME.value = res.data.value
  } catch (e) {
    IDLETIME.value = null
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