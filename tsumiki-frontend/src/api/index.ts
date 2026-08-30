import { ofetch, $fetch } from 'ofetch';
import { isTokenValid, useUserStore } from "@/stores/user"

// 创建 ofetch 实例
const http = ofetch.create({
    baseURL: '',
    timeout: 30000,
    // 请求拦截器：添加 Token
    async onRequest({ request, options, response }) {
        const userStore = useUserStore();

        // access_token 不存在或已过期
        if (!isTokenValid(userStore.access_token)) {
            try {
                const access_token = await userStore.refreshToken();
                if (userStore.refreshPromise != null) {
                    localStorage.setItem('access_token', userStore.access_token = access_token);
                    userStore.refreshPromise = null
                }
            }
            catch (e: unknown) {
                userStore.logout();
                window.location.href = '/login';
                throw e
            }
        }

        options.headers.append("Authorization", userStore.access_token);
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
    baseURL: '',
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },

    async onRequest({ request, options, response }) {
        const userStore = useUserStore();
        if (userStore.access_token) {
            options.headers.append("Authorization", userStore.access_token);
        }
    },

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