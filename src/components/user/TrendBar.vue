<template>
  <div class="trend-container">
    <v-progress-linear :model-value="previous" height="10" color="grey lighten-2" class="mb-1" />
    <div class="text-caption">이전 7일: {{ previous }}%</div>
    <v-progress-linear :model-value="current" height="10" color="primary" class="mt-2 mb-1" />
    <div class="text-caption">최근 7일: {{ current }}%</div>
  </div>
</template>

<script setup>
defineProps({
  previous: Number,
  current: Number
})
</script>

<style scoped>
.trend-container {
  padding: 4px 0;
}
</style>
