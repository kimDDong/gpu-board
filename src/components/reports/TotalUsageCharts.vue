<template>
  <v-row class="mb-4">
    <v-col cols="12" md="6">
      <v-card class="pa-4 mb-2" style="border:1.5px solid #e0e0e0;">
        <div style="min-height:170px;">
          <LineChart v-if="usageLoaded"
            :chart-data="cpuUsageChartData"
            :options="cpuLineOptions"
            title="CPU 전체 사용량" />
          <div v-else>Loading...</div>
        </div>
      </v-card>
    </v-col>
    <v-col cols="12" md="6">
      <v-card class="pa-4 mb-2" style="border:1.5px solid #e0e0e0;">
        <div style="min-height:170px;">
          <LineChart v-if="usageLoaded"
            :chart-data="memoryUsageChartData"
            :options="memoryLineOptions"
            title="Memory 전체 사용량" />
          <div v-else>Loading...</div>
        </div>
      </v-card>
    </v-col>
  </v-row>
  <v-row class="mb-6">
    <v-col cols="12">
      <v-card class="pa-4" style="border:2.5px solid #e0e0e0;">
        <div style="min-height:230px;">
          <LineChart v-if="usageLoaded"
            :chart-data="gpuUsageChartData"
            :options="gpuLineOptions"
            title="GPU 전체 사용량" />
          <div v-else>Loading...</div>
        </div>
      </v-card>
    </v-col>
  </v-row>
</template>
<script setup>
import LineChart from '@/components/resources/LineChart.vue'
defineProps({
  usageLoaded: Boolean,
  cpuUsageChartData: Object,
  memoryUsageChartData: Object,
  gpuUsageChartData: Object,
  cpuLineOptions: Object,
  memoryLineOptions: Object,
  gpuLineOptions: Object,
})
</script>
