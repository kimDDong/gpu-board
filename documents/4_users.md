
# 📘 사용자 관리 및 리소스 보고 시스템 메뉴얼

## 🗂️ 구성 파일 개요

| 파일명 | 설명 |
|--------|------|
| `users.vue` | 사용자 목록을 테이블 형태로 보여주고 생성, 삭제, 상세 보기 기능을 수행 |
| `UserReportDialog.vue` | 선택한 사용자에 대한 상세 리포트를 다이얼로그로 표시 |
| `TrendBar.vue` | 리소스 사용률(CPU, GPU, MEM)의 시간에 따른 변화 시각화 컴포넌트 |
| `users_api.py` | 사용자 데이터 및 역할/권한 관련 API를 제공하는 Flask 서버 |

## 1. `users_api.py`: Flask 백엔드 API 서버

### 🔧 주요 기능

- **사용자 CRUD**
  - `GET /api/users`: 전체 사용자 목록 반환
  - `POST /api/users`: 새 사용자 추가
  - `DELETE /api/users/<user_id>`: 특정 사용자 삭제
  - `PUT /api/users/<user_id>`: 사용자 정보 수정
- **활성/비활성 전환**
  - `POST /api/users/<user_id>/deactivate`: 비활성 처리
  - `POST /api/users/<user_id>/activate`: 활성 처리
- **역할 권한 관리**
  - `POST /api/roles`: 역할별 권한 저장
  - `GET /api/roles/<role>`: 특정 역할 권한 조회

### 💾 데이터 구조

```python
{
  "id": "user1",
  "name": "홍길동",
  "role": "관리자",
  "expiry": "2025-12-31",
  "active": true,
  "cpuUsage": [30, 40, 45, ...],
  "gpuUsage": [12, 55, 60, ...],
  "memUsage": [60, 70, 50, ...],
  "usageTimestamps": ["1", "2", ..., "31"]
}
```

## 2. `users.vue`: 사용자 관리 화면 (Vue)

### 📌 주요 기능

- 사용자 리스트 테이블 렌더링
- 신규 사용자 추가 다이얼로그
- 사용자 삭제 기능
- 리포트 다이얼로그 열기 (`UserReportDialog.vue`)

### 🧩 구조 요약

```html
<template>
  <v-data-table :items="users" :headers="headers" ... />
  <v-dialog v-model="dialog">
    <!-- 사용자 추가 입력 폼 -->
  </v-dialog>
  <UserReportDialog :user="selectedUser" :show="reportDialog" />
</template>
```

### 📘 핵심 메서드

- `fetchUsers()`: `/api/users`로부터 사용자 목록 로드
- `addUser()`: 신규 사용자 POST 요청 후 목록 갱신
- `deleteUser(id)`: 특정 사용자 삭제
- `openReport(user)`: 선택한 사용자 상세 리포트 보기

## 3. `UserReportDialog.vue`: 사용자 리포트 다이얼로그

### 📌 주요 기능

- 사용자 리포트를 보여주는 팝업 다이얼로그
- `TrendBar`를 이용한 자원 사용률 시각화
- 평균 사용률 계산 및 날짜 필터링 기능

### 🧩 구조 요약

```html
<template>
  <v-dialog :value="show">
    <v-card>
      <v-card-title>{{ user.name }} 리포트</v-card-title>
      <v-date-picker v-model="selectedDate" />
      <TrendBar v-if="user" :user="user" :filterDate="selectedDate" />
    </v-card>
  </v-dialog>
</template>
```

### 📘 핵심 기능

- `selectedDate`: 사용자 리소스 사용 필터 기준일
- `TrendBar`: 필터링된 사용률 데이터 전달
- `computed averages`: CPU, GPU, MEM 평균값 계산

## 4. `TrendBar.vue`: 리소스 사용률 시각화 컴포넌트

### 📊 주요 기능

- Chart.js 기반 사용자별 CPU, GPU, MEM 사용률 라인 차트 표시
- 날짜 필터 기반으로 선택된 범위만 보여주기
- 세 가지 자원 모두에 대한 평균, 추세 확인 가능

### 📘 Props

```js
props: {
  user: Object,
  filterDate: String
}
```

### 🎨 차트 구성 예시

```js
new Chart(ctx, {
  type: 'line',
  data: {
    labels: usageTimestamps,
    datasets: [
      {
        label: "CPU Usage",
        data: cpuUsage,
        borderColor: "#f44336"
      },
      ...
    ]
  }
});
```

## 🔁 전체 흐름 요약

1. `users.vue`에서 사용자 목록을 로드하고 관리.
2. 사용자 상세를 보고 싶을 때 `UserReportDialog.vue`가 열림.
3. 이 다이얼로그에서 선택된 날짜 기준으로 `TrendBar.vue`에서 사용률 시각화.
4. Flask `users_api.py`는 사용자 생성 및 리소스 기록 데이터를 제공.

## 🛠️ 향후 확장 포인트

| 항목 | 설명 |
|------|------|
| 사용자 검색 기능 | 이름, ID 기준 테이블 필터링 |
| 평균 사용량 경고 | 경고 알림 시각화 |
| 리포트 다운로드 | PDF/이미지로 저장 |
| 실시간 데이터 연동 | WebSocket 기반 실시간 차트 |
| 인증 시스템 추가 | 로그인/토큰 기반 접근 제어 |

## 📎 예시 API 호출

### 사용자 추가 요청

```bash
curl -X POST http://localhost:8000/api/users   -H "Content-Type: application/json"   -d '{
    "id": "user16",
    "name": "강하늘",
    "role": "일반 사용자",
    "expiry": "2025-12-31"
  }'
```

### 역할 권한 등록

```bash
curl -X POST http://localhost:8000/api/roles   -H "Content-Type: application/json"   -d '{
    "role": "관리자",
    "permissions": ["사용자 보기", "사용자 삭제"]
  }'
```

## 📂 디렉토리 구성 예시

```plaintext
gpu-board/
├── backend/
│   └── users_api.py
├── frontend/
│   ├── components/
│   │   ├── TrendBar.vue
│   │   └── UserReportDialog.vue
│   └── views/
│       └── users.vue
```

## ✅ 테스트 체크리스트

| 테스트 항목 | 설명 | 완료 여부 |
|-------------|------|------------|
| 사용자 목록 조회 | `/api/users` | ✅ |
| 사용자 추가 | POST `/api/users` | ✅ |
| 사용자 삭제 | DELETE `/api/users/<id>` | ✅ |
| 사용자 수정 | PUT `/api/users/<id>` | ✅ |
| 자원 시각화 | TrendBar 표시 여부 | ✅ |
| 날짜 필터링 | TrendBar에 필터 반영 여부 | ✅ |

## 📌 결론

이 시스템은 사용자 계정을 생성하고 관리하며, 각 사용자의 일별 리소스(CPU, GPU, MEM) 사용량을 시각적으로 분석하기 위한 통합 프론트엔드/백엔드 아키텍처입니다. 이 문서는 구성요소의 연결 흐름, API 설계, 시각화 구조를 상세히 설명하여 유지보수성과 협업 효율성을 높입니다.
