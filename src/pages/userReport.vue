<template>
  <v-container fluid class="pa-4" style="height:100vh;width:100vw;">

    <v-row>
      <v-col>
        <v-card-text class="py-4">
          <span style="font-size: 200%;">
            {{ user.name }} 님의 리소스 사용 레포트
          </span>
        </v-card-text>
      </v-col>
    </v-row>

    <!-- 날짜 선택 UI -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-menu v-model="startDateMenu" :close-on-content-click="false" transition="scale-transition" offset-y
          min-width="auto">
          <template v-slot:activator="{ props }">
            <v-text-field v-model="selectedStartDate" label="시작 날짜" prepend-icon="mdi-calendar" readonly v-bind="props"
              hide-details />
          </template>
          <v-date-picker v-model="selectedStartDate" type="string" no-title scrollable
            @update:modelValue="date => { startDateMenu = false; selectedStartDate = formatDateToString(date); }"
            locale="ko-KR" />
        </v-menu>
      </v-col>
      <v-col cols="12" md="6">
        <v-menu v-model="endDateMenu" :close-on-content-click="false" transition="scale-transition" offset-y
          min-width="auto">
          <template v-slot:activator="{ props }">
            <v-text-field v-model="selectedEndDate" label="종료 날짜" prepend-icon="mdi-calendar" readonly v-bind="props"
              hide-details />
          </template>
          <v-date-picker v-model="selectedEndDate" type="string" no-title scrollable
            @update:modelValue="date => { endDateMenu = false; selectedEndDate = formatDateToString(date); }"
            locale="ko-KR" />
        </v-menu>
      </v-col>
    </v-row>



    <v-row>
      <v-col>
        <!-- selectedStartDate의 값을 직접 YYYYMMDD로 변환하여 전달 -->
        <GPU_CHART :startDate="selectedStartDate ? selectedStartDate.replace(/-/g, '') : ''"
          :endDate="selectedEndDate ? selectedEndDate.replace(/-/g, '') : ''" />
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <!-- selectedStartDate의 값을 직접 YYYYMMDD로 변환하여 전달 -->
        <CPU_CHART :startDate="selectedStartDate ? selectedStartDate.replace(/-/g, '') : ''"
          :endDate="selectedEndDate ? selectedEndDate.replace(/-/g, '') : ''" />
      </v-col>
      <v-col>
        <!-- selectedStartDate의 값을 직접 YYYYMMDD로 변환하여 전달 -->
        <CPU_CHART :startDate="selectedStartDate ? selectedStartDate.replace(/-/g, '') : ''"
          :endDate="selectedEndDate ? selectedEndDate.replace(/-/g, '') : ''" />
      </v-col>
    </v-row>

  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router'
import GPU_CHART from '@/components/user/GPU_CHART.vue'; // 실제 경로에 맞게 수정
import CPU_CHART from '@/components/user/CPU_CHART.vue';
import MEM_CHART from '@/components/user/MEM_CHART.vue';

const selectedStartDate = ref('2025-01-01');
const selectedEndDate = ref('2025-01-31');
const startDateMenu = ref(false);
const endDateMenu = ref(false);

function formatDateToString(date) {
  if (!date) return ''; // null 또는 undefined 처리
  if (typeof date === 'string') return date; // 이미 문자열이면 그대로 반환

  if (date instanceof Date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
  return ''; // 그 외의 경우 (예: 숫자가 들어온 경우)
}

// user 객체 선언
const user = ref({ name: '사용자' })  // 초기값 설정 (혹은 빈 객체로 시작 가능)
const route = useRoute()

// 컴포넌트 마운트 시 유저 데이터 fetch
onMounted(async () => {
  try {
    const id = route.query.id  // 예: /users/:id/report?id=3
    const res = await fetch(`https://gpu-board.onrender.com/api/users/${id}/report`)
    const data = await res.json()
    user.value = data  // name, cpu/gpu/mem 등 포함되도록 백엔드 구조에 맞게
  } catch (err) {
    console.error('유저 정보 로드 실패:', err)
    user.value.name = '알 수 없음'
  }
})

</script>