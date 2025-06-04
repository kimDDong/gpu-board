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
        <tr v-for="(user, idx) in top5" :key="user.user">
          <td>{{ idx+1 }}</td>
          <td>{{ user.user }}</td>
          <td>
              {{ user.idle }}
          </td>
        </tr>
        <tr v-if="!top5.length"><td colspan="3"><v-skeleton-loader type="table-row"/></td></tr>
      </tbody>
    </v-table>
  </v-card>
</template>
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
const top5 = ref([])
let timer = null
const INTERVAL_MILLIS = 2000

async function fetchRank() {
 try {
    const res = await axios.get('http://localhost:8000/api/idle_user_rank')
    top5.value = res.data.users.sort((a, b) => b.idle - a.idle).slice(0,5)
  } catch { top5.value = [] }
}
onMounted(() => {
 fetchRank()
  timer = setInterval(fetchRank, INTERVAL_MILLIS)
});
onUnmounted(() => timer && clearInterval(timer));
</script>