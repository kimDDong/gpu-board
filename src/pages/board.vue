<script setup>
import KPI from '@/components/dashboard/KPI.vue'
import CPU_1 from '@/components/dashboard/CPU_1.vue'
import CPU_2 from '@/components/dashboard/CPU_2.vue'
import GPU_1 from '@/components/dashboard/GPU_1.vue'
import GPU_2 from '@/components/dashboard/GPU_2.vue'

</script>

<template>
  <v-container fluid>

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
        <GPU_1 />
      </v-col>  
    </v-row>
    
  </v-container>
</template>