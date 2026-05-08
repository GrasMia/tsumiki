import { ofetch, $fetch } from 'ofetch';
import { useUserStore } from "@/stores/user"

export const isTokenValid = (token: string) => {
    if (!token) return false;

    try {
        const parts = token.split('.');
        if (parts[1] === undefined) return false;  // 检查 JWT 格式
        const payload = JSON.parse(atob(parts[1]));
        return payload.exp - 5 > Date.now() / 1000;
    } catch {
        return false;
    }
};

// 创建 ofetch 实例
const http = ofetch.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '',
    timeout: 30000,
    // 请求拦截器：添加 Token
    async onRequest({ request, options, response }) {
        const userStore = useUserStore();
        // 没有 token → 返回登陆
        if (!userStore.user_id && !userStore.token) {
            userStore.logout();
            window.location.href = '/login';
            return;
        }
        // token 存在且未过期
        if (isTokenValid(userStore.token)) {
            options.headers.append("Authorization", userStore.token);
            return;
        }
        // token 存在但已过期
        if (userStore.refreshPromise) {
            await userStore.refreshPromise;
        } else {
            try {
                await userStore.refreshToken();
            }
            catch (e) {
                userStore.logout();
                window.location.href = '/login';
                throw e
            }
        }

        options.headers.append("Authorization", userStore.token);
    },
    // 响应拦截器：统一错误处理
    async onResponseError({ request, options, response }) {
        const data = response._data;

        // pydantic 验证错误
        if (Array.isArray(data?.detail)) {
            const firstError = data.detail[0];
            const message = firstError?.msg || '请求参数错误';
            throw new Error(message);
        }

        // 其他错误
        const message = data?.detail || '请求失败';
        throw new Error(message);
    }
});

const authHttp = ofetch.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '',
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },

    async onResponseError({ request, options, response }) {
        const data = response._data;
        const message = data?.detail || '请求失败';
        throw new Error(message);
    }
});

type DetailResponse = {
    detail: string
};

export { http, authHttp, type DetailResponse };