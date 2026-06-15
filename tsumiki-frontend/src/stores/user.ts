import { defineStore } from 'pinia';
import { ref } from 'vue';
import { userApi, type UserProfile } from '@/api/user';

const useUserStore = defineStore('user', () => {
    const user_id = ref(localStorage.getItem('user_id') || '');
    const token = ref(localStorage.getItem('access_token') || '');
    const user = ref<UserProfile>({} as UserProfile);
    const refreshPromise = ref<Promise<void> | null>(null);
    const avatarBlobUrl = ref('');

    const login = async (username: string, password: string) => {
        const res = await userApi.login({ username, password });
        user.value = res.user;
        localStorage.setItem('user_id', user_id.value = String(res.user.id));
        localStorage.setItem('access_token', token.value = `${res.token_type} ${res.access_token}`);

        await loadAvatar();
    };

    const register = async (username: string, email: string, password: string) => {
        return await userApi.register({ username, email, password });
    };

    const logout = async () => {
        user_id.value = '';
        token.value = '';
        user.value = {} as UserProfile;
        localStorage.removeItem('user_id');
        localStorage.removeItem('access_token');

        revokeAvatarUrl();

        return await userApi.logout();
    };

    const refreshToken = async () => {
        if (refreshPromise.value) return refreshPromise.value;

        refreshPromise.value = (async () => {
            const res = await userApi.refresh();
            user.value = res.user;
            localStorage.setItem('user_id', user_id.value = String(res.user.id));
            localStorage.setItem('access_token', token.value = `${res.token_type} ${res.access_token}`);
        })();

        try {
            return await refreshPromise.value;
        } finally {
            refreshPromise.value = null;
        }
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
        if (avatarBlobUrl.value && avatarBlobUrl.value.startsWith('blob:')) {
            URL.revokeObjectURL(avatarBlobUrl.value);
        }
        avatarBlobUrl.value = '';
    };

    const fetchUser = async () => {
        user.value = await userApi.getUserProfile(user_id.value)
    };

    return {
        user_id,
        token,
        user,
        refreshPromise,
        avatarBlobUrl,
        register,
        login,
        logout,
        refreshToken,
        loadAvatar,
        fetchUser
    };
});

export { useUserStore, userApi };