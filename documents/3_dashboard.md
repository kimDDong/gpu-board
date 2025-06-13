# 3. 대시보드

대시보드의 `XMLHttpRequests` 기반의 실시간 모니터링 기능은 Promise 기반 HTTP 클라이언트 라이브러리 Axios를 이용해 구현되었습니다.

(참고: [Axios]( https://axios-http.com/kr/docs/intro))

## 3.1 관련 파일 구성
```
src
├── components
│   └── dashboard
│       ├── KPI_CPU.vue
│       ├── KPI_GPU.vue
│       ├── KPI_MEM.vue
│       ├── KPI_IDLE.vue
│       ├── KPI_INFO.vue
│       ├── CPU_BARS.vue
│       ├── GPU_BARS.vue
│       ├── GPU_TEMP.vue
│       ├── CPU_CHART.vue
│       ├── GPU_CHART.vue
│       ├── CPU_RANK.vue
│       ├── GPU_RANK.vue
│       ├── MEM_RANK.vue
│       └── IDLE_RANK.vue
└── pages
    └── board.vue
```
1. `KPI_CPU.vue` : 전체 CPU 사용률을 간략하게 표시(실시간)
1. `KPI_GPU.vue` : 전체 GPU 사용률을 간략하게 표시(실시간)
1. `KPI_MEM.vue` : 전체 MEM 사용률을 간략하게 표시(실시간)
1. `KPI_IDLE.vue` : 전체 누적 IDEL 시간을 간략하게 표시(실시간)
1. `KPI_INFO.vue` : 시스템의 HW 정보 간략하게 표시
1. `CPU_BARS.vue` : 개별 CPU의 상세 사용률을 막대 그래프 형태 표시 (실시간)
1. `GPU_BARS.vue` : 개별 GPU의 상세 사용률을 바 형태 표시 (실시간)
1. `GPU_TEMP.vue` : 개별 GPU의 상세 사용률을 바 형태 표시 (실시간)
1. `CPU_CHART.vue` : 시간에 따른 전체 CPU 사용률을 차트 형태 표시 (실시간, 누적)
1. `GPU_CHART.vue` : 시간에 따른 개별 GPU 사용률을 차트 형태 표시 (실시간, 누적)
1. `CPU_RANK.vue` : CPU 사용률이 높은 상위 5명의 사용자를 목록으로 표시 (실시간)
1. `GPU_RANK.vue` : GPU 사용률이 높은 상위 5명의 사용자를 목록으로 표시 (실시간)
1. `MEM_RANK.vue` : MEM 사용률이 높은 상위 5명의 사용자를 목록으로 표시 (실시간)
1. `IDLE_RANK.vue` : IDLE 시간이 가장 긴 상위 5명의 사용자를 목록으로 표시 (실시간)


## 3.2 `KPI_CPU.vue`, `KPI_GPU.vue`, `KPI_MEM.vue`

### 기능 설명:
- API를 통해 주기적으로 각 자원의 전체 사용률을 받아옵니다.
- 데이터 로딩 중에는 인디케이터(무한 로딩)로 표시합니다.
- 값을 불러오면 원형 프로그레스바에 퍼센트를 표시합니다.
- 사용하는 값에 따라 색상이 변경됩니다(설정 가능): 
    - 90% 이상 : 빨간색 (위험) 
    - 80% 이상 : 주황색 (주의) 

### 주요 데이터 바인딩 
- `const {cpu | gpu | mem} = ...` : API 에서 받아온 실시간 사용률 값 저장용(JSON)
    ```
    // JSON Format
    { value: 0}
    ```
- `const API_INTERVAL = ...` : API 호출 주기(업데이트 주기)
- `const API_URL = ...` : API 호출 URL 주소
- `const DANGER_LEVEL = ...` : 해당 수준을 넘을 경우 인디케이터 색상을 빨간색으로 변경 
- `const WARNING_LEVEL = ...` : 해당 수준을 넘을 경우 인디케이터 색상을 주황색으로 변경 

## 3.3 `KPI_IDLE.vue`

### 기능 설명:
- API를 통해 주기적으로 시스템의 전체 IDLE 시간을 받아옵니다.
- 데이터 로딩 중에는 ...으로 표시합니다.
- 값을 불러오면 누적 분을 표시합니다.

### 주요 데이터 바인딩 
- `const idletime = ...` : API 에서 받아온 누적 IDLE 시간 저장용(JSON)
    ```
    // JSON Format
    { value: 0}
    ```
- `const API_INTERVAL = ...` : API 호출 주기(업데이트 주기)
- `const API_URL = ...` : API 호출 URL 주소


## 3.4 `KPI_INFO.vue`

### 기능 설명:
- API를 통해 시스템 HW 정보 및 Uptime을 받아옵니다.
- HW 정보는 페이지 로딩시 최초 한번만 받아옵니다.
- Uptime은 API를 통해 주기적으로 업데이트 됩니다.
- CPU 개수, GPU 개수, 전체 MEM 크기, UPTIME 누적 시간 표시

### 주요 데이터 바인딩 
- `const cpucnt = ...` : API 에서 받아온 cpu 개수 저장용(JSON)
- `const gpucnt = ...` : API 에서 받아온 cpu 개수 저장용(JSON)
- `const totalmem = ...` : API 에서 받아온 전체 mem 크기 저장용(JSON)
- `const uptime = ...` : API 에서 받아온 누적 Uptime 저장용(JSON)
    ```
    // JSON Format
    { value: 0}
    ```
    
- `const API_INTERVAL = ...` : API 호출 주기(업데이트 주기)
- `const API_URL_... = ...` : API 호출 URL 주소

## 3.5 `CPU_BARS.vue`, `GPU_BARS.vue`, `GPU_TEMP.vue`

### 기능 설명:
- API를 통해 주기적으로 각 자원의 전체 사용률을 받아옵니다.
- 데이터 로딩 중에는 인디케이터(무한 로딩)로 표시합니다.
- 값을 불러오면 원형 프로그레스바에 퍼센트를 표시합니다.
- 사용하는 값에 따라 색상이 변경됩니다(설정 가능): 
    - 90% 이상 : 빨간색 (위험) 
    - 80% 이상 : 주황색 (주의) 

### 주요 데이터 바인딩 
- `const {cpu | gpu | mem} = ...` : API 에서 받아온 실시간 사용률 값 저장용(JSON)
    ```
    // JSON Format
    { value: 0}
    ```
- `const API_INTERVAL = ...` : API 호출 주기(업데이트 주기)
- `const API_URL = ...` : API 호출 URL 주소
- `const DANGER_LEVEL = ...` : 해당 수준을 넘을 경우 인디케이터 색상을 빨간색으로 변경 
- `const WARNING_LEVEL = ...` : 해당 수준을 넘을 경우 인디케이터 색상을 주황색으로 변경 

## 3.6 `CPU_CHART.vue`, `GPU_CHART.vue`

## 3.6 `CPU_RANK.vue`, `GPU_RANK.vue`, `MEM_RANK.vue`

## 3.7 `IDLE_RANK.vue`