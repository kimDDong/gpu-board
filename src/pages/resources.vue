<!-- src/pages/resources.vue -->
<template>
  <v-row>
    <!-- 할당된 GPU 자원 목록 -->
    <v-col cols="12">
      <v-card>
        <v-card-title>
          할당된 GPU 자원
          <v-spacer/>
          <v-btn color="primary" @click="openAssignDialog">자원 할당</v-btn>
        </v-card-title>
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
                  <v-btn size="small" color="error" @click="reclaimResource(r.gpu_id)">회수</v-btn>
                  <v-btn size="small" color="info" @click="editPeriod(r)">기간조정</v-btn>
                </td>
              </tr>
              <tr v-if="gpuResources.length === 0">
                <td colspan="5" class="text-center">등록된 GPU 자원이 없습니다.</td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </v-col>

    <!-- 자원 할당 정책 -->
    <v-col cols="12" md="6" class="mt-5">
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
    </v-col>

    <!-- 자원 할당 다이얼로그 -->
    <v-dialog v-model="showAssignDialog" max-width="400">
      <v-card>
        <v-card-title>자원 할당</v-card-title>
        <v-card-text>
          <v-select
            label="사용자"
            :items="users"
            v-model="assignUser"
            :rules="[v => !!v || '필수 입력']"
            clearable
            dense
          />
          <!-- 시작일 -->
          <v-menu
            v-model="assignStartMenu"
            :close-on-content-click="false"
            transition="scale-transition"
            offset-y
          >
            <template #activator="{ props }">
              <v-text-field
                label="시작일"
                v-model="assignStartStr"
                readonly
                v-bind="props"
                dense
              />
            </template>
            <v-date-picker
              v-model="assignStartObj"
              color="primary"
              :max="assignEndObj"
              show-adjacent-months
              @update:model-value="onPickAssignStart"
            />
          </v-menu>
          <!-- 만료일 -->
          <v-menu
            v-model="assignEndMenu"
            :close-on-content-click="false"
            transition="scale-transition"
            offset-y
          >
            <template #activator="{ props }">
              <v-text-field
                label="만료일"
                v-model="assignEndStr"
                readonly
                v-bind="props"
                dense
              />
            </template>
            <v-date-picker
              v-model="assignEndObj"
              color="primary"
              :min="assignStartObj"
              show-adjacent-months
              @update:model-value="onPickAssignEnd"
            />
          </v-menu>
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
          <v-menu
            v-model="editPeriodMenu"
            :close-on-content-click="false"
            transition="scale-transition"
            offset-y
          >
            <template #activator="{ props }">
              <v-text-field
                label="만료일 (YYYY-MM-DD)"
                v-model="editPeriodStr"
                readonly
                v-bind="props"
                dense
              />
            </template>
            <v-date-picker
              v-model="editPeriodObj"
              color="primary"
              :min="todayDate"
              show-adjacent-months
              @update:model-value="onPickEditPeriod"
            />
          </v-menu>
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="showEditDialog = false">취소</v-btn>
          <v-btn color="primary" @click="submitEditPeriod">적용</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import axios from 'axios'

function formatDate(dateObj) {
  if (!dateObj) return '';
  const yyyy = dateObj.getFullYear();
  const mm = String(dateObj.getMonth() + 1).padStart(2, '0');
  const dd = String(dateObj.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}
function parseDate(str) {
  if (!str) return null;
  const [y, m, d] = str.split('-');
  return new Date(Number(y), Number(m) - 1, Number(d));
}

export default {
  data() {
    return {
      gpuResources: [],
      policy: { max_days: '', user_limit: '' },
      users: [],
      // 할당
      showAssignDialog: false,
      assignUser: '',
      assignStartObj: null,
      assignEndObj: null,
      assignStartStr: '',
      assignEndStr: '',
      assignStartMenu: false,
      assignEndMenu: false,
      // 기간 수정
      showEditDialog: false,
      editGpuId: null,
      editPeriodObj: null,
      editPeriodStr: '',
      editPeriodMenu: false,
      // 오늘 날짜
      todayDate: new Date(),
    }
  },
  methods: {
    formatDate,
    fetchResources() {
      axios.get('http://127.0.0.1:5000/api/resources')
        .then(res => { this.gpuResources = res.data })
    },
    fetchPolicy() {
      axios.get('http://127.0.0.1:5000/api/policy')
        .then(res => { this.policy = res.data })
    },
    fetchUsers() {
      axios.get('http://127.0.0.1:5000/api/users')
        .then(res => { this.users = res.data })
    },
    openAssignDialog() {
      this.assignUser = ''
      this.assignStartObj = null
      this.assignEndObj = null
      this.assignStartStr = ''
      this.assignEndStr = ''
      this.showAssignDialog = true
    },
    onPickAssignStart(val) {
      this.assignStartObj = val
      this.assignStartStr = this.formatDate(val)
      this.assignStartMenu = false
    },
    onPickAssignEnd(val) {
      this.assignEndObj = val
      this.assignEndStr = this.formatDate(val)
      this.assignEndMenu = false
    },
    assignResource() {
      if (!this.assignUser || !this.assignStartObj || !this.assignEndObj) {
        alert('모든 값을 입력하세요')
        return
      }
      axios.post('http://127.0.0.1:5000/api/resources', {
        user: this.assignUser,
        start_date: this.assignStartStr,
        end_date: this.assignEndStr
      }).then(() => {
        this.showAssignDialog = false
        this.fetchResources()
      })
    },
    reclaimResource(gpu_id) {
      axios.post(`http://127.0.0.1:5000/api/resources/${gpu_id}/reclaim`)
        .then(() => this.fetchResources())
    },
    editPeriod(resource) {
      this.editGpuId = resource.gpu_id
      this.editPeriodObj = parseDate(resource.end_date)
      this.editPeriodStr = resource.end_date
      this.showEditDialog = true
    },
    onPickEditPeriod(val) {
      this.editPeriodObj = val
      this.editPeriodStr = this.formatDate(val)
      this.editPeriodMenu = false
    },
    submitEditPeriod() {
      if (!this.editPeriodObj) {
        alert('만료일을 선택하세요')
        return
      }
      axios.patch(`http://127.0.0.1:5000/api/resources/${this.editGpuId}/period`, { end_date: this.editPeriodStr })
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
