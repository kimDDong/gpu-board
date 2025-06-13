<template>
  <!-- GPU 온도 여러개 토글 -->
  <v-row>
    <v-col cols="12">
      <v-card class="pa-3 mb-2" style="border:1.5px solid #e0e0e0;">
        <div class="d-flex align-center mb-2">
          <div class="text-h6">GPU 개별 온도(°C)</div>
          <v-select
            :items="gpuNames"
            :model-value="selectedGpuTemps"
            @update:model-value="val => $emit('update:selectedGpuTemps', val)"
            label="GPU 선택"
            multiple
            dense
            class="ml-4"
            style="max-width:350px"
            chips
          />
        </div>
        <div style="min-height:170px;">
          <LineChart
            v-if="gpuTempsChartData"
            :chart-data="gpuTempsChartData"
            :options="gpuTempLineOptions"
            title="GPU 온도"
          />
        </div>
      </v-card>
    </v-col>
  </v-row>
  <!-- GPU 개별 사용량 -->
  <v-row>
    <v-col cols="12">
      <v-card class="pa-3 mb-2" style="border:1.5px solid #e0e0e0;">
        <div class="d-flex align-center mb-2">
          <div class="text-h6">GPU 개별 사용량</div>
          <v-select
            :items="gpuNames"
            :model-value="selectedGpu"
            @update:model-value="val => $emit('update:selectedGpu', val)"
            label="GPU 선택"
            dense
            class="ml-4"
            style="max-width:150px"
          />
        </div>
        <div style="min-height:170px;">
          <LineChart v-if="gpuDetailChartData" :chart-data="gpuDetailChartData" :options="gpuLineOptions" title="GPU 개별 사용량" />
        </div>
      </v-card>
    </v-col>
  </v-row>
  <v-row>
    <v-col cols="12" md="6">
      <v-card class="pa-3 mb-2" style="border:1.5px solid #e0e0e0;">
        <div class="d-flex align-center mb-2">
          <div class="text-h6">CPU 개별 사용량</div>
          <v-select
            :items="cpuNames"
            :model-value="selectedCpu"
            @update:model-value="val => $emit('update:selectedCpu', val)"
            label="CPU 선택"
            dense
            class="ml-4"
            style="max-width:150px"
          />
        </div>
        <div style="min-height:170px;">
          <LineChart v-if="cpuDetailChartData" :chart-data="cpuDetailChartData" :options="cpuLineOptions" title="CPU 개별 사용량" />
        </div>
      </v-card>
    </v-col>
    <v-col cols="12" md="6">
      <v-card class="pa-3 mb-2" style="border:1.5px solid #e0e0e0;">
        <div class="d-flex align-center mb-2">
          <div class="text-h6">Memory 개별 사용량</div>
          <v-select
            :items="memoryNames"
            :model-value="selectedMemory"
            @update:model-value="val => $emit('update:selectedMemory', val)"
            label="Memory 선택"
            dense
            class="ml-4"
            style="max-width:150px"
          />
        </div>
        <div style="min-height:170px;">
          <LineChart v-if="memoryDetailChartData" :chart-data="memoryDetailChartData" :options="memoryLineOptions" title="Memory 개별 사용률(%)" />
        </div>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import LineChart from '@/components/resources/LineChart.vue'
defineProps({
  gpuNames: Array,
  selectedGpuTemps: Array,
  gpuTempsChartData: Object,
  gpuTempLineOptions: Object,
  selectedGpu: String,
  gpuDetailChartData: Object,
  gpuLineOptions: Object,
  cpuNames: Array,
  selectedCpu: String,
  cpuDetailChartData: Object,
  cpuLineOptions: Object,
  memoryNames: Array,
  selectedMemory: String,
  memoryDetailChartData: Object,
  memoryLineOptions: Object
})
</script>
