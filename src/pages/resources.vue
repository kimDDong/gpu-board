<template>
  <v-container>
    <!-- 버튼들 -->
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
          :items="['ALL','GPU','CPU']"
          label="자원 종류 필터"
          dense
          class="mb-3"
          style="max-width:160px"
        />
      </v-col>
    </v-row>

    <!-- 사용자별 할당 내역 -->
    <v-row>
      <v-col
        v-for="user in filteredUsers"
        :key="user"
        cols="12" md="6"
      >
        <v-card class="mb-4">
          <v-card-title>{{ user }} - 할당 자원</v-card-title>
          <v-card-text>
            <div v-if="userResources(user).length > 0">
              <table style="width: 100%; border-collapse: collapse;">
                <thead>
                  <tr>
                    <th style="border-bottom: 1px solid #ccc; padding: 8px;">종류</th>
                    <th style="border-bottom: 1px solid #ccc; padding: 8px;">번호</th>
                    <th style="border-bottom: 1px solid #ccc; padding: 8px;">기간</th>
                    <th style="border-bottom: 1px solid #ccc; padding: 8px;">조치</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="res in userResources(user)"
                    :key="`${res.type}-${res.res_id}`"
                  >
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{{ res.type }}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{{ res.res_id }}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{{ res.start_date }} ~ {{ res.end_date }}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">
                      <v-btn
                        color="error"
                        text
                        small
                        @click="reclaim(res)"
                      >
                        회수
                      </v-btn>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-caption text--disabled">
              할당된 자원이 없습니다.
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 이하 할당 다이얼로그 등 생략... 동일 -->
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import ReportDialog from '@/components/ReportDialog.vue'

const users = ref([])
const resources = ref([])
const resourceTypeFilter = ref('ALL')

const assignDialog = ref(false)
const assignUser = ref('')
const assignType = ref('GPU')
const selected = ref([])
const startObj = ref(null)
const endObj = ref(null)
const start = ref('')
const end = ref('')
const menuStart = ref(false)
const menuEnd = ref(false)
const showReport = ref(false)

async function fetchData() {
  try {
    const u = await axios.get('/api/users')
    users.value = Array.isArray(u.data) ? u.data : []
    const r = await axios.get('/api/resources')
    resources.value = Array.isArray(r.data) ? r.data : []
    console.log('resources loaded:', resources.value) // debug
  } catch (e) {
    console.error('fetchData error:', e)
    users.value = []
    resources.value = []
  }
}
fetchData()

const filteredUsers = computed(() => {
  if (resourceTypeFilter.value === 'ALL') return users.value
  const filteredSet = new Set(
    resources.value.filter(r => r.user && r.type === resourceTypeFilter.value).map(r => r.user)
  )
  return users.value.filter(u => filteredSet.has(u))
})

function userResources(user) {
  // 안전하게 배열 체크 후 필터링
  if (!Array.isArray(resources.value)) return []
  return resources.value.filter(r =>
    r.user === user &&
    (resourceTypeFilter.value === 'ALL' || r.type === resourceTypeFilter.value)
  )
}

const freeResources = computed(() => {
  if (!Array.isArray(resources.value)) return []
  return resources.value
    .filter(r => !r.user && r.type === assignType.value)
    .map(r => ({
      key: `${r.type}-${r.res_id}`,
      label: `${r.type} ${r.res_id}`,
      ...r
    }))
})


// 날짜 선택 이벤트 핸들러
function onPickStart(val) {
  startObj.value = val
  start.value = val ? val.toISOString().substring(0, 10) : ''
  menuStart.value = false
}
function onPickEnd(val) {
  endObj.value = val
  end.value = val ? val.toISOString().substring(0, 10) : ''
  menuEnd.value = false
}

// 다이얼로그 닫기 초기화
function closeAssignDialog() {
  assignDialog.value = false
  assignUser.value = ''
  assignType.value = 'GPU'
  selected.value = []
  start.value = ''
  end.value = ''
  startObj.value = null
  endObj.value = null
}

// 자원 할당 API 호출
async function confirmAssign() {
  if (!assignUser.value || !selected.value.length || !start.value || !end.value) {
    alert('모든 값을 입력해주세요.')
    return
  }
  for (const key of selected.value) {
    const res = freeResources.value.find(r => r.key === key)
    if (!res) continue
    await axios.post('/api/allocations', {
      res_id: res.res_id,
      type: res.type,
      user: assignUser.value,
      start_date: start.value,
      end_date: end.value
    })
  }
  await fetchData()
  closeAssignDialog()
}

// 자원 회수 API 호출
async function reclaim(res) {
  await axios.post('/api/allocations/reclaim', {
    res_id: res.res_id,
    type: res.type
  })
  await fetchData()
}
</script>
