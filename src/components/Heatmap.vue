<template>
  <v-card class="my-5">
    <v-card-title>{{ resourceType }} 월별 사용 히트맵</v-card-title>
    <v-card-text>
      <div style="overflow-x:auto;">
        <table style="border-collapse: collapse;">
          <thead>
            <tr>
              <th style="width: 50px;">ID</th>
              <th v-for="d in days" :key="d" style="font-size:10px; min-width: 25px;">
                {{ d.slice(8) }}<br/><span style="font-size:9px;">{{ ['일','월','화','수','목','금','토'][new Date(d).getDay()] }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in heatmap" :key="row.res_id">
              <td style="text-align:center">{{ row.res_id }}</td>
              <td v-for="(u,i) in row.usage" :key="i"
                :style="{
                  background: u === 1 ? '#42a5f5' : u === 2 ? '#e53935' : '#ececec',
                  width:'20px', height:'26px',
                  border: u === 2 ? '1px solid #b71c1c' : '1px solid #fff',
                  cursor: u ? 'pointer' : 'default'
                }"
                :title="u === 1 ? '사용중' : (u === 2 ? '중복 할당' : '유휴')"
              ></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div style="font-size:12px;" class="mt-2">
        <span style="display:inline-block;width:16px;height:16px;background:#42a5f5;margin-right:4px;border:1px solid #888;"></span> 사용중
        <span style="display:inline-block;width:16px;height:16px;background:#ececec;margin:0 4px;border:1px solid #ccc;"></span> 유휴
        <span style="display:inline-block;width:16px;height:16px;background:#e53935;margin:0 4px;border:1px solid #b71c1c;"></span> 중복/과할당
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

onMounted(fetchHeatmap)
watch(() => props.resourceType, fetchHeatmap)

async function fetchHeatmap() {
  const res = (await axios.get('http://127.0.0.1:5000/api/reports/heatmap')).data
  days.value = res.days
  // 값: 0=유휴, 1=사용중, 2=중복/과할당 등 가시적으로 조정
  // API에서 2를 반환하지 않으면 1/0만 나옴
  heatmap.value = res.heatmap[props.resourceType]
}
</script>
