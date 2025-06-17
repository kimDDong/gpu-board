<template>

    <v-btn @click="openEditDialog">
        수정
    </v-btn>

    <!-- 수정 팝업 다이얼로그 -->
    <v-dialog v-model="showDialog" persistent max-width="600px">
        <v-card>
            <v-card-title class="headline d-flex align-center">
                수정
                <v-spacer></v-spacer>
                <!-- 닫기 버튼 -->
                <v-btn icon @click="closeEditDialog" :disabled="loadingSubmit">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
            </v-card-title>
            <v-card-text>
                <!-- 초기 데이터 로딩 중 -->
                <div v-if="loadingInitialData" class="text-center py-5">
                    <v-progress-circular indeterminate color="primary"></v-progress-circular>
                    <p class="mt-3">사용자 정보를 불러오는 중...</p>
                </div>

                <!-- 폼 -->
                <v-form v-else ref="editForm" v-model="valid" @submit.prevent="submitForm">
                    <v-text-field v-model="FROM_DATA.username" label="사용자명" :rules="[rules.required]" required disabled
                        prepend-inner-icon="mdi-account" hint="사용자명은 수정할 수 없습니다." persistent-hint></v-text-field>

                    <v-text-field v-model="newPassword" label="새 비밀번호 (변경 시 입력)"
                        :append-inner-icon="showNewPassword ? 'mdi-eye' : 'mdi-eye-off'"
                        :type="showNewPassword ? 'text' : 'password'"
                        :rules="newPassword ? [rules.minPasswordLength] : []"
                        @click:append-inner="showNewPassword = !showNewPassword"
                        prepend-inner-icon="mdi-lock"></v-text-field>

                    <v-text-field v-model="confirmNewPassword" label="새 비밀번호 확인"
                        :append-inner-icon="showConfirmNewPassword ? 'mdi-eye' : 'mdi-eye-off'"
                        :type="showConfirmNewPassword ? 'text' : 'password'"
                        :rules="newPassword ? [rules.passwordMatch] : []"
                        @click:append-inner="showConfirmNewPassword = !showConfirmNewPassword"
                        prepend-inner-icon="mdi-lock-check"></v-text-field>

                    <v-text-field v-model="FROM_DATA.fullName" label="전체 이름" :rules="[rules.required]" required
                        prepend-inner-icon="mdi-card-account-details"></v-text-field>

                    <v-checkbox v-model="FROM_DATA.initialActivation" label="활성화 여부" color="primary"
                        prepend-inner-icon="mdi-check-circle"></v-checkbox>

                    <v-text-field v-model.number="FROM_DATA.usagePeriod" label="사용 기한 (일)" type="number"
                        :rules="[rules.required, rules.number, rules.minUsagePeriod]" required min="1"
                        prepend-inner-icon="mdi-calendar-range"></v-text-field>

                    <v-alert v-if="errorMessage" type="error" closable class="mt-4" @click:close="errorMessage = ''">
                        {{ errorMessage }}
                    </v-alert>

                    <v-alert v-if="successMessage" type="success" closable class="mt-4"
                        @click:close="successMessage = ''">
                        {{ successMessage }}
                    </v-alert>

                </v-form>
            </v-card-text>

            <v-card-actions class="mt-4">
                <v-spacer></v-spacer>
                <v-btn color="grey" variant="flat" @click="closeEditDialog" :disabled="loadingSubmit">
                    취소
                </v-btn>
                <v-btn color="primary" type="submit" @click="submitForm" :disabled="!valid || loadingSubmit"
                    :loading="loadingSubmit">
                    수정
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

// Props 정의 (수정할 사용자 ID를 받아옴)
const props = defineProps({
    userName: {
        type: [String, Number],
        required: true,
    },
});

const FROM_DATA = ref({
    username: '',
    fullName: '',
    initialActivation: false,
    usagePeriod: 0,
});

const API_URL = `https://gpu-board.onrender.com/api/sample/users/${props.userName}`;

// 폼 참조
const editForm = ref(null);

// 반응형 데이터
const showDialog = ref(false); // 팝업(v-dialog)의 가시성 제어
const loadingInitialData = ref(false); // 초기 데이터 로딩 상태
const loadingSubmit = ref(false); // 폼 제출 시 로딩 상태
const valid = ref(false); // 폼 전체의 유효성 상태
const errorMessage = ref(''); // API 호출 실패 시 에러 메시지
const successMessage = ref(''); // API 호출 성공 시 성공 메시지

const showNewPassword = ref(false);
const showConfirmNewPassword = ref(false);

const newPassword = ref('');
const confirmNewPassword = ref('');

