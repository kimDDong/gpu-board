<script setup>
import KPI from '@/components/dashboard/KPI.vue'
import CPU_1 from '@/components/dashboard/CPU_1.vue'
import CPU_2 from '@/components/dashboard/CPU_2.vue'
import GPU_1 from '@/components/dashboard/GPU_1.vue'
import GPU_2 from '@/components/dashboard/GPU_2.vue'
import USER_CPU from '@/components/dashboard/USER_CPU.vue'
import USER_GPU from '@/components/dashboard/USER_GPU.vue'
import USER_MEM from '@/components/dashboard/USER_MEM.vue'
import USER_IDLE from '@/components/dashboard/USER_IDLE.vue'

</script>

<template>
  <v-container fluid class="pa-4" style="height:100vh;width:100vw;">

    <KPI />

    <v-row>
      <v-col>
        <CPU_2 />
      </v-col>  
      <v-col>
        <CPU_1 />
      </v-col>  
    </v-row>

    <v-row>
      <v-col>
        <GPU_2 />
      </v-col>  
      <v-col>
        <v-row>
        <v-col><GPU_1 /></v-col>
        </v-row>
        <v-row>
        <v-col><GPU_3 /></v-col>
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