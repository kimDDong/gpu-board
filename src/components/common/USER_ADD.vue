<!-- UserRegistrationDialog.vue -->
<template>

    <!-- 추가 버튼 (항상 보임) -->
    <v-btn color="primary" @click="openRegistrationDialog">
        추가
    </v-btn>

    <!-- 추가 팝업 다이얼로그 -->
    <v-dialog v-model="showDialog" persistent max-width="600px">
        <v-card>
            <v-card-title class="headline d-flex align-center">
                추가
                <v-spacer></v-spacer>
                <!-- 닫기 버튼 -->
                <v-btn icon @click="closeRegistrationDialog" :disabled="loading">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
            </v-card-title>
            <v-card-text>
                <v-form ref="registrationForm" v-model="valid" @submit.prevent="submitForm">
                    <v-text-field v-model="formData.username" label="사용자명" :rules="[rules.required]" required
                        prepend-inner-icon="mdi-account"></v-text-field>

                    <v-text-field v-model="formData.password" label="비밀번호"
                        :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                        :type="showPassword ? 'text' : 'password'" :rules="[rules.required, rules.minPasswordLength]"
                        @click:append-inner="showPassword = !showPassword" required
                        prepend-inner-icon="mdi-lock"></v-text-field>

                    <v-text-field v-model="formData.confirmPassword" label="비밀번호 확인"
                        :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
                        :type="showConfirmPassword ? 'text' : 'password'" :rules="[rules.required, rules.passwordMatch]"
                        @click:append-inner="showConfirmPassword = !showConfirmPassword" required
                        prepend-inner-icon="mdi-lock-check"></v-text-field>

                    <v-text-field v-model="formData.fullName" label="전체 이름" :rules="[rules.required]" required
                        prepend-inner-icon="mdi-card-account-details"></v-text-field>

                    <v-checkbox v-model="formData.initialActivation" label="활성화 여부" color="primary"
                        prepend-inner-icon="mdi-check-circle"></v-checkbox>

                    <v-text-field v-model.number="formData.usagePeriod" label="사용 기한 (일)" type="number"
                        :rules="[rules.required, rules.number, rules.minUsagePeriod]" required min="1"
                        prepend-inner-icon="mdi-calendar-range"></v-text-field>

                    <v-alert v-if="errorMessage" type="error" closable class="mt-4" @click:close="errorMessage = ''">
                        {{ errorMessage }}
                    </v-alert>
                </v-form>
            </v-card-text>

            <v-card-actions class="mt-4">
                <v-spacer></v-spacer>
                <v-btn color="grey" variant="flat" @click="closeRegistrationDialog" :disabled="loading">
                    취소
                </v-btn>
                <v-btn color="primary" type="submit" @click="submitForm" :disabled="!valid || loading"
                    :loading="loading">
                    추가
                    <template v-slot:loader>
                        <v-progress-circular indeterminate size="24"></v-progress-circular>
                    </template>
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import axios from 'axios';

const formData = ref({
    username: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    initialActivation: true, // 기본값 true
    usagePeriod: 30, // 기본값 30일
});
const API_URL = 'http://localhost:8000/api/sample/users'; // 실제 백엔드 API 주소

// 폼 참조
const registrationForm = ref(null);

// 반응형 데이터
const showDialog = ref(false); // 팝업(v-dialog)의 가시성 제어
const valid = ref(false); // 폼 전체의 유효성 상태
const loading = ref(false); // API 호출 중 로딩 상태
const showPassword = ref(false); // 비밀번호 보이기/숨기기 토글
const showConfirmPassword = ref(false); // 비밀번호 확인 보이기/숨기기 토글
const errorMessage = ref(''); // API 호출 실패 시 에러 메시지

// 유효성 검사 규칙
const rules = {
    required: value => !!value || '필수 항목입니다.',
    minPasswordLength: value => (value && value.length >= 6) || '비밀번호는 6자 이상이어야 합니다.',
    passwordMatch: value =>
        value === formData.value.password || '비밀번호가 일치하지 않습니다.',
    number: value => !isNaN(parseFloat(value)) && isFinite(value) || '숫자만 입력 가능합니다.',
    minUsagePeriod: value => (value && value >= 1) || '사용 기한은 1일 이상이어야 합니다.'
};


// --- Methods ---

// 다이얼로그 열기
const openRegistrationDialog = () => {
    showDialog.value = true;
    resetFormAndMessages(); // 폼을 열기 전에 초기화
};

// 다이얼로그 닫기 (취소 또는 닫기 버튼 클릭 시)
const closeRegistrationDialog = () => {
    if (loading.value) return; // 제출 중에는 닫기 비활성화
    showDialog.value = false;
    resetFormAndMessages(); // 폼 데이터 및 유효성 상태 초기화
};

// 폼 데이터, 유효성, 메시지 초기화
const resetFormAndMessages = () => {
    if (registrationForm.value) {
        registrationForm.value.reset(); // Vuetify 폼 유효성 상태 초기화
        registrationForm.value.resetValidation(); // 유효성 메시지 초기화
    }

    formData.value = {
        username: '',
        password: '',
        confirmPassword: '',
        fullName: '',
        initialActivation: true,
        usagePeriod: 30,
    };
    loading.value = false;
    valid.value = false;
    showPassword.value = false;
    showConfirmPassword.value = false;
    errorMessage.value = ''; // 에러 메시지 초기화
};

// 폼 제출 핸들러
const submitForm = async () => {
    const { valid: formIsValid } = await registrationForm.value.validate();
    if (!formIsValid) {
        errorMessage.value = '입력된 정보를 확인해주세요.';
        return;
    }

    loading.value = true; // 로딩 상태 활성화
    errorMessage.value = ''; // 이전 에러 메시지 초기화

    try {
        // 서버로 보낼 데이터 (confirmPassword는 제외)
        const dataToSend = {
            username: formData.value.username,
            password: formData.value.password,
            fullName: formData.value.fullName,
            initialActivation: formData.value.initialActivation,
            usagePeriod: formData.value.usagePeriod,
        };

        // axios를 사용하여 POST 요청
        const response = await axios.post(API_URL, dataToSend);

        console.log('추가 성공:', response.data);

        // 성공 시 다이얼로그 닫고 지정된 URL로 리다이렉션
        showDialog.value = false; // 다이얼로그 닫기
        window.location.reload();

    } catch (error) {
        console.error('추가 실패:', error);
        // 에러 메시지 처리
        if (error.response) {
            // 서버 응답이 있는 경우 (예: 4xx, 5xx 에러)
            errorMessage.value = error.response.data.message || '추가에 실패했습니다. 서버 오류.';
        } else if (error.request) {
            // 요청은 보내졌지만 응답을 받지 못한 경우 (예: 네트워크 오류)
            errorMessage.value = '네트워크 오류: 서버에 연결할 수 없습니다.';
        } else {
            // 그 외 오류
            errorMessage.value = '알 수 없는 오류가 발생했습니다.';
        }
    } finally {
        loading.value = false; // 로딩 상태 비활성화
    }
};

// 비밀번호 필드 변경 감지하여 유효성 재검사 (선택적)
watch([() => formData.value.password, () => formData.value.confirmPassword], () => {
    if (registrationForm.value) {
        registrationForm.value.validate();
    }
});
</script>

<style scoped>
/* 컴포넌트 자체에 특별한 스타일이 필요하다면 여기에 추가 */
.v-card {
    border-radius: 8px;
    /* box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); */
    /* v-dialog 자체 그림자가 더 우선 */
}
</style>