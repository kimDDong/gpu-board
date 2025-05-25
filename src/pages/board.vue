<!-- pages/board.vue -->
<template>
  <v-row dense>
    <!-- 시각적 KPI 카드: CPU, GPU, 메모리 활용률 -->
    <v-col cols="12" md="4">
      <v-card>
        <v-card-title>CPU 활용률</v-card-title>
        <v-card-text>
          <!-- 더미 Progress Bar -->
          <v-progress-circular :value="60" color="primary" size="60" width="8"></v-progress-circular>
          <span class="ml-2">60%</span>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12" md="4">
      <v-card>
        <v-card-title>GPU 활용률</v-card-title>
        <v-card-text>
          <v-progress-circular :value="80" color="deep-purple accent-4" size="60" width="8"></v-progress-circular>
          <span class="ml-2">80%</span>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12" md="4">
      <v-card>
        <v-card-title>메모리 활용률</v-card-title>
        <v-card-text>
          <v-progress-circular :value="50" color="green" size="60" width="8"></v-progress-circular>
          <span class="ml-2">50%</span>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>

  <v-row class="mt-4">
    <v-col cols="12" md="6">
      <v-card height="280">
        <v-card-title>자원 유휴 시간</v-card-title>
        <v-card-text>
          <!-- 차트 라이브러리 실제로는 필요, 여기선 박스/더미 표시만 -->
          <div class="d-flex align-center justify-center" style="height:200px;">
            [차트/그래프 자리]
          </div>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12" md="6">
      <v-card height="280">
        <v-card-title>사용자별 자원 사용량</v-card-title>
        <v-card-text>
          <div class="d-flex align-center justify-center" style="height:200px;">
            [차트/그래프 자리]
          </div>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>

  <v-row class="mt-4">
    <v-col cols="12">
      <v-card>
        <v-card-title>실시간 시스템 상태</v-card-title>
        <v-card-text>
          <v-list dense>
            <v-list-item title="GPU 클러스터 상태" subtitle="정상"></v-list-item>
            <v-list-item title="시스템 상태" subtitle="정상"></v-list-item>
            <v-list-item title="알림" subtitle="모든 시스템 정상 작동 중"></v-list-item>
          </v-list>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>

  <v-row class="mt-4">
    <v-col cols="12">
      <v-card>
        <v-card-title>맞춤형 대시보드 보기 설정</v-card-title>
        <v-card-text>
          <!-- 실제 설정 기능은 없음, 간략한 placeholder 버튼/체크박스 -->
          <v-checkbox label="CPU 정보 표시" />
          <v-checkbox label="GPU 정보 표시" />
          <v-checkbox label="유휴 시간 표시" />
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>