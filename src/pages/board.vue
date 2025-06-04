<template>
  <v-container>
    <v-row dense>
      <!-- GPU 자원 리스트 -->
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>
            <span>할당된 GPU 자원</span>
            <v-spacer/>
            <v-btn color="primary" @click="openAssignDialog">자원 할당</v-btn>
          </v-card-title>
          <v-card-text>
            <v-table>
              <thead>
                <tr>
                  <th>GPU 번호</th>
                  <th>사용자</th>
                  <th>시작일</th>
                  <th>만료일</th>
                  <th>조치</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in filteredResources" :key="r.gpu_id">
                  <td>{{ r.gpu_id }}</td>
                  <td>{{ r.user }}</td>
                  <td>{{ r.start_date }}</td>
                  <td>{{ r.end_date }}</td>
                  <td>
                    <v-btn size="small" @click="reclaimResource(r.gpu_id)">회수</v-btn>
                    <v-btn size="small" @click="editPeriod(r)">사용기간조정</v-btn>
                  </td>
                </tr>
                <tr v-if="filteredResources.length === 0">
                  <td colspan="5">등록된 GPU 자원이 없습니다.</td>
                </tr>
              </tbody>
            </v-table>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 정책 설정/필터 박스 -->
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>자원 할당 정책</v-card-title>
          <v-card-text>
            <v-text-field
              label="최대 사용 기간(일)"
              v-model="policy.max_days"
              type="number"
            />
            <v-text-field
              label="사용자별 할당 제한"
              v-model="policy.user_limit"
              type="number"
            />
            <v-btn color="primary" @click="savePolicy">저장</v-btn>
          </v-card-text>
        </v-card>
        <v-card class="mt-4">
          <v-card-title>사용자별 보기</v-card-title>
          <v-card-text>
            <v-select :items="users" label="사용자" v-model="userFilter" clearable />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 자원 할당 다이얼로그 -->
    <v-dialog v-model="showAssignDialog" max-width="400">
      <v-card>
        <v-card-title>자원 할당</v-card-title>
        <v-card-text>
          <v-select label="사용자" :items="users" v-model="assignUser"/>
          <v-text-field label="시작일 (YYYY-MM-DD)" v-model="assignStart"/>
          <v-text-field label="만료일 (YYYY-MM-DD)" v-model="assignEnd"/>
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="showAssignDialog = false">취소</v-btn>
          <v-btn color="primary" @click="assignResource">할당</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 사용기간 조정 다이얼로그 -->
    <v-dialog v-model="showEditDialog" max-width="400">
      <v-card>
        <v-card-title>사용기간 조정</v-card-title>
        <v-card-text>
          <v-text-field
            label="만료일 (YYYY-MM-DD)"
            v-model="editPeriodDate"
            placeholder="예: 2025-07-01"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="showEditDialog = false">취소</v-btn>
          <v-btn color="primary" @click="submitEditPeriod">적용</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      gpuResources: [],
      policy: { max_days: '', user_limit: '' },
      users: [], // 사용자 리스트
      userFilter: '',
      showAssignDialog: false,
      assignUser: '',
      assignStart: '',
      assignEnd: '',
      showEditDialog: false,
      editGpuId: null,
      editPeriodDate: '',
    }
  },
  computed: {
    filteredResources() {
      if (this.userFilter) {
        return this.gpuResources.filter(r => r.user === this.userFilter)
      }
      return this.gpuResources
    }
  },
  methods: {
    fetchResources() {
      axios.get('http://127.0.0.1:5000/api/resources')
        .then(res => { this.gpuResources = res.data })
    },
    fetchPolicy() {
      axios.get('http://127.0.0.1:5000/api/policy')
        .then(res => { this.policy = res.data })
    },
    fetchUsers() {
      // users: 문자열 배열 (ex: ['홍길동', '김철수', '이영희', ...])
      axios.get('http://127.0.0.1:5000/api/users')
        .then(res => { this.users = res.data })
    },
    openAssignDialog() {
      this.showAssignDialog = true
    },
    assignResource() {
      if (!this.assignUser || !this.assignStart || !this.assignEnd) return
      axios.post('http://127.0.0.1:5000/api/resources', {
        user: this.assignUser,
        start_date: this.assignStart,
        end_date: this.assignEnd
      }).then(() => {
        this.showAssignDialog = false
        this.assignUser = ''
        this.assignStart = ''
        this.assignEnd = ''
        this.fetchResources()
      })
    },
    reclaimResource(gpu_id) {
      axios.post(`http://127.0.0.1:5000/api/resources/${gpu_id}/reclaim`)
        .then(() => this.fetchResources())
    },
    editPeriod(resource) {
      this.editGpuId = resource.gpu_id
      this.editPeriodDate = resource.end_date
      this.showEditDialog = true
    },
    submitEditPeriod() {
      axios.patch(`http://127.0.0.1:5000/api/resources/${this.editGpuId}/period`, { end_date: this.editPeriodDate })
        .then(() => {
          this.showEditDialog = false
          this.fetchResources()
        })
    },
    savePolicy() {
      axios.post('http://127.0.0.1:5000/api/policy', this.policy)
        .then(() => alert('정책이 저장되었습니다.'))
    },
  },
  mounted() {
    this.fetchUsers()
    this.fetchResources()
    this.fetchPolicy()
  }
}
</script>
