<template>
    <div class="profile-container">
        <n-card title="个人设置" :bordered="false" class="profile-card">
            <n-tabs type="line" animated>
                <!-- 基本信息 -->
                <n-tab-pane name="info" tab="基本信息">
                    <n-form :model="profileForm" :rules="profileRules" ref="profileFormRef" label-placement="left"
                        label-width="100">
                        <n-form-item label="用户名" path="new_username">
                            <n-input :placeholder="userStore.user.username" v-model:value="profileForm.new_username"
                                @keydown="preventSpace" @keyup.enter="updateProfile" />
                        </n-form-item>
                        <n-form-item label="邮箱" path="new_email">
                            <n-input :placeholder="userStore.user.email" v-model:value="profileForm.new_email"
                                @keydown="preventSpace" @keyup.enter="updateProfile" />
                        </n-form-item>
                        <n-form-item>
                            <n-button type="primary" @click="updateProfile" :loading="updateLoading">
                                保存修改
                            </n-button>
                        </n-form-item>
                    </n-form>
                </n-tab-pane>

                <!-- 修改密码 -->
                <n-tab-pane name="password" tab="修改密码">
                    <n-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-placement="left"
                        label-width="120">
                        <n-form-item label="当前密码" path="current_password">
                            <n-input v-model:value="passwordForm.current_password" type="password"
                                show-password-on="click" @keydown="preventSpace" />
                        </n-form-item>
                        <n-form-item label="新密码" path="new_password">
                            <n-input v-model:value="passwordForm.new_password" type="password" show-password-on="click"
                                @keydown="preventSpace" />
                        </n-form-item>
                        <n-form-item label="确认新密码" path="confirm_password">
                            <n-input v-model:value="passwordForm.confirm_password" type="password"
                                show-password-on="click" @keydown="preventSpace" @keyup.enter="updatePassword" e />
                        </n-form-item>
                        <n-form-item>
                            <n-button type="primary" @click="updatePassword" :loading="passwordLoading">
                                修改密码
                            </n-button>
                        </n-form-item>
                    </n-form>
                </n-tab-pane>

                <!-- 头像设置 -->
                <n-tab-pane name="avatar" tab="头像设置">
                    <div class="avatar-section">
                        <div class="avatar-preview">
                            <n-avatar :size="120" :src="userStore.avatarBlobUrl" object-fit="cover" />
                        </div>
                        <n-upload ref="uploadRef" :show-file-list="false" :multiple="false"
                            :custom-request="customUpload" accept="image/*">
                            <n-button type="tertiary">
                                <template #icon><n-icon><cloud-upload-outline /></n-icon></template>
                                上传头像
                            </n-button>
                        </n-upload>
                    </div>
                </n-tab-pane>
            </n-tabs>
        </n-card>
    </div>
</template>

