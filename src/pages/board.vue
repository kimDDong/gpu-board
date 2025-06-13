<script setup>
import KPI_CPU from '@/components/dashboard/KPI_CPU.vue'
import KPI_GPU from '@/components/dashboard/KPI_GPU.vue'
import KPI_MEM from '@/components/dashboard/KPI_MEM.vue'
import KPI_IDLE from '@/components/dashboard/KPI_IDLE.vue'
import KPI_INFO from '@/components/dashboard/KPI_INFO.vue'
import CPU_BARS from '@/components/dashboard/CPU_BARS.vue'
import CPU_CHART from '@/components/dashboard/CPU_CHART.vue'
import GPU_BARS from '@/components/dashboard/GPU_BARS.vue'
import GPU_CHART from '@/components/dashboard/GPU_CHART.vue'
import GPU_TEMP from '@/components/dashboard/GPU_TEMP.vue'
import USER_CPU from '@/components/dashboard/CPU_RANK.vue'
import USER_GPU from '@/components/dashboard/GPU_RANK.vue'
import USER_MEM from '@/components/dashboard/MEM_RANK.vue'
import USER_IDLE from '@/components/dashboard/IDLE_RANK.vue'

</script>

<template>
  <v-container fluid class="pa-4" style="height:100vh;width:100vw;">

    <v-row>
      <v-col>
        <KPI_CPU />
      </v-col>
      <v-col>
        <KPI_GPU />
      </v-col>
      <v-col>
        <KPI_MEM />
      </v-col>
      <v-col>
        <KPI_IDLE />
      </v-col>
      <v-col>
        <KPI_INFO />
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <CPU_CHART />
      </v-col>
      <v-col>
        <CPU_BARS />
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <GPU_CHART />
      </v-col>
      <v-col>
        <v-row>
          <v-col>
            <GPU_BARS />
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <GPU_TEMP />
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <USER_CPU />
      </v-col>
      <v-col>
        <USER_GPU />
      </v-col>
      <v-col>
        <USER_MEM />
      </v-col>
      <v-col>
        <USER_IDLE />
      </v-col>
    </v-row>
  </v-container>
</template>