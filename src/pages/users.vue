<template>
  <v-container fluid>
    <v-row justify="center">
      <v-col cols="12" md="10" class="pa-6">
        <div class="text-h6 font-weight-bold mb-2">사용자 관리</div>
        <div class="text-body-2 mb-6">워크스페이스 내 사용자 목록을 조회하고 관리합니다</div>

        <!-- 검색/필터 -->
        <v-row class="align-center mb-4" no-gutters>
          <v-col cols="12" md="6" class="pr-2">
            <v-text-field v-model="searchKeyword" placeholder="이름, 이메일 또는 ID 검색" dense hide-details prepend-inner-icon="mdi-magnify" />
          </v-col>
          <v-col cols="6" md="3" class="pr-2">
            <v-select label="역할 필터" :items="['전체', ...roles]" v-model="roleFilter" dense hide-details />
          </v-col>
          <v-col cols="6" md="3">
            <v-btn color="primary" @click="addUser" block>사용자 추가</v-btn>
          </v-col>
        </v-row>

        <!-- 테이블 -->
        <v-checkbox
          v-model="hideExpired"
          label="만료 사용자 숨기기"
          density="compact"
          class="mb-2"
        />
            <v-data-table
              :headers="headers"
              :items="filteredUsers"
              item-key="id"
              class="elevation-1"
              density="comfortable"
              :items-per-page-options="[10, 20, 30]"
              :items-per-page="10"
              :item-class="item => !item.active ? 'inactive-orange-text' : ''"
            >

            <template #item.actions="{ item }">
              <v-btn icon @click="editUser(item)" size="x-small">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn icon @click="deleteUser(item.id)" size="x-small">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
              <v-btn
                size="x-small"
                @click="toggleUserActivation(item)"
                class="activation-btn"
                variant="outlined"
              >
                {{ item.active ? '비활성화' : '활성화' }}
              </v-btn>
               <!-- ✅ 비활성화 상태인 경우에만 아이콘 + 배지 표시 -->
  <span v-if="!item.active" class="ml-2 d-inline-flex align-center">
    <v-icon size="14" color="orange" class="mr-1">mdi-alert-circle</v-icon>
    <v-chip label small color="orange" text-color="white" variant="flat">
      비활성화됨
    </v-chip>
  </span>
  <v-btn icon @click="openReport(item)" size="x-small">
  <v-icon>mdi-file-document</v-icon>
</v-btn>

            </template>
          <template #item.daysLeft="{ item }">
          <span :style="{ color: item.daysLeft < 0 ? 'red' : undefined }">
            {{ item.daysLeft }}일
          </span>
        </template>

          <!--
          <template #item.usageChart="{ item }">
            <div class="chart-cell">
              <div class="chart-wrapper">
                <canvas :ref="el => renderGradientChart(el, item.usageTimestamps, item.cpuUsage)" />
                <small>CPU</small>
              </div>
              <div class="chart-wrapper">
                <canvas :ref="el => renderGradientChart(el, item.usageTimestamps, item.gpuUsage)" />
                <small>GPU</small>
              </div>
              <div class="chart-wrapper">
                <canvas :ref="el => renderGradientChart(el, item.usageTimestamps, item.memUsage)" />
                <small>MEM</small>
              </div>
            </div>
          </template>
          -->
        </v-data-table>

        <!-- 권한 관리 -->
        <v-card class="mt-8" v-if="selectedRole">
          <v-card-title>권한 관리 - {{ selectedRole }}</v-card-title>
          <v-card-text>
            <v-checkbox v-for="(perm, index) in permissions" :key="index" :label="perm.label" v-model="perm.value" />
            <v-btn color="primary" @click="savePermissions">저장</v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 사용자 추가 -->
    <v-dialog v-model="dialogAdd" max-width="500">
      <v-card>
        <v-card-title class="text-h6">사용자 추가</v-card-title>
        <v-card-text>
  <v-text-field label="아이디" v-model="newUser.id" />
  <v-text-field label="이름" v-model="newUser.name" />
  <v-select label="역할" :items="roles" v-model="newUser.role" />
  <v-text-field
    label="사용 기한"
    v-model="newUser.expiry"
    type="date"
  />
</v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn text @click="dialogAdd = false">취소</v-btn>
          <v-btn color="primary" @click="confirmAddUser">추가</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 사용자 수정 -->
    <v-dialog v-model="dialogEdit" max-width="500">
      <v-card>
        <v-card-title class="text-h6">사용자 수정</v-card-title>
        <v-card-text>
  <v-text-field label="아이디" v-model="editUserData.id" disabled />
  <v-text-field label="이름" v-model="editUserData.name" />
  <v-select label="역할" :items="roles" v-model="editUserData.role" />
  <v-text-field
    label="사용 기한"
    v-model="editUserData.expiry"
    type="date"
  />
</v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="dialogEdit = false">취소</v-btn>
          <v-btn color="primary" @click="confirmEditUser">저장</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale } from 'chart.js'
import { useRouter } from 'vue-router'

Chart.register(LineController, LineElement, PointElement, LinearScale, Title, CategoryScale)



const users = ref([])
const roles = ref(['관리자', '일반 사용자'])
const searchKeyword = ref('')
const roleFilter = ref('전체')
const dialogAdd = ref(false)
const dialogEdit = ref(false)
const selectedRole = ref('')
const newUser = ref({ id: '', name: '', role: '', expiry: '' })
const editUserData = ref({ id: '', name: '', role: '', expiry: '' })
const permissions = ref([
  { label: '자원 할당', value: false },
  { label: '자원 회수', value: false },
  { label: '사용자 계정 관리', value: false }
])

