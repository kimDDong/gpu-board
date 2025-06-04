<template>
  <v-row>
    <!-- 사용자 목록 -->
    <v-col cols="12">
      <v-card>
        <v-card-title>사용자 계정 관리</v-card-title>
        <v-card-text>
          <v-btn color="primary" @click="addUser">사용자 추가</v-btn>
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
              <tr v-for="(user, index) in users" :key="index">
                <td>{{ user.id }}</td>
                <td>{{ user.name }}</td>
                <td>{{ user.role }}</td>
                <td>
                  <v-btn size="small" @click="editUser(user)">수정</v-btn>
                  <v-btn size="small" @click="deleteUser(user.id)">삭제</v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </v-col>

    <!-- 역할 및 권한 관리 -->
    <v-col cols="12" md="6" class="mt-5">
      <v-card>
        <v-card-title>역할 및 권한 관리</v-card-title>
        <v-card-text>
          <v-select label="역할 선택" :items="roles" v-model="selectedRole" />
          <v-checkbox
            v-for="(perm, index) in permissions"
            :key="index"
            :label="perm.label"
            v-model="perm.value"
          />
          <v-btn @click="savePermissions">저장</v-btn>
        </v-card-text>
      </v-card>
    </v-col>

    <!-- 사용자 추가 다이얼로그 -->
    <v-dialog v-model="dialogAdd" max-width="500">
      <v-card>
        <v-card-title>사용자 추가</v-card-title>
        <v-card-text>
          <v-text-field label="아이디" v-model="newUser.id" />
          <v-text-field label="이름" v-model="newUser.name" />
          <v-select label="역할" :items="roles" v-model="newUser.role" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="dialogAdd = false">취소</v-btn>
          <v-btn color="primary" @click="confirmAddUser">추가</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>

  <!-- 사용자 수정 다이얼로그 -->
  <v-dialog v-model="dialogEdit" max-width="500">
    <v-card>
      <v-card-title>사용자 수정</v-card-title>
      <v-card-text>
        <v-text-field label="아이디" v-model="editUserData.id" disabled />
        <v-text-field label="이름" v-model="editUserData.name" />
        <v-select label="역할" :items="roles" v-model="editUserData.role" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="dialogEdit = false">취소</v-btn>
        <v-btn color="primary" @click="confirmEditUser">저장</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>


  <v-card-text>
    <v-row class="mb-3" align="center">
      <v-col cols="12" md="6">
        <v-text-field
          label="이름 또는 아이디 검색"
          v-model="searchKeyword"
          clearable
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          label="역할 필터"
          :items="['전체', ...roles]"
          v-model="roleFilter"
          clearable
        />
      </v-col>
    </v-row>

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
        <tr v-for="(user, index) in filteredUsers" :key="index">
          <td>{{ user.id }}</td>
          <td>{{ user.name }}</td>
          <td>{{ user.role }}</td>
          <td>
            <v-btn size="small" @click="editUser(user)">수정</v-btn>
            <v-btn size="small" @click="deleteUser(user.id)">삭제</v-btn>
          </td>
        </tr>
      </tbody>
    </v-table>
  </v-card-text>


</template>


<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'

// 사용자 목록 상태
const users = ref([])

// 역할 목록
const roles = ref(['관리자', '일반 사용자'])



const searchKeyword = ref('')
const roleFilter = ref('전체')

const filteredUsers = computed(() => {
  return users.value.filter(user => {
    const matchKeyword =
      user.id.includes(searchKeyword.value) ||
      user.name.includes(searchKeyword.value)

    const matchRole =
      roleFilter.value === '전체' || roleFilter.value === '' || user.role === roleFilter.value

    return matchKeyword && matchRole
  })
})

const dialogEdit = ref(false)
const editUserData = ref({
  id: '',
  name: '',
  role: ''
})

const editUser = (user) => {
  editUserData.value = { ...user }
  dialogEdit.value = true
}

const confirmEditUser = async () => {
  try {
    const res = await axios.put(
      `http://localhost:5002/api/users/${editUserData.value.id}`,
      {
        name: editUserData.value.name,
        role: editUserData.value.role
      }
    )
    // 수정된 사용자 정보로 반영
    const idx = users.value.findIndex(u => u.id === editUserData.value.id)
    if (idx !== -1) {
      users.value[idx] = res.data.user
    }
    dialogEdit.value = false
  } catch (error) {
    console.error('수정 실패:', error)
    alert('사용자 수정 중 오류 발생')
  }
}


const selectedRole = ref('')

// 권한 목록
const permissions = ref([
  { label: '자원 할당', value: false },
  { label: '자원 회수', value: false },
  { label: '사용자 계정 관리', value: false }
])

watch(selectedRole, async (newRole) => {
  if (!newRole) return

  try {
    const res = await axios.get(`http://localhost:5000/api/roles/${newRole}`)
    const savedPerms = res.data.permissions || []

    // 전체 권한 체크박스 상태 초기화 후 반영
    permissions.value.forEach(p => {
      p.value = savedPerms.includes(p.label)
    })
  } catch (err) {
    console.error('권한 불러오기 실패:', err)
  }
})


// 사용자 추가용 상태
const dialogAdd = ref(false)
const newUser = ref({
  id: '',
  name: '',
  role: ''
})

// API로 사용자 목록 불러오기
const fetchUsers = async () => {
  try {
    const res = await axios.get('http://localhost:5002/api/users')
    users.value = res.data
  } catch (err) {
    console.error('사용자 데이터를 불러오지 못했습니다.', err)
  }
}

// 사용자 추가 버튼 클릭 시
const addUser = () => {
  newUser.value = { id: '', name: '', role: '' }
  dialogAdd.value = true
}

// 사용자 실제 추가
const confirmAddUser = async () => {
  if (!newUser.value.id || !newUser.value.name || !newUser.value.role) {
    alert('모든 항목을 입력해주세요.')
    return
  }

  try {
    // 서버에 POST 요청 보내기
    const res = await axios.post('http://localhost:5002/api/users', newUser.value)
    users.value.push(res.data.user)  // 응답 데이터 기반으로 테이블 갱신
    dialogAdd.value = false
  } catch (error) {
    console.error('사용자 추가 실패:', error)
    alert('사용자 추가 중 오류 발생')
  }
}


// 사용자 삭제
const deleteUser = async (userId) => {
  try {
    await axios.delete(`http://localhost:5002/api/users/${userId}`)
    users.value = users.value.filter(u => u.id !== userId)
  } catch (error) {
    console.error('사용자 삭제 실패:', error)
    alert('사용자 삭제 중 오류 발생')
  }
}
// 권한 저장
const savePermissions = async () => {
  if (!selectedRole.value) {
    alert('역할을 먼저 선택하세요.')
    return
  }

  const selectedPerms = permissions.value
    .filter(p => p.value)
    .map(p => p.label)

  try {
    await axios.post('http://localhost:5002/api/roles', {
      role: selectedRole.value,
      permissions: selectedPerms
    })
    alert(`${selectedRole.value} 권한이 저장되었습니다.`)
  } catch (error) {
    console.error('권한 저장 실패:', error)
    alert('권한 저장 중 오류 발생')
  }
}



// 초기 실행
onMounted(() => {
  fetchUsers()
})
</script>
