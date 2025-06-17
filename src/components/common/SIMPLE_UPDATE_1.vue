<template>
  <v-card height="100%" elevation="2" class="pa-4 d-flex flex-column align-center justify-center">
    <div class="text-caption mb-2 font-weight-bold">SIMPLE_UPDATE_1</div>
    <template v-if="SIMPLE_DATA !== null">
      <v-progress-circular :size="100" :width="10" :model-value="SIMPLE_DATA" color="primary">
        <span class="text-h6">{{ SIMPLE_DATA }}%</span>
      </v-progress-circular>
    </template>
    <template v-else>
      <v-progress-circular indeterminate :size="100" :width="10">
        <span class="text-h6">%</span>
      </v-progress-circular>
    </template>
  </v-card>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

const props = defineProps({
  startDate: {
    type: String,
    required: true,
    validator: (value) => /^\d{8}$/.test(value), // YYYYMMDD 형식 검증
  },
  endDate: {
    type: String,
    required: true,
    validator: (value) => /^\d{8}$/.test(value), // YYYYMMDD 형식 검증
  },
});

const API_URL = 'https://gpu-board.onrender.com:8000/api/simple/1'
const SIMPLE_DATA = ref(null)

async function fetch() {
  try {
    const res = await axios.get(API_URL)
    SIMPLE_DATA.value = res.data.value
  } catch (e) {
    SIMPLE_DATA.value = null
  }
}

watch([() => props.startDate, () => props.endDate], async () => {
  fetch();
});

onMounted(() => {
  fetch()
})
</script>

<style scoped>
.caption {
  font-size: 0.85rem;
}
</style>