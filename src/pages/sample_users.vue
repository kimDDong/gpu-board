<script setup>
import USER_ADD from '@/components/common/USER_ADD.vue';
import USER_TABLE from '@/components/common/USER_TABLE.vue';
</script>

<template>
  <v-container fluid class="pa-4" style="height:100vh;width:100vw;">
    <v-row>
      <v-col>
        <v-card-text class="py-4">
          <span style="font-size: 200%;">
            README: 사용자 관련
          </span>
        </v-card-text>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <USER_ADD />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <USER_TABLE />
        <!-- <USER_MOD :user-id="123" /> -->
      </v-col>
    </v-row>

  </v-container>
</template>