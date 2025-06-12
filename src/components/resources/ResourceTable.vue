<template>
  <div>
    <v-expansion-panels>
      <v-expansion-panel v-for="u in users" :key="u">
        <v-expansion-panel-title>{{ u }}</v-expansion-panel-title>
        <v-expansion-panel-text>
          <div v-for="t in ['GPU','CPU']" :key="t">
            <h4>{{ t }} 자원</h4>
            <v-table>
              <thead>
                <tr>
                  <th>번호</th>
                  <th>기간</th>
                  <th>조치</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="r in resources.filter(rr => rr.user === u && rr.type === t)"
                  :key="t + '_' + r.res_id"
                >
                  <td>{{ r.res_id }}</td>
                  <td>{{ r.start_date }} ~ {{ r.end_date }}</td>
                  <td>
                    <v-btn size="small" color="error" @click="$emit('reclaim', r)">회수</v-btn>
                  </td>
                </tr>
              </tbody>
            </v-table>
            <div>
              <v-btn
                v-for="r in resources.filter(rr => !rr.user && rr.type === t)"
                :key="t + '_free_' + r.res_id"
                size="small"
                color="success"
                class="ma-1"
                @click="$emit('allocate', { ...r, user: u, type: t })"
              >
                자원 {{ r.res_id }} 할당
              </v-btn>
              <!-- 여러 자원 할당 (GPU/CPU 둘 다) -->
              <v-btn
                size="small"
                color="primary"
                class="ma-1"
                @click="$emit('multi-allocate', { user: u, type: t })"
              >
                여러 자원 할당
              </v-btn>
            </div>
          </div>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </div>
</template>
<script setup>
const props = defineProps({
  users: Array,
  resources: Array
})
defineEmits(['reclaim', 'allocate', 'multi-allocate'])
</script>
