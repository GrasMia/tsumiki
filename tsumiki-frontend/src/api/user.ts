import { http, authHttp } from './index';

interface BaseParams {
    username: string
    password: string
}

export interface LoginParams extends BaseParams {
}

export interface RegisterParams extends BaseParams {
    email: string
}

export interface AuthResponse {
    user: UserProfile
    access_token: string
}

export interface UserProfile {
    id: number
    username: string
    email: string
    total_space: number
    used_space: number
    created_at: string
}

export interface UpdatePasswordParams {
    old_password: string
    new_password: string
}

type DetailResponse = {
    detail: string
}

export const userApi = {
    register: (data: RegisterParams) => {
        return authHttp<DetailResponse>('/auth/register', { method: 'POST', body: data });
    },

    login: (data: LoginParams) => {
        const formData = new URLSearchParams();
        formData.append('username', data.username);
        formData.append('password', data.password);

        return authHttp<AuthResponse>('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
    },

    logout: () => {
        return authHttp<DetailResponse>('/auth/logout', { method: 'POST' });
    },

    refresh: () => {
        return authHttp<string>(`/auth/refresh`, { method: 'POST' });
    },

    getUserProfile: (user_id: string) => {
        return http<UserProfile>(`/users/${user_id}/info`, { method: 'GET' });
    },

    modifyUsername: (user_id: string, new_name: string) => {
        return http<DetailResponse>(`/users/${user_id}/username?new_name=${encodeURIComponent(new_name)}`, { method: 'PATCH' });
    },

    modifyEmail: (user_id: string, new_email: string) => {
        return http<DetailResponse>(`/users/${user_id}/email?new_email=${encodeURIComponent(new_email)}`, { method: 'PATCH' });
    },

    modifyPassword: (user_id: string, params: UpdatePasswordParams) => {
        return http<DetailResponse>(`/users/${user_id}/password`, { method: 'PATCH', body: params });
    },

    modifyAvatar: (user_id: string, avatar_data: File) => {
        const formData = new FormData();
        formData.append('upload_file', avatar_data);
        return http<DetailResponse>(`/users/${user_id}/avatar`, { method: 'PUT', body: formData });
    },

    getAvatarBlob(user_id: string) {
        return http<Blob>(`/users/${user_id}/avatar`, { method: 'GET' });
    },

    resetAvatar(user_id: string) {
        return http<DetailResponse>(`/users/${user_id}/avatar`, { method: 'DELETE' });
    },

    inactive: (user_id: string, password: string) => {
        return http<DetailResponse>(`/users/${user_id}/inactive/password?password=${encodeURIComponent(password)}`, { method: 'PUT' });
    },
};