<script setup lang="ts">
    import { ref, reactive, useTemplateRef } from 'vue';
    import { useRouter } from 'vue-router';
    import {
        NCard, NTabs, NIcon, NTabPane, NForm, NFormItem, NInput, NButton, NAvatar, NUpload, useMessage, type FormRules,
        type UploadCustomRequestOptions
    } from 'naive-ui';
    import { CloudUploadOutline, TrashOutline } from '@vicons/ionicons5';
    import { useUserStore, userApi } from '@/stores/user';
    import { preventSpace } from '@/utils/format';

    const router = useRouter();
    const message = useMessage();
    const userStore = useUserStore();

    const profileFormRef = useTemplateRef('profileFormRef');
    const passwordFormRef = useTemplateRef('passwordFormRef');
    const uploadRef = useTemplateRef('uploadRef');
    const updateLoading = ref(false);
    const passwordLoading = ref(false);

    const profileForm = reactive({
        new_username: '',
        new_email: ''
    });

    const profileRules: FormRules = {
        new_username: { min: 5, message: '用户名长度不能少于5位', trigger: 'blur' },
        new_email: [{ type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }]
    };

    const passwordForm = reactive({
        current_password: '',
        new_password: '',
        confirm_password: ''
    });

    const passwordRules: FormRules = {
        current_password: [
            { required: true, message: '请输入当前密码', trigger: 'blur' },
            { min: 8, message: '密码长度少于8位', trigger: 'blur' }
        ],
        new_password: [
            { required: true, message: '请输入新密码', trigger: 'blur' },
            { min: 8, message: '新密码长度不能少于8位', trigger: 'blur' },
            {
                validator: (_rule, value) => {
                    if (value && value === passwordForm.current_password)
                        return new Error('新密码不能与旧密码相同');
                    return true;
                },
                trigger: 'blur'
            },
        ],
        confirm_password: [
            { required: true, message: '请再次输入新密码', trigger: 'blur' },
            {
                validator: (_rule, value) => {
                    if (value && value !== passwordForm.new_password) {
                        return new Error('两次输入的密码不一致');
                    }
                    return true;
                },
                trigger: 'blur'
            }
        ]
    };

    // 更新个人信息
    const updateProfile = async () => {
        try { await profileFormRef.value?.validate(); }
        catch { return; }

        if (userStore.user.username == profileForm.new_username || !profileForm.new_username) { profileForm.new_username = ""; }
        if (userStore.user.email == profileForm.new_email || !profileForm.new_email) { profileForm.new_email = ""; }
        if (!profileForm.new_username && !profileForm.new_email) { return; }

        updateLoading.value = true;
        if (profileForm.new_username) {
            try {
                const res = await userApi.modifyUsername(userStore.user_id, profileForm.new_username);
                // 更新 userStore 
                userStore.user.username = profileForm.new_username;
                // 清空输入框
                profileForm.new_username = "";
                // 刷新URL
                router.push(`/${userStore.user.username}/profile`);
                message.success(res.detail);
            }
            catch (error: unknown) {
                message.error(error instanceof Error ? error.message : String(error));
            }
        }
        if (profileForm.new_email) {
            try {
                const res = await userApi.modifyEmail(userStore.user_id, profileForm.new_email);
                userStore.user.email = profileForm.new_email;
                profileForm.new_email = "";
                message.success(res.detail);
            }
            catch (error: unknown) {
                message.error(error instanceof Error ? error.message : String(error));
            }
        }
        updateLoading.value = false;
    };

    // 修改密码
    const updatePassword = async () => {
        try {
            await passwordFormRef.value?.validate();
        } catch {
            return;
        }

        passwordLoading.value = true;
        try {
            const res = await userApi.modifyPassword(userStore.user_id, {
                old_password: passwordForm.current_password,
                new_password: passwordForm.new_password
            });
            message.success(`${res.detail}，请重新登录`);
            await new Promise(resolve => setTimeout(resolve, 1000));
            await userStore.logout();
            router.push('/login');
        } catch (error: unknown) {
            message.error(error instanceof Error ? error.message : String(error));
        } finally {
            passwordLoading.value = false;
        }
    };

    // 头像上传
    const customUpload = async ({ file }: UploadCustomRequestOptions) => {
        uploadRef.value?.clear()

        const uploadFile = file.file;
        if (!uploadFile) throw new Error("无效的头像文件");

        try {
            const res = await userApi.modifyAvatar(userStore.user_id, uploadFile);
            await userStore.loadAvatar();
            message.success(res.detail);
        } catch (error: unknown) {
            message.error(error instanceof Error ? error.message : String(error));
        }
    };
</script>

<style scoped>
    .profile-container {
        min-height: 100vh;
        background: linear-gradient(135deg, MediumAquaMarine 0%, LightSteelBlue 100%);
        padding: 24px;
    }

    .profile-card {
        max-width: 800px;
        margin: 0 auto;
    }

    .avatar-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 20px;
        padding: 24px;
    }

    .avatar-preview {
        margin-bottom: 16px;
    }
</style>