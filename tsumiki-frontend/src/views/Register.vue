<template>
    <div class="register-container">
        <n-card class="register-card" :bordered="false">
            <n-h1 style="text-align: center; margin-bottom: 24px;">注册账号</n-h1>

            <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
                <n-form-item label="用户名" path="username">
                    <n-input v-model:value="formData.username" placeholder="请输入用户名" size="large"
                        @keydown="preventSpace" />
                </n-form-item>

                <n-form-item label="邮箱" path="email">
                    <n-input v-model:value="formData.email" placeholder="请输入邮箱" size="large" @keydown="preventSpace" />
                </n-form-item>

                <n-form-item label="密码" path="password">
                    <n-input v-model:value="formData.password" type="password" placeholder="请输入密码（至少8位）" size="large"
                        show-password-on="click" @keydown="preventSpace" />
                </n-form-item>

                <n-form-item label="确认密码" path="confirmPassword">
                    <n-input v-model:value="formData.confirmPassword" type="password" placeholder="请再次输入密码" size="large"
                        show-password-on="click" @keydown="preventSpace" @keyup.enter="handleRegister" />
                </n-form-item>

                <n-form-item>
                    <n-button type="primary" size="large" block :loading="loading" @click="handleRegister">
                        注册
                    </n-button>
                </n-form-item>

                <div style="text-align: center">
                    <n-text depth="3">已有账号？</n-text>
                    <n-button text type="primary" @click="goToLogin">
                        立即登录
                    </n-button>
                </div>
            </n-form>
        </n-card>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive, useTemplateRef } from 'vue';
    import { useRouter } from 'vue-router';
    import { useMessage, NButton, NCard, NForm, NFormItem, NInput, NH1, NText, type FormRules } from 'naive-ui';
    import { useUserStore } from '@/stores/user';
    import { live2dAlertPrompt } from '@/stores/live2d';
    import { preventSpace } from '@/utils/format';

    const router = useRouter();
    const message = useMessage();
    const userStore = useUserStore();

    const formRef = useTemplateRef('formRef');
    const loading = ref(false);

    const formData = reactive({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });

    const validateConfirmPassword = (_rule: any, value: string) => {
        if (!value) {
            return new Error('请再次输入密码');
        }
        if (value !== formData.password) {
            return new Error('两次输入的密码不一致');
        }
        return true;
    };

    const rules: FormRules = {
        username: [
            { required: true, message: '请输入用户名', trigger: 'blur' },
            { min: 5, max: 20, message: '用户名长度应为5-20位', trigger: 'blur' },
        ],
        email: [
            { required: true, message: '请输入邮箱', trigger: 'blur' },
            { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
        ],
        password: [
            { required: true, message: '请输入密码', trigger: 'blur' },
            { min: 8, message: '密码长度不能少于8位', trigger: 'blur' },
        ],
        confirmPassword: [
            { validator: validateConfirmPassword, trigger: 'blur' },
        ],
    };

    const handleRegister = async () => {
        try {
            await formRef.value?.validate();
        } catch {
            return;
        }

        loading.value = true;
        try {
            const res = await userStore.register(formData.username, formData.email, formData.password);
            message.success(res.detail);
            router.push('/login');
        } catch (error: any) {
            message.error(error instanceof Error ? error.message : String(error));
        } finally {
            loading.value = false;
        }
    };

    const goToLogin = () => {
        router.push('/login');
        live2dAlertPrompt('ログイン画面');
    };
</script>

<style scoped>
    .register-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background: linear-gradient(135deg, MediumAquaMarine 0%, LightSteelBlue 100%);
    }

    .register-card {
        width: 100%;
        max-width: 460px;
        padding: 32px;
        border-radius: 16px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
</style>