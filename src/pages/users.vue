<!-- pages/users.vue -->
<template>
  <v-container>
  <v-row>
    <v-col cols="12">
      <v-card>
        <v-card-title>사용자 계정 관리</v-card-title>
        <v-card-text>
          <v-btn color="primary">사용자 추가</v-btn>
          <v-table>
            <thead>
              <tr>
                <th>아이디</th>
                <th>이름</th>
                <th>역할</th>
                <th>조치</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>user1</td>
                <td>홍길동</td>
                <td>관리자</td>
                <td>
                  <v-btn size="small">수정</v-btn>
                  <v-btn size="small">삭제</v-btn>
                </td>
              </tr>
              <tr>
                <td>user2</td>
                <td>김철수</td>
                <td>일반</td>
                <td>
                  <v-btn size="small">수정</v-btn>
                  <v-btn size="small">삭제</v-btn>
                </td>
              </tr>
              <!-- 더미 -->
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12" md="6" class="mt-5">
      <v-card>
        <v-card-title>역할 및 권한 관리</v-card-title>
        <v-card-text>
          <v-select label="역할 선택" :items="['관리자', '일반 사용자']" />
          <v-checkbox label="자원 할당" />
          <v-checkbox label="자원 회수" />
          <v-checkbox label="사용자 계정 관리" />
          <v-btn>저장</v-btn>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
  </v-container>
</template>