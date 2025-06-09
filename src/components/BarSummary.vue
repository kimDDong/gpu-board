<template>
  <v-row>
    <v-col cols="12" v-if="!resourceType">
      <v-card v-for="t in ['GPU','CPU']" :key="t" class="mb-2">
        <v-card-title>{{ t }} 사용 현황</v-card-title>
        <v-card-text>
          <div>
            총 {{ summary[t]?.total ?? '-' }} |
            사용중 {{ summary[t]?.used ?? '-' }} |
            잔여 {{ summary[t]?.idle ?? '-' }}
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
    <v-col cols="12" v-else>
      <v-card class="mb-2">
        <v-card-title>{{ resourceType }} 사용 현황</v-card-title>
        <v-card-text>
          <div>
            총 {{ summary[resourceType]?.total ?? '-' }} |
            사용중 {{ summary[resourceType]?.used ?? '-' }} |
            잔여 {{ summary[resourceType]?.idle ?? '-' }}
          </div>
          <v-progress-linear
            :model-value="summary[resourceType]?.used_percent || 0"
            height="20"
            color="primary"
            striped
          >
            <template #default>
              <span>{{ summary[resourceType]?.used_percent || 0 }}%</span>
            </template>
          </v-progress-linear>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
const props = defineProps({ resourceType: String })
const summary = ref({})

async function fetchSummary() {
  const res = (await axios.get('http://127.0.0.1:5000/api/reports/summary')).data
  summary.value = res
}
onMounted(fetchSummary)
watch(() => props.resourceType, fetchSummary)
</script>
