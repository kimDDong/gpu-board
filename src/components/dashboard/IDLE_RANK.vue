<template>
  <v-card class="pa-4" elevation="2">
    <div class="font-weight-bold mb-2">IDLE TIME TOP5 사용자</div>
    <v-table density="compact">
      <thead>
        <tr>
          <th>순위</th>
          <th>사용자</th>
          <th>IdleTime(분)</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(user, idx) in USERS_IDLE" :key="user.user">
          <td>{{ idx + 1 }}</td>
          <td>
            <router-link :to="`/user/${user.user}/report`">{{ user.user }}</router-link>

          </td>
          <td>
            {{ user.value }}
          </td>
        </tr>
        <tr v-if="!USERS_IDLE.length">
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
const API_URL = 'http://localhost:8000/api/idle_user_rank'
const USERS_IDLE = ref([])

let timer = null

async function fetch() {
  try {
    const res = await axios.get(API_URL)
    USERS_IDLE.value = res.data.users.sort((a, b) => b.value - a.value).slice(0, 5)
  } catch { USERS_IDLE.value = [] }
}

onMounted(() => {
  fetch()
  timer = setInterval(fetch, API_INTERVAL)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>