<template>
  <v-card class="my-5">
    <v-card-title>{{ resourceType }} 월별 사용 히트맵</v-card-title>
    <v-card-text>
      <div style="overflow-x:auto;">
        <table style="border-collapse: collapse;">
          <thead>
            <tr>
              <th style="width: 50px;">ID</th>
              <th v-for="d in days" :key="d" style="font-size:10px; min-width: 25px;">{{ d.slice(8) }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in heatmap" :key="row.res_id">
              <td style="text-align:center">{{ row.res_id }}</td>
              <td v-for="(u,i) in row.usage" :key="i"
                :style="{
                  background: u ? '#80cbc4':'#ececec',
                  width:'20px', height:'24px',
                  border: u ? '1px solid #009688' : '1px solid #eee'
                }"
              ></td>
            </tr>
          </tbody>
        </table>
      </div>
    </v-card-text>
  </v-card>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
const props = defineProps({ resourceType: String })
const days = ref([])
const heatmap = ref([])
async function fetchHeatmap(type) {
  const res = (await axios.get('http://127.0.0.1:5000/api/reports/heatmap')).data
  days.value = res.days
  heatmap.value = res.heatmap[type]
}
onMounted(() => fetchHeatmap(props.resourceType))
watch(() => props.resourceType, fetchHeatmap)
</script>
