import { defineStore } from 'pinia';
import { ref } from 'vue';
import { userApi, type UserInfo } from '@/api/user';
import { useListCacheStore } from '@/stores/listCache';

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
    const avatarBlobUrl = ref('');
    const fetchPromise = ref<Promise<UserInfo> | null>(null);
    const refreshPromise = ref<Promise<string> | null>(null);


    const register = async (username: string, email: string, password: string) => {
        return await userApi.register({ username, email, password });
    };

    const login = async (username: string, password: string) => {
        const res = await userApi.login({ username, password });
        user.value = res.user;
        localStorage.setItem('user_id', user_id.value = getUserIdFromToken(res.access_token));
        localStorage.setItem('access_token', access_token.value = res.access_token);
        loadAvatar();
    };

    const fetchUser = async () => {
        if (fetchPromise.value) { return fetchPromise.value }
        user.value = await (fetchPromise.value = userApi.getUserInfo(user_id.value));
        fetchPromise.value = null;
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

    const refreshToken = async () => {
        if (refreshPromise.value) return refreshPromise.value;
        access_token.value = await (refreshPromise.value = userApi.refresh(access_token.value));
        localStorage.setItem('access_token', access_token.value);
        refreshPromise.value = null;
    };

    const logout = async (mode: 'logout' | 'clear' = 'logout') => {
        try {
            let res: Awaited<ReturnType<typeof userApi.logout>> | undefined = undefined;
            if (mode === 'logout') {
                res = await userApi.logout(access_token.value);
            }
            user_id.value = access_token.value = '';
            user.value = {} as UserInfo;
            revokeAvatarUrl();
            localStorage.removeItem('user_id');
            localStorage.removeItem('access_token');
            useListCacheStore().clearCache();
            return res;
        } catch (error: unknown) {
            throw error;
        }
    };

    return {
        user_id,
        access_token,
        user,
        avatarBlobUrl,
        fetchPromise,
        refreshPromise,
        register,
        login,
        fetchUser,
        loadAvatar,
        refreshToken,
        logout
    };
});

export { userApi, isTokenValid, useUserStore };