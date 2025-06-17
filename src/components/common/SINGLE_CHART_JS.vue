<template>
  <v-card height="100%" elevation="2" class="pa-4 d-flex flex-column align-center justify-center">
    <div class="chart-wrapper">
      <canvas ref="singleChartCanvas"></canvas>
    </div>
  </v-card>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { Chart, registerables } from 'chart.js';
import 'chartjs-adapter-date-fns'; // Chart.js Time Scale 어댑터
import axios from 'axios';

const props = defineProps({
  startDate: {
    type: String,
    required: true,
    validator: (value) => /^\d{8}$/.test(value), // YYYYMMDD 형식 검증
  },
  endDate: {
    type: String,
    required: true,
    validator: (value) => /^\d{8}$/.test(value), // YYYYMMDD 형식 검증
  },
});

Chart.register(...registerables);

const API_URL = 'https://gpu-board.onrender.com:8000/api/chartjs/single'; // API 엔드포인트 변경
const SINGLE_SERIES = ref([]); // 단일 시리즈 데이터를 저장할 ref

const singleChartCanvas = ref(null); // canvas 엘리먼트의 참조
const chartInstance = ref(null);      // Chart.js 인스턴스

async function fetch() {
  try {
    const res = await axios.get(API_URL + `?start=${props.startDate}&end=${props.endDate}`);
    SINGLE_SERIES.value = res.data;
  } catch (e) {
    SINGLE_SERIES.value = []; // 에러 발생 시 데이터 초기화
  }
}

// Chart.js를 사용하여 차트를 그리는 함수
const renderChartJS = () => {

  if (!SINGLE_SERIES.value || SINGLE_SERIES.value.length === 0 || !singleChartCanvas.value) {
    if (chartInstance.value) {
      chartInstance.value.destroy();
      chartInstance.value = null;
    }
    return;
  }

  // 데이터셋 구성 (단일 시리즈)
  const labels = SINGLE_SERIES.value.map(dataPoint => dataPoint.timestamp);

  const datasets = [{
    label: props.chartTitle, // 차트 제목을 그대로 라벨로 사용하거나 다른 라벨 prop을 만들 수 있음
    data: SINGLE_SERIES.value.map(dataPoint => dataPoint.value), // 'value' 필드 사용
    borderColor: 'rgb(54, 162, 235)', // 단일 라인이므로 고정 색상
    borderWidth: 1, // 선 두께를 얇게
    tension: 0.1,
    fill: false,
    pointRadius: 0, // 포인트 제거
    pointHitRadius: 0, // 마우스 오버 시 감지 영역 제거
  }];

  // 캔버스 컨텍스트 가져오기 및 차트 인스턴스 생성/업데이트
  const ctx = singleChartCanvas.value.getContext('2d');
  if (chartInstance.value) {
    chartInstance.value.destroy(); // 기존 차트 인스턴스 파괴
  }

  chartInstance.value = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      elements: { // 전역으로 선 두께와 포인트 제거 설정
        line: { borderWidth: 0.5 },
        point: { radius: 0, hitRadius: 0 }
      },
      plugins: {
        title: { display: true, text: 'SINGLE_CHART_JS', font: { size: 16 } },
        tooltip: { mode: 'index', intersect: false },
        legend: { display: false }, // 단일 라인이므로 범례는 숨김
      },
      scales: {
        x: {
          type: 'time', // Time Scale
          time: {
            unit: 'day', // 기본 표시 단위
            tooltipFormat: 'yyyy-MM-dd HH:mm', // 툴팁 형식
            displayFormats: { // 확대/축소 수준별 표시 형식
              millisecond: 'HH:mm:ss.SSS',
              second: 'HH:mm:ss',
              minute: 'HH:mm',
              hour: 'HH:mm',
              day: 'MMM d',    // 1월 1일
              week: 'MMM d',
              month: 'MMM yyyy', // 1월 2025
              quarter: 'MMM yyyy',
              year: 'yyyy'
            }
          },
          title: { display: true, text: '시간' }
        },
        y: {
          title: { display: true, text: '사용률 (%)' },
          min: 0,
          max: 100,
          ticks: { callback: value => `${value}%` }
        }
      },
    },
  });
};

watch([() => props.startDate, () => props.endDate], async () => {
  await fetch();
  renderChartJS();
});

// 컴포넌트 마운트 시 초기 데이터 로드 및 차트 렌더링
onMounted(async () => {
  await fetch(); // API에서 시계열 데이터 받아오기
  renderChartJS(); // 데이터를 성공적으로 받아온 후 차트 그리기
});

// 컴포넌트 파괴 시 차트 인스턴스 정리
onBeforeUnmount(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy();
  }
});
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  height: 350px;
  /* 싱글 차트이므로 높이를 줄여봤습니다. 필요시 조정 */
  position: relative;
}

canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>