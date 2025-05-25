<!-- pages/resources.vue -->
<template>
  <v-row>
    <v-col cols="12" md="7">
      <v-card>
        <v-card-title>할당된 GPU 자원</v-card-title>
        <v-card-text>
          <v-table>
            <thead>
              <tr>
                <th>GPU 번호</th>
                <th>사용자</th>
                <th>사용 시작일</th>
                <th>만료일</th>
                <th>조치</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>0</td>
                <td>홍길동</td>
                <td>2024-05-20</td>
                <td>2024-06-20</td>
                <td>
                  <v-btn size="small">회수</v-btn>
                  <v-btn size="small">사용기간조정</v-btn>
                </td>
              </tr>
              <tr>
                <td>1</td>
                <td>김철수</td>
                <td>2024-05-22</td>
                <td>2024-06-22</td>
                <td>
                  <v-btn size="small">회수</v-btn>
                  <v-btn size="small">사용기간조정</v-btn>
                </td>
              </tr>
              <!-- 더미 데이터 -->
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12" md="5">
      <v-card>
        <v-card-title>자원 할당 정책</v-card-title>
        <v-card-text>
          <v-text-field label="최대 사용 기간(일)" />
          <v-text-field label="사용자별 할당 제한" />
          <v-btn>저장</v-btn>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>