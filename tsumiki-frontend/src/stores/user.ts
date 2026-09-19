import { defineStore } from 'pinia';
import { ref } from 'vue';
import { userApi, type UserInfo } from '@/api/user';

const isTokenValid = (token: string) => {
    if (!token) return false;

    try {
        const parts = token.split('.');
        if (parts[1] === undefined) return false;  // 检查 JWT 格式
        const payload = JSON.parse(atob(parts[1]));
        return payload.exp > Math.ceil(Date.now() / 1000);
    } catch {
        return false;
    }
};

const getUserIdFromToken = (token: string): string => {
    if (!token) return '';

    try {
        const parts = token.split('.');
        if (parts[1] === undefined) return '';
        const payload = JSON.parse(atob(parts[1]));
        return payload.sub || '';
    } catch {
        return '';
    }
};

const useUserStore = defineStore('user', () => {
    const user_id = ref(localStorage.getItem('user_id') || '');
    const access_token = ref(localStorage.getItem('access_token') || '');
    const user = ref<UserInfo>({} as UserInfo);
    const refreshPromise = ref<Promise<string> | null>(null);
    const avatarBlobUrl = ref('');

    const register = async (username: string, email: string, password: string) => {
        return await userApi.register({ username, email, password });
    };

    const login = async (username: string, password: string) => {
        const res = await userApi.login({ username, password });
        user.value = res.user;
        localStorage.setItem('user_id', user_id.value = getUserIdFromToken(res.access_token));
        localStorage.setItem('access_token', access_token.value = res.access_token);
    };

    const fetchUser = async () => {
        user.value = await userApi.getUserInfo(user_id.value);
        if (!avatarBlobUrl.value) { await loadAvatar(); }
    };

    const loadAvatar = async () => {
        try {
            const blob = await userApi.getAvatarBlob(user_id.value);
            // 释放旧的 Blob URL
            revokeAvatarUrl();
            // 创建新的 Blob URL
            avatarBlobUrl.value = URL.createObjectURL(blob);
        } catch (error: unknown) {
            console.error(error instanceof Error ? error.message : String(error));
        }
    };

    const revokeAvatarUrl = () => {
        if (avatarBlobUrl.value) { URL.revokeObjectURL(avatarBlobUrl.value); }
        avatarBlobUrl.value = '';
    };

    const refreshToken = () => {
        if (refreshPromise.value) return refreshPromise.value;
        return refreshPromise.value = userApi.refresh();
    };

    const logout = async () => {
        user.value = {} as UserInfo;
        localStorage.removeItem('user_id');
        localStorage.removeItem('access_token');

        revokeAvatarUrl();

        return await userApi.logout();
    };

    return {
        user_id,
        access_token,
        user,
        refreshPromise,
        avatarBlobUrl,
        register,
        login,
        fetchUser,
        loadAvatar,
        refreshToken,
        logout
    };
});

export { userApi, isTokenValid, useUserStore };