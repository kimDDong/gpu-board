<script setup>
import KPI from '@/components/dashboard/KPI.vue'
import CPU_1 from '@/components/dashboard/CPU_1.vue'
import CPU_2 from '@/components/dashboard/CPU_2.vue'
import GPU_1 from '@/components/dashboard/GPU_1.vue'
import GPU_2 from '@/components/dashboard/GPU_2.vue'
import USER_CPU from '@/components/dashboard/USER_CPU.vue'
import USER_GPU from '@/components/dashboard/USER_GPU.vue'
import USER_MEM from '@/components/dashboard/USER_MEM.vue'
import USER_IDLE from '@/components/dashboard/USER_IDLE.vue'

</script>

<template>
  <v-container fluid class="pa-4" style="height:100vh;width:100vw;">

    <KPI />

    <v-row>
      <v-col>
        <CPU_2 />
      </v-col>  
      <v-col>
        <CPU_1 />
      </v-col>  
    </v-row>

    <v-row>
      <v-col>
        <GPU_2 />
      </v-col>  
      <v-col>
        <v-row>
        <v-col><GPU_1 /></v-col>
        </v-row>
        <v-row>
        <v-col><GPU_3 /></v-col>
        </v-row>
      </v-col>  
    </v-row>
    
    <v-row>
      <v-col>
        <USER_CPU />
      </v-col>
            <v-col>
        <USER_GPU />
      </v-col>
            <v-col>
        <USER_MEM />
      </v-col>
            <v-col>
        <USER_IDLE />
      </v-col>
    </v-row>
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
