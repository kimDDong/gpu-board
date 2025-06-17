<template>
  <v-container>
    <!-- 날짜 선택 영역 -->
    <v-row>
      <v-col cols="12" md="6">
        <v-menu v-model="startDateMenu" :close-on-content-click="false" transition="scale-transition" offset-y min-width="auto">
          <template #activator="{ props }">
            <v-text-field
              v-model="selectedStartDate"
              label="시작 날짜"
              prepend-icon="mdi-calendar"
              readonly
              v-bind="props"
              dense
              hide-details
            />
          </template>
          <v-date-picker v-model="selectedStartDate" type="string" @update:modelValue="val => { startDateMenu = false; selectedStartDate = formatDateToString(val); }" />
        </v-menu>
      </v-col>
      <v-col cols="12" md="6">
        <v-menu v-model="endDateMenu" :close-on-content-click="false" transition="scale-transition" offset-y min-width="auto">
          <template #activator="{ props }">
            <v-text-field
              v-model="selectedEndDate"
              label="종료 날짜"
              prepend-icon="mdi-calendar"
              readonly
              v-bind="props"
              dense
              hide-details
            />
          </template>
          <v-date-picker v-model="selectedEndDate" type="string" @update:modelValue="val => { endDateMenu = false; selectedEndDate = formatDateToString(val); }" />
        </v-menu>
      </v-col>
    </v-row>

    <!-- 사용자 검색 -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card class="pa-4" style="border:1.5px solid #e0e0e0;">
          <div class="text-h5 mb-2">사용자 검색</div>
          <v-text-field v-model="searchKeyword" placeholder="이름 또는 ID 검색" dense hide-details
            prepend-inner-icon="mdi-magnify" style="max-width: 320px;" />
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <v-btn @click="assignDialog = true" color="primary" class="mb-3">
          <v-icon left>mdi-plus</v-icon> 자원 할당
        </v-btn>
        <router-link to="/reports">
          <v-btn color="info" class="mb-3 ml-3">
            <v-icon left>mdi-chart-bar</v-icon> 자원 현황/보고서 보기
          </v-btn>
        </router-link>
        <v-select v-model="resourceTypeFilter" :items="['ALL', 'GPU', 'CPU', 'Memory']" label="자원 종류 필터" dense
          class="mb-3" style="max-width: 160px;" />
      </v-col>
    </v-row>

    <!-- 사용자별 자원 테이블 -->
    <v-row>
      <v-col cols="12" md="6"
        v-for="userObj in filteredUsers"
        :key="getUserName(userObj)">
        <v-card class="mb-4">
          <v-card-title>
            <span>{{ getUserName(userObj) }} - 할당 자원</span>
          </v-card-title>
          <v-card-text>
            <div v-if="userResources(getUserName(userObj)).length">
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
                  <tr v-for="r in userResources(getUserName(userObj))" :key="r.type + '_' + r.res_id">
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

    <!-- 자원 할당 다이얼로그 (여러 개 동시) -->
    <v-dialog v-model="assignDialog" max-width="520">
      <v-card>
        <v-card-title>자원 할당</v-card-title>
        <v-card-text>
          <v-select label="사용자" :items="userNamesList" v-model="assignUser" :rules="[v => !!v || '필수 입력']" dense clearable />
          <v-select label="자원 종류" :items="['GPU', 'CPU', 'Memory']" v-model="assignResourceType" dense />
          <v-select label="자원 선택(복수)" v-model="selectedResourceKeys" :items="filteredAvailableResources"
            item-title="label" item-value="key" multiple :rules="[v => v && v.length > 0 || '최소 1개 선택']" dense />
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
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

// 날짜 선택 State
const today = new Date()
const thisYear = today.getFullYear()
const selectedStartDate = ref(`${thisYear}-01-01`)
const selectedEndDate = ref(`${thisYear}-12-31`)
const startDateMenu = ref(false)
const endDateMenu = ref(false)

function formatDateToString(date) {
  if (!date) return ''
  if (typeof date === 'string') return date
  if (date instanceof Date) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  return ''
}

// 사용자 데이터 상태 (string or object 모두 대응)
const users = ref([])
const resources = ref([])

// user 객체이든 string이든 이름만 반환
function getUserName(user) {
  if (!user) return ''
  if (typeof user === 'string') return user
  if (typeof user === 'object' && user.name) return user.name
  // 혹시 name 필드가 없으면 string 변환
  return String(user)
}

// 🔍 사용자 검색 (이름 또는 ID)
const searchKeyword = ref('')
const filteredUsers = computed(() => {
  if (!searchKeyword.value) return users.value
  return users.value.filter(u => {
    const name = getUserName(u)
    return name.toLowerCase().includes(searchKeyword.value.toLowerCase())
  })
})
// 모든 유저 이름만 추출 (자원 할당 다이얼로그 등에서 사용)
const userNamesList = computed(() => users.value.map(getUserName))

// 자원종류(GPU/CPU/Memory/ALL) 필터
const resourceTypeFilter = ref('ALL')

// 날짜 범위 내 자원만 필터링
function isInSelectedPeriod(res) {
  if (!res.start_date || !res.end_date) return false
  const start = selectedStartDate.value.replace(/-/g, '')
  const end = selectedEndDate.value.replace(/-/g, '')
  const res_start = res.start_date.replace(/-/g, '')
  const res_end = res.end_date.replace(/-/g, '')
  // 겹치면 true
  return !(res_end < start || res_start > end)
}

// 사용자별 자원 필터 (userName만 비교)
function userResources(userName) {
  let list = resources.value.filter(r => r.user === userName)
  if (resourceTypeFilter.value !== 'ALL') {
    list = list.filter(r => r.type === resourceTypeFilter.value)
  }
  // 날짜 범위 내 할당만 필터링
  list = list.filter(isInSelectedPeriod)
  return list
}

// --- 다중 자원 할당 팝업 ---
const assignDialog = ref(false)
const assignUser = ref('')
const assignResourceType = ref('GPU') // 기본값 GPU
const selectedResourceKeys = ref([])
const startObj = ref(null)
const endObj = ref(null)
const startStr = ref('')
const endStr = ref('')
const menu1 = ref(false)
const menu2 = ref(false)

// 할당 안된 자원만 리스트
const availableResources = computed(() =>
  resources.value
    .filter(r => !r.user)
    .map(r => ({
      key: r.type + '-' + r.res_id,
      label: `${r.type} ${r.res_id}`,
      res_id: r.res_id,
      type: r.type
    }))
)
const filteredAvailableResources = computed(() =>
  availableResources.value.filter(r => r.type === assignResourceType.value)
)

// 날짜 선택 (자원 할당 팝업)
function onPickStart(v) {
  startObj.value = v
  startStr.value = v ? formatDateToString(v) : ''
  menu1.value = false
}
function onPickEnd(v) {
  endObj.value = v
  endStr.value = v ? formatDateToString(v) : ''
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
    await axios.post('https://gpu-board.onrender.com:8000/api/allocations', {
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

// 자원목록+유저 불러오기
async function fetchData() {
  resources.value = (await axios.get('https://gpu-board.onrender.com:8000/api/resources')).data
  users.value = (await axios.get('https://gpu-board.onrender.com:8000/api/users')).data
}
fetchData()

// 회수
async function reclaimResource(r) {
  await axios.post('https://gpu-board.onrender.com:8000/api/allocations/reclaim', {
    res_id: r.res_id,
    type: r.type
  })
  await fetchData()
}
</script>