// 유효성 검사 규칙
const rules = {
    required: value => !!value || '필수 항목입니다.',
    minPasswordLength: value => (value && value.length >= 6) || '비밀번호는 6자 이상이어야 합니다.',
    passwordMatch: value =>
        value === newPassword.value || '새 비밀번호가 일치하지 않습니다.',
    number: value => !isNaN(parseFloat(value)) && isFinite(value) || '숫자만 입력 가능합니다.',
    minUsagePeriod: value => (value && value >= 1) || '사용 기한은 1일 이상이어야 합니다.'
};

// --- Methods ---

// 다이얼로그 열기 및 데이터 로드 시작
const openEditDialog = () => {
    showDialog.value = true; // 다이얼로그 표시
    resetFormAndMessages(); // 폼 데이터, 유효성, 메시지 초기화
    fetchUserData(); // 데이터 로드 시작
};

// 다이얼로그 닫기 (취소 또는 닫기 버튼 클릭 시)
const closeEditDialog = () => {
    if (loadingSubmit.value) return; // 제출 중에는 닫기 비활성화
    showDialog.value = false; // 다이얼로그 숨기기
    resetFormAndMessages(); // 폼 데이터, 유효성, 메시지 초기화
};

// 초기 사용자 정보 불러오기
const fetchUserData = async () => {
    loadingInitialData.value = true;
    errorMessage.value = '';
    try {
        const response = await axios.get(API_URL);
        // 실제 API 응답 구조에 맞게 매핑
        FROM_DATA.value = {
            username: response.data.username,
            fullName: response.data.fullName,
            initialActivation: response.data.initialActivation,
            usagePeriod: response.data.usagePeriod,
        };
    } catch (error) {
        console.error('사용자 정보 불러오기 실패:', error);
        errorMessage.value = '사용자 정보를 불러오는데 실패했습니다.';
        // 에러 발생 시 다이얼로그를 닫거나, 계속 에러 메시지를 보여줄 수 있습니다.
        // 여기서는 일단 다이얼로그는 열어두고 에러 메시지를 보여줍니다.
    } finally {
        loadingInitialData.value = false;
    }
};

// 폼 데이터, 유효성, 메시지 초기화
const resetFormAndMessages = () => {
    if (editForm.value) {
        editForm.value.reset();
        editForm.value.resetValidation();
    }
    FROM_DATA.value = {
        username: '',
        fullName: '',
        initialActivation: false,
        usagePeriod: 0,
    };
    newPassword.value = '';
    confirmNewPassword.value = '';
    valid.value = false;
    errorMessage.value = '';
    successMessage.value = '';
    loadingSubmit.value = false;
    showNewPassword.value = false;
    showConfirmNewPassword.value = false;
};

// 폼 제출 핸들러
const submitForm = async () => {
    const { valid: formIsValid } = await editForm.value.validate();
    if (!formIsValid) {
        errorMessage.value = '입력된 정보를 확인해주세요.';
        return;
    }

    loadingSubmit.value = true;
    errorMessage.value = '';
    successMessage.value = '';

    try {
        const dataToUpdate = {
            fullName: FROM_DATA.value.fullName,
            initialActivation: FROM_DATA.value.initialActivation,
            usagePeriod: FROM_DATA.value.usagePeriod,
        };

        // 새 비밀번호가 입력되었다면 추가
        if (newPassword.value) {
            dataToUpdate.password = newPassword.value;
        }

        const response = await axios.patch(API_URL, dataToUpdate); // PATCH 요청

        console.log('수정 성공:', response.data);
        successMessage.value = '사용자 정보가 성공적으로 수정되었습니다!';

        // 성공 메시지 표시 후 다이얼로그 닫기 및 리다이렉션
        setTimeout(() => {
            showDialog.value = false; // 다이얼로그 닫기
            window.location.reload();
        }, 1500); // 1.5초 후 리다이렉션

    } catch (error) {
        console.error('수정 실패:', error);
        if (error.response) {
            errorMessage.value = error.response.data.message || '수정에 실패했습니다. 서버 오류.';
        } else if (error.request) {
            errorMessage.value = '네트워크 오류: 서버에 연결할 수 없습니다.';
        } else {
            errorMessage.value = '알 수 없는 오류가 발생했습니다.';
        }
    } finally {
        loadingSubmit.value = false;
    }
};

// 비밀번호 필드 변경 감지하여 유효성 재검사 (새 비밀번호/확인 비밀번호 입력 시)
watch([newPassword, confirmNewPassword], () => {
    if (editForm.value) {
        editForm.value.validate();
    }
}, { deep: true });
</script>