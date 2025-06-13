<template>
  <v-card class="pa-4" elevation="2">
    <div class="font-weight-bold mb-2">CPU 사용률 TOP5</div>
    <v-table density="compact">
      <thead>
        <tr>
          <th>순위</th>
          <th>사용자</th>
          <th>CPU(%)</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(user, idx) in users" :key="user.user">
          <td>{{ idx + 1 }}</td>
          <td>{{ user.user }}</td>
          <td>
            <v-progress-linear :model-value="user.value" :color="getColor(user.value, 'primary')" height="16" striped>
              {{ user.value }}%
            </v-progress-linear>
          </td>
        </tr>
        <tr v-if="!users.length">
          <td colspan="3"><v-skeleton-loader type="table-row" /></td>
        </tr>
      </tbody>
    </v-table>
  </v-card>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'

const API_INTERVAL = 1000
const API_URL = 'http://localhost:8000/api/cpu_user_rank'
const WARNING_LEVEL = 70
const DANGER_LEVEL = 90

const users = ref([])
let timer = null

function getColor(val, color) {
  if (val >= WARNING_LEVEL) return 'orange'
  if (val >= DANGER_LEVEL) return 'red'
  return color //'primary'
}


async function fetch() {
  try {
    const res = await axios.get(API_URL)
    users.value = res.data.users.sort((a, b) => b.value - a.value).slice(0, 5)
  } catch { users.value = [] }
}

onMounted(() => {
  fetch()
  timer = setInterval(fetch, API_INTERVAL)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>