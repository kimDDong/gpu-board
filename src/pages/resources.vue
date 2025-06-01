<!-- src/pages/resources.vue -->
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
              <tr v-for="r in gpuResources" :key="r.gpu_id">
                <td>{{ r.gpu_id }}</td>
                <td>{{ r.user }}</td>
                <td>{{ r.start_date }}</td>
                <td>{{ r.end_date }}</td>
                <td>
                  <v-btn size="small" @click="reclaimResource(r.gpu_id)">회수</v-btn>
                  <v-btn size="small" @click="editPeriod(r)">사용기간조정</v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12" md="5">
      <v-card>
        <v-card-title>자원 할당 정책</v-card-title>
        <v-card-text>
          <v-text-field label="최대 사용 기간(일)" v-model="policy.max_days"/>
          <v-text-field label="사용자별 할당 제한" v-model="policy.user_limit"/>
          <v-btn @click="savePolicy">저장</v-btn>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>

  <!-- 기간조정 다이얼로그는 반드시 최상위에서! -->
  <v-dialog v-model="showEditDialog" max-width="400">
    <v-card>
      <v-card-title>사용기간 조정</v-card-title>
      <v-card-text>
        <v-text-field label="만료일 (YYYY-MM-DD)" v-model="editPeriodDate"/>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="showEditDialog=false">취소</v-btn>
        <v-btn color="primary" @click="submitEditPeriod">적용</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      gpuResources: [],
      policy: { max_days: '', user_limit: '' },
      showEditDialog: false,
      editGpuId: null,
      editPeriodDate: '',
    }
  },
  methods: {
    fetchResources() {
      axios.get('http://localhost:5000/api/resources')
        .then(res => { this.gpuResources = res.data })
    },
    fetchPolicy() {
      axios.get('http://localhost:5000/api/policy')
        .then(res => { this.policy = res.data })
    },
    reclaimResource(gpu_id) {
      axios.post(`http://localhost:5000/api/resources/${gpu_id}/reclaim`)
        .then(() => this.fetchResources())
    },
    editPeriod(resource) {
      this.editGpuId = resource.gpu_id
      this.editPeriodDate = resource.end_date
      this.showEditDialog = true
    },
    submitEditPeriod() {
      axios.patch(`http://localhost:5000/api/resources/${this.editGpuId}/period`, { end_date: this.editPeriodDate })
        .then(() => {
          this.showEditDialog = false
          this.fetchResources()
        })
    },
    savePolicy() {
      axios.post('http://localhost:5000/api/policy', this.policy)
        .then(() => alert('정책이 저장되었습니다.'))
    },
  },
  mounted() {
    this.fetchResources()
    this.fetchPolicy()
  }
}
</script>
