<template>
  <v-card class="pa-4" elevation="2">
    <div class="font-weight-bold mb-2">GPU TOP5 사용자</div>
    <v-table density="compact">
      <thead>
        <tr>
          <th>순위</th>
          <th>사용자</th>
          <th>GPU(%)</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(user, idx) in top5" :key="user.user">
          <td>{{ idx+1 }}</td>
          <td>{{ user.user }}</td>
          <td>
            <v-progress-linear :model-value="user.gpu" :color="getColor(user.gpu)" height="16" striped>
              {{ user.gpu }}%
            </v-progress-linear>
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

function getColor(val) {
  if (val >= 80.0) return 'red'       // 위험(빨강)
  if (val >= 50.0) return 'orange'   // 주의(주황)
  return 'primary'
}

async function fetchRank() {
 try {
    const res = await axios.get('http://localhost:8000/api/gpu_user_rank')
    top5.value = res.data.users.sort((a, b) => b.gpu - a.gpu).slice(0,5)
  } catch { top5.value = [] }
}
onMounted(() => {
 fetchRank()
  timer = setInterval(fetchRank, INTERVAL_MILLIS)
});
onUnmounted(() => timer && clearInterval(timer));
</script>