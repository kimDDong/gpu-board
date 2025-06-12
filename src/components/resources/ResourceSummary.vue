<!-- src/components/ResourceSummary.vue -->
<template>
  <v-row>
    <v-col cols="12" md="4">
      <v-card color="primary" class="text-white pa-4">
        <div class="text-h6">전체 자원</div>
        <div class="text-h4">{{ data.total }}개</div>
        <v-progress-linear :value="(data.used / data.total) * 100" height="8" color="lime"></v-progress-linear>
        <div>사용중: {{ data.used }} / 유휴: {{ data.idle }}</div>
      </v-card>
    </v-col>
    <v-col cols="6" md="4">
      <v-card color="deep-purple lighten-1" class="text-white pa-4">
        <div class="text-h6">GPU</div>
        <div class="text-h4">{{ data.gpu_used }} / {{ data.gpu_total }}</div>
      </v-card>
    </v-col>
    <v-col cols="6" md="4">
      <v-card color="cyan darken-1" class="text-white pa-4">
        <div class="text-h6">CPU</div>
        <div class="text-h4">{{ data.cpu_used }} / {{ data.cpu_total }}</div>
      </v-card>
    </v-col>
  </v-row>
</template>
<script setup>
const props = defineProps({ data: Object })
</script>
