<!-- src/components/ResourceCalendar.vue -->
<template>
  <div style="background: white; border-radius:16px; padding:12px">
    <FullCalendar :events="events" :initial-view="'dayGridMonth'" :header-toolbar="{
      left: 'prev,next today',
      center: 'title',
      right: ''
    }" :event-color="'#1976d2'" height="480px" />
  </div>
</template>
<script setup>
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import { onMounted, ref } from 'vue'
import axios from 'axios'
const events = ref([])
onMounted(async () => {
  events.value = (await axios.get('http://localhost:8000/api/reports/calendar')).data
})
</script>
<style>
@import "@fullcalendar/core/main.css";
@import "@fullcalendar/daygrid/main.css";
</style>
