<template>
    <div class="login-container">
        <n-card class="login-card" :bordered="false">
            <n-h1 style="text-align: center; margin-bottom: 24px;">登录</n-h1>

            <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
                <n-form-item label="用户名 / 邮箱" path="username">
                    <n-input id="username" v-model:value="formData.username" placeholder="请输入用户名或邮箱" size="large"
                        @keydown="preventSpace" />
                </n-form-item>

                <n-form-item label="密码" path="password">
                    <n-input v-model:value="formData.password" type="password" placeholder="请输入密码" size="large"
                        show-password-on="click" @keyup.enter="handleLogin" @keydown="preventSpace" />
                </n-form-item>

                <n-form-item>
                    <n-button type="primary" size="large" block :loading="loading" @click="handleLogin">
                        登录
                    </n-button>
                </n-form-item>

                <div style="text-align: center">
                    <n-text depth="3">还没有账号？</n-text>
                    <n-button text type="primary" @click="goToRegister">
                        立即注册
                    </n-button>
                </div>
            </n-form>
        </n-card>
    </div>
</template>

<script setup lang="ts">
    import { ref, useTemplateRef } from 'vue';
    import { useRouter } from 'vue-router';
    import { useMessage, NButton, NCard, NForm, NFormItem, NInput, NH1, NText, type FormRules, type FormInst } from 'naive-ui';
    import { useUserStore } from '@/stores/user';
    import { live2dAlert,live2dAlertPrompt, live2dAlertRhetorical } from '@/stores/live2d';
    import { preventSpace } from '@/utils/format';

    const router = useRouter();
    const userStore = useUserStore();
    const message = useMessage();

    const formRef = useTemplateRef('formRef')
    const formData = ref({ username: '', password: '' });
    const loading = ref(false);

    const rules: FormRules = {
        username: [
            { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
            { min: 5, message: '用户名长度不少于5位', trigger: 'blur' }
        ],
        password: [
            { required: true, message: '请输入密码', trigger: 'blur' },
            { min: 8, message: '密码长度不少于8位', trigger: 'blur' }
        ]
    };

    const handleLogin = async () => {
        if (!formData.value.username)
            live2dAlertRhetorical('ユーザーネーム');
        else if (formData.value.username && !formData.value.password)
            live2dAlertRhetorical('パスワード');
        try {
            await formRef.value?.validate();
        } catch {
            return;
        }

        loading.value = true;
        try {
            await userStore.login(formData.value.username, formData.value.password);
            live2dAlert('ログイン成功しました');
            message.success('登录成功');
            router.push(`/${formData.value.username}/`);
        } catch (error: any) {
            live2dAlert('ログイン失敗しました')
            message.error(error instanceof Error ? error.message : String(error));
        }
        finally {
            loading.value = false;
        }
    };

    const goToRegister = () => {
        router.push('/register');
        live2dAlertPrompt('新規登録画面');
    };
</script>

<style scoped>
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background: linear-gradient(135deg, MediumAquaMarine 0%, LightSteelBlue 100%);
    }

    .login-card {
        width: 100%;
        max-width: 420px;
        padding: 32px;
        border-radius: 16px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
</style>