<template>
    <v-btn @click="showDialog = true">삭제</v-btn>

    <v-dialog v-model="showDialog" max-width="400px">
        <v-card>
            <v-card-title>정말 삭제하시겠습니까?</v-card-title>
            <v-card-actions>
                <v-spacer />
                <v-btn @click="showDialog = false">취소</v-btn>
                <v-btn color="error" @click="deleteUser">확인</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

// Props 정의 (삭제할 사용자 ID를 받아옴)
const props = defineProps({
    userName: {
        type: [String, Number],
        required: true,
    },
});

const API_URL = `http://localhost:8000/api/sample/users/${props.userName}`;

const showDialog = ref(false);
const loading = ref(false);
const errorMessage = ref('');

const deleteUser = async () => {
    loading.value = true;
    errorMessage.value = '';
    try {
        await axios.delete(API_URL);
        window.location.reload();
    } catch (e) {
        errorMessage.value = e.response?.data?.message || '삭제에 실패했습니다.';
    } finally {
        loading.value = false;
    }
};

</script>
