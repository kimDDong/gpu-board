<template>
  <div class="chart-wrapper">
    <canvas ref="mulitChartCanvas"></canvas>
  </div>
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

const API_URL = 'http://localhost:8000/api/chartjs/multi'
const MULTI_SERIES = ref([]);

const mulitChartCanvas = ref(null);
const chartInstance = ref(null);

async function fetch() {
  try {
    const res = await axios.get(API_URL + `?start=${props.startDate}&end=${props.endDate}`);
    MULTI_SERIES.value = res.data;
  } catch (e) {
    MULTI_SERIES.value = []; // 에러 발생 시 데이터 초기화
  }
}

// --- 각 선에 다른 색상을 할당하기 위한 헬퍼 함수 ---
const getLineColor = (index) => {
  const colors = [
    'rgb(255, 99, 132)',  // Red
    'rgb(54, 162, 235)',  // Blue
    'rgb(255, 206, 86)',  // Yellow
    'rgb(75, 192, 192)',  // Green
    'rgb(153, 102, 255)', // Purple
    'rgb(255, 159, 64)',  // Orange
    'rgb(200, 200, 200)', // Grey
    'rgb(100, 100, 255)', // Light Blue
    'rgb(128, 0, 0)',     // Maroon
    'rgb(0, 128, 128)'    // Teal
  ];
  return colors[index % colors.length]; // GPU 인덱스에 따라 색상 순환
};

// Chart.js를 사용하여 차트를 그리는 함수
const renderChartJS = () => {

  if (!MULTI_SERIES.value || MULTI_SERIES.value.length === 0 || !mulitChartCanvas.value) {
    if (chartInstance.value) {
      chartInstance.value.destroy();
      chartInstance.value = null;
    }
    return;
  }

  // 데이터셋 구성
  const labels = MULTI_SERIES.value.map(dataPoint => dataPoint.timestamp); // Chart.js Time Scale이 ISO 문자열 파싱
  const ids = new Set(); // 고유 ID 수집

  MULTI_SERIES.value.forEach(dataPoint => {
    dataPoint.datas.forEach(gpu => ids.add(gpu.id));
  });

  const sortedGpuIds = Array.from(ids).sort((a, b) => a - b);
  const datasets = sortedGpuIds.map(gpuId => ({
    label: `ITEM ${gpuId}(클릭,토글)`,
    data: MULTI_SERIES.value.map(dataPoint => {
      const gpuEntry = dataPoint.datas.find(gpu => gpu.id === gpuId);
      return gpuEntry ? gpuEntry.value : null; // 데이터 없으면 null
    }),
    borderColor: getLineColor(gpuId),
    borderWidth: 1,
    tension: 0.1,
    fill: false,
    pointRadius: 0, // <-- 이 부분 추가: 포인트 반지름을 0으로 설정
    pointHitRadius: 0, // <-- 이 부분 추가: 마우스 오버 시 감지 영역도 0으로 설정 (선택 사항)
  }));

  // 캔버스 컨텍스트 가져오기 및 차트 인스턴스 생성/업데이트
  const ctx = mulitChartCanvas.value.getContext('2d');
  if (chartInstance.value) {
    chartInstance.value.destroy(); // 기존 차트 인스턴스 파괴
  }

  chartInstance.value = new Chart(ctx, { // ChartJS 대신 Chart 사용
    type: 'line',
    data: { labels, datasets }, // 간결한 객체 리터럴
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: { display: true, text: 'MULTI-CHART-JS', font: { size: 16 } },
        tooltip: { mode: 'index', intersect: false },
        legend: { display: true }, // Chart.js 기본 범례 사용
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

// 컴포넌트가 DOM에 마운트된 후 실행될 로직
onMounted(async () => {
  await fetch();
  renderChartJS();
});

// 컴포넌트가 파괴되기 전에 실행될 로직
onBeforeUnmount(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy(); // Chart.js 인스턴스 정리
  }
});

</script>


<style scoped>
.chart-wrapper {
  width: 100%;
  height: 300px;
  /* 차트 높이 조정 */
  position: relative;
}

canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>
