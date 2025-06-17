<!-- UserTable.vue -->
<template>

    <div v-if="loadingUsers" class="text-center py-5">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
        <p class="mt-3">사용자 목록을 불러오는 중...</p>
    </div>

    <!-- 사용자 목록 에러 메시지 -->
    <v-alert v-if="userListErrorMessage" type="error" closable class="mt-4" @click:close="userListErrorMessage = ''">
        {{ userListErrorMessage }}
    </v-alert>

    <!-- 사용자 목록 테이블 -->
    <v-data-table v-else :headers="headers" :items="users" :items-per-page="10" class="elevation-1"
        :loading="loadingUsers" loading-text="데이터를 불러오는 중..." no-data-text="사용자가 없습니다.">
        <template v-slot:item.initialActivation="{ item }">
            <v-icon :color="item.initialActivation ? 'success' : 'error'">
                {{ item.initialActivation ? 'mdi-check-circle' : 'mdi-close-circle' }}
            </v-icon>
        </template>

        <template v-slot:item.createdAt="{ item }">
            {{ formatDateTime(item.createdAt) }}
        </template>

        <template v-slot:item.expiredAt="{ item }">
            {{ formatDateTime(item.expiredAt) }}
        </template>

        <template v-slot:item.report="{ item }">
            <!-- <v-btn @click="window.location.href = `/users/${item.username}/report`"> -->
            <v-btn @click="goToUrl(`/users/${item.username}/report`)">
                리포트
            </v-btn>
        </template>

        <template v-slot:item.modify="{ item }">
            <USER_MOD :userName="item.username" />
        </template>

        <template v-slot:item.delete="{ item }">
            <USER_DEL :userName="item.username" />
        </template>

    </v-data-table>

</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

import USER_MOD from './USER_MOD.vue';
import USER_DEL from './USER_DEL.vue';

const API_URL = 'https://gpu-board.onrender.com/api/sample/users';

// --- Data for User Table ---
const users = ref([]);
const loadingUsers = ref(true);
const userListErrorMessage = ref('');

const headers = ref([
    { title: '사용자명', align: 'start', key: 'username' },
    { title: '전체 이름', key: 'fullName' },
    { title: '활성화 여부', key: 'initialActivation' },
    { title: '사용 기한 (일)', key: 'usagePeriod' },
    { title: '생성된 날짜', key: 'createdAt' },
    { title: '만료 날짜', key: 'expiredAt' },
    { title: '리포트', key: 'report', sortable: false },
    { title: '수정', key: 'modify', sortable: false },
    { title: '제거', key: 'delete', sortable: false },
]);

// --- Methods ---

const goToUrl = (url) => {
    window.location.href = url;
};

// 날짜 포맷팅 헬퍼 함수 (두 컴포넌트에서 재사용)
const formatDateTime = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        // hour: '2-digit',
        // minute: '2-digit',
        // second: '2-digit',
        // hour12: false,
    });
};

// 사용자 목록 불러오기
const fetch = async () => {
    loadingUsers.value = true;
    userListErrorMessage.value = '';
    try {
        const response = await axios.get(API_URL);
        users.value = response.data;
    } catch (error) {
        console.error('사용자 목록 불러오기 실패:', error);
        userListErrorMessage.value = '사용자 목록을 불러오는데 실패했습니다.';
    } finally {
        loadingUsers.value = false;
    }
};

// --- Component Lifecycle ---
onMounted(() => {
    fetch(); // 컴포넌트 마운트 시 사용자 목록 불러오기
});
</script>