const headers = [
  { title: '아이디', key: 'id' },
  { title: '이름', key: 'name' },
  { title: '역할', key: 'role' },
  { title: '사용 기한', key: 'expiry' },
  { title: '남은 일수', key: 'daysLeft' },
  { title: '조치', key: 'actions', sortable: false, width: '400px' } // ✅ 여유  고정
]


const hideExpired = ref(false)



const filteredUsers = computed(() =>
  users.value
    .map(user => {
      const today = new Date()
      const expiry = new Date(user.expiry)
      const msPerDay = 1000 * 60 * 60 * 24
      const daysLeft = Math.floor((expiry - today) / msPerDay)

      return {
        ...user,
        daysLeft
      }
    })
    .filter(user =>
      (user.id.includes(searchKeyword.value) || user.name.includes(searchKeyword.value)) &&
      (roleFilter.value === '전체' || user.role === roleFilter.value) &&
      (!hideExpired.value || user.daysLeft >= 0)
    )
)

const toggleUserActivation = async (user) => {
  const action = user.active ? 'deactivate' : 'activate'
  const confirmed = confirm(`정말로 ${user.name} 계정을 ${user.active ? '비활성화' : '활성화'}하시겠습니까?`)
  if (!confirmed) return

  const res = await axios.post(`http://localhost:5002/api/users/${user.id}/${action}`)
  const idx = users.value.findIndex(u => u.id === user.id)
  if (idx !== -1) users.value[idx] = res.data.user
}


const router = useRouter()

const openReport = (user) => {
  router.push({ path: '/userReport', query: { id: user.id } })
}


const fetchUsers = async () => {
  const res = await axios.get('http://localhost:5002/api/users')
  users.value = res.data
}


const addUser = () => {
  newUser.value = { id: '', name: '', role: '' }
  dialogAdd.value = true
}

const confirmAddUser = async () => {
  if (!newUser.value.id || !newUser.value.name || !newUser.value.role) return alert('모든 항목을 입력해주세요.')
  if (users.value.some(u => u.id === newUser.value.id)) return alert('이미 존재하는 아이디입니다.')
  const res = await axios.post('http://localhost:5002/api/users', newUser.value)
  users.value.push(res.data.user)
  dialogAdd.value = false
}

const editUser = (user) => {
  editUserData.value = { ...user }
  dialogEdit.value = true
}

const confirmEditUser = async () => {
  const res = await axios.put(`http://localhost:5002/api/users/${editUserData.value.id}`, {
    name: editUserData.value.name,
    role: editUserData.value.role,
    expiry: editUserData.value.expiry
  })
  const idx = users.value.findIndex(u => u.id === editUserData.value.id)
  if (idx !== -1) users.value[idx] = res.data.user
  dialogEdit.value = false
}

const deleteUser = async (userId) => {
  await axios.delete(`http://localhost:5002/api/users/${userId}`)
  users.value = users.value.filter(u => u.id !== userId)
}

watch(selectedRole, async (newRole) => {
  if (!newRole) return
  const res = await axios.get(`http://localhost:5002/api/roles/${newRole}`)
  const savedPerms = res.data.permissions || []
  permissions.value.forEach(p => p.value = savedPerms.includes(p.label))
})

const savePermissions = async () => {
  if (!selectedRole.value) return alert('역할을 선택하세요.')
  const selectedPerms = permissions.value.filter(p => p.value).map(p => p.label)
  await axios.post('http://localhost:5002/api/roles', {
    role: selectedRole.value,
    permissions: selectedPerms
  })
  alert('권한 저장 완료')
}


// const chartInstances = new WeakMap()
/*
const renderGradientChart = async (canvas, labels, values) => {
  await nextTick()
  if (!canvas || !values) return

  const ctx = canvas.getContext('2d')

  if (chartInstances.has(canvas)) {
    chartInstances.get(canvas).destroy()
  }

  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: '사용률',
          data: values,
          borderWidth: 2,
          fill: false,
          tension: 0.4,
          pointRadius: 0,
          borderColor: (ctx) => {
            const chart = ctx.chart
            const { ctx: context, chartArea } = chart
            if (!chartArea) return '#ccc'
            const gradient = context.createLinearGradient(0, chartArea.bottom, 0, chartArea.top)
            gradient.addColorStop(0, '#12c2e9')
            gradient.addColorStop(0.5, '#f9d423')
            gradient.addColorStop(1, '#ff0033')
            return gradient
          }
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales: {
        x: {
          display: true,
          ticks: { color: '#888', font: { size: 10 } },
          grid: { display: false }
        },
        y: { display: false }
      }
    }
  })

  chartInstances.set(canvas, chart)
}*/

const fetchUserById = async (id) => {
  const response = await fetch(`http://localhost:5002/api/users/${id}/report`)
  if (!response.ok) throw new Error('User not found')
  return await response.json()
}

onMounted(fetchUsers)
</script>

<style scoped>
.chart-cell {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chart-wrapper {
  height: 75px;
  position: relative;
}

.chart-wrapper canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}
.chart-wrapper small {
  position: absolute;
  top: 0;
  left: 4px;
  font-size: 10px;
  color: #aaa;
}
.activation-btn {
  min-width: 64px;
  padding: 0 8px;
  font-size: 10px;
  text-transform: none;
  height: 28px;
}
.inactive-orange-text td {
  color: #FFA500 !important; /* 주황색 글씨 */
  font-weight: 500;
}
</style>