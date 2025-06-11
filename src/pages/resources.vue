<template>
  <v-container>
    <v-row>
      <v-col>
        <v-btn @click="assignDialog = true" color="primary" class="mb-3">
          <v-icon left>mdi-plus</v-icon> 자원 할당
        </v-btn>
        <v-btn @click="showReport = true" color="info" class="mb-3 ml-3">
          <v-icon left>mdi-chart-bar</v-icon> 자원 현황/보고서 보기
        </v-btn>
        <v-select
          v-model="resourceTypeFilter"
          :items="['ALL', 'GPU', 'CPU', 'Memory']"
          label="자원 종류 필터"
          dense
          class="mb-3"
          style="max-width: 160px;"
        />
      </v-col>
    </v-row>
    <!-- 사용자별 자원 테이블 -->
    <v-row>
      <v-col cols="12" md="6" v-for="user in users" :key="user">
        <v-card class="mb-4">
          <v-card-title>
            <span>{{ user }} - 할당 자원</span>
          </v-card-title>
          <v-card-text>
            <div v-if="userResources(user).length">
              <v-table>
                <thead>
                  <tr>
                    <th>종류</th>
                    <th>번호</th>
                    <th>기간</th>
                    <th>조치</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="r in userResources(user)" :key="r.type + '_' + r.res_id">
                    <td>{{ r.type }}</td>
                    <td>{{ r.res_id }}</td>
                    <td>{{ r.start_date }} ~ {{ r.end_date }}</td>
                    <td>
                      <v-btn size="small" color="error" @click="reclaimResource(r)">회수</v-btn>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </div>
            <div v-else class="text-grey text-caption mt-2">
              할당된 자원이 없습니다.
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <!-- 자원 할당 다이얼로그 -->
    <v-dialog v-model="assignDialog" max-width="520">
      <v-card>
        <v-card-title>자원 할당</v-card-title>
        <v-card-text>
          <v-select
            label="사용자"
            :items="users"
            v-model="assignUser"
            :rules="[v => !!v || '필수 입력']"
            dense
            clearable
          />
          <v-select
            label="자원 종류"
            :items="['GPU','CPU','Memory']"
            v-model="assignResourceType"
            dense
          />
          <v-select
            label="자원 선택(복수)"
            v-model="selectedResourceKeys"
            :items="filteredAvailableResources"
            item-title="label"
            item-value="key"
            multiple
            :rules="[v => v && v.length > 0 || '최소 1개 선택']"
            dense
          />
          <v-menu v-model="menu1" :close-on-content-click="false" transition="scale-transition" offset-y>
            <template #activator="{ props }">
              <v-text-field label="시작일" v-model="startStr" readonly v-bind="props" dense />
            </template>
            <v-date-picker v-model="startObj" @update:model-value="onPickStart" color="primary" />
          </v-menu>
          <v-menu v-model="menu2" :close-on-content-click="false" transition="scale-transition" offset-y>
            <template #activator="{ props }">
              <v-text-field label="만료일" v-model="endStr" readonly v-bind="props" dense />
            </template>
            <v-date-picker v-model="endObj" @update:model-value="onPickEnd" color="primary" />
          </v-menu>
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="closeAssignDialog">취소</v-btn>
          <v-btn color="primary" @click="confirmAssign">할당</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- 보고서 모달 -->
    <ReportDialog v-model="showReport" />
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import ReportDialog from '@/components/ReportDialog.vue'

const users = ref([])
const resources = ref([])
const resourceTypeFilter = ref('ALL')

function userResources(user) {
  return Array.isArray(resources.value)
    ? resources.value.filter(r => r.user === user && (resourceTypeFilter.value === 'ALL' || r.type === resourceTypeFilter.value))
    : []
}

// 다이얼로그 상태
const assignDialog = ref(false)
const assignUser = ref('')
const assignResourceType = ref('GPU')
const selectedResourceKeys = ref([])
const startObj = ref(null)
const endObj = ref(null)
const startStr = ref('')
const endStr = ref('')
const menu1 = ref(false)
const menu2 = ref(false)

const availableResources = computed(() =>
  Array.isArray(resources.value)
    ? resources.value.filter(r => !r.user).map(r => ({
        key: `${r.type}-${r.res_id}`,
        label: `${r.type} ${r.res_id}`,
        res_id: r.res_id,
        type: r.type
      }))
    : []
)
const filteredAvailableResources = computed(() =>
  availableResources.value.filter(r => r.type === assignResourceType.value)
)

function onPickStart(v) {
  startObj.value = v
  startStr.value = v ? `${v.getFullYear()}-${String(v.getMonth()+1).padStart(2, "0")}-${String(v.getDate()).padStart(2, "0")}` : ''
  menu1.value = false
}
function onPickEnd(v) {
  endObj.value = v
  endStr.value = v ? `${v.getFullYear()}-${String(v.getMonth()+1).padStart(2, "0")}-${String(v.getDate()).padStart(2, "0")}` : ''
  menu2.value = false
}
function closeAssignDialog() {
  assignDialog.value = false
  assignUser.value = ''
  assignResourceType.value = 'GPU'
  selectedResourceKeys.value = []
  startObj.value = null
  endObj.value = null
  startStr.value = ''
  endStr.value = ''
}
async function confirmAssign() {
  if (!assignUser.value || !selectedResourceKeys.value.length || !startStr.value || !endStr.value) {
    alert('모든 값을 입력하세요'); return
  }
  for (const key of selectedResourceKeys.value) {
    const res = availableResources.value.find(r => r.key === key)
    if (!res) continue
    await axios.post('/api/allocations', {
      res_id: res.res_id,
      type: res.type,
      user: assignUser.value,
      start_date: startStr.value,
      end_date: endStr.value
    })
  }
  await fetchData()
  closeAssignDialog()
}
async function fetchData() {
  try {
    const res = await axios.get('/api/resources')
    resources.value = Array.isArray(res.data) ? res.data : []
    const usr = await axios.get('/api/users')
    users.value = Array.isArray(usr.data) ? usr.data : []
  } catch (e) {
    resources.value = []
    users.value = []
  }
}
async function reclaimResource(r) {
  await axios.post('/api/allocations/reclaim', {
    res_id: r.res_id,
    type: r.type
  })
  await fetchData()
}
const showReport = ref(false)
fetchData()
</script>
