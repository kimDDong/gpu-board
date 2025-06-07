<!-- src/components/BarSummary.vue -->
<template>
  <v-row>
    <v-col cols="6" v-for="t in ['GPU','CPU']" :key="t">
      <v-card class="mb-2">
        <v-card-title>{{ t }} 사용 현황</v-card-title>
        <v-card-text>
          <div>
            총 {{ summary[t]?.total ?? '-' }} |  
            사용중 {{ summary[t]?.used ?? '-' }}  
            | 잔여 {{ summary[t]?.idle ?? '-' }}
          </div>
          <v-progress-linear
            :model-value="summary[t]?.used_percent || 0"
            height="20"
            color="primary"
            striped
            >
            <template #default>
              <span>{{ summary[t]?.used_percent || 0 }}%</span>
            </template>
          </v-progress-linear>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const summary = ref({})
onMounted(async () => {
  summary.value = (await axios.get('http://127.0.0.1:5000/api/reports/summary')).data
})
</script>
