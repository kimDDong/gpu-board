<template>
  <v-row class="mt-6">
    <v-col cols="12" md="6">
      <v-card class="pa-3" style="border:1.5px solid #e0e0e0;">
        <div class="text-h6 mb-2">TOP5 누적 사용량 랭크</div>
        <v-table>
          <thead>
            <tr>
              <th>순위</th>
              <th>이름</th>
              <th>GPU</th>
              <th>CPU</th>
              <th>Memory</th>
              <th>총합</th>
              <th>리포트</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(u, i) in userRank.usage" :key="u.name">
              <td>{{ i+1 }}</td>
              <td>{{ u.name }}</td>
              <td>{{ u.gpu }}</td>
              <td>{{ u.cpu }}</td>
              <td>{{ u.memory }}</td>
              <td>{{ u.gpu + u.cpu + u.memory }}</td>
              <td>
                <a :href="'/report/user/' + u.name" target="_blank">보고서</a>
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card>
    </v-col>
    <v-col cols="12" md="6">
      <v-card class="pa-3" style="border:1.5px solid #e0e0e0;">
        <div class="text-h6 mb-2">TOP5 누적 유휴시간 랭크</div>
        <v-table>
          <thead>
            <tr>
              <th>순위</th>
              <th>이름</th>
              <th>유휴시간(일)</th>
              <th>리포트</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(u, i) in userRank.idle" :key="u.name">
              <td>{{ i+1 }}</td>
              <td>{{ u.name }}</td>
              <td>{{ u.idle }}</td>
              <td>
                <a :href="'/report/user/' + u.name" target="_blank">보고서</a>
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card>
    </v-col>
  </v-row>
</template>
<script setup>
defineProps({
  userRank: Object
})
</script>
