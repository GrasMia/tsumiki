import { http, authHttp, type DetailResponse } from './index';

export interface LoginParams {
    username: string
    password: string
}

export interface RegisterParams {
    username: string
    email: string
    password: string
}

export interface AuthResponse {
    user: UserProfile
    access_token: string
    token_type: string
}

export interface UserProfile {
    id: number
    username: string
    email: string
    is_superuser: boolean
    total_space: number
    used_space: number
    created_at: string
}

export interface UpdatePasswordParams {
    old_password: string
    new_password: string
}

export const userApi = {
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

    register: (data: RegisterParams) => {
        return authHttp<DetailResponse>('/auth/register', { method: 'POST', body: data });
    },

    logout: () => {
        return authHttp<DetailResponse>('/auth/logout', { method: 'POST' });
    },

    refresh: () => {
        return authHttp<AuthResponse>(`/auth/refresh`, { method: 'POST' });
    },

    getUserProfile: (user_id: string) => {
        return http<UserProfile>(`/users/${user_id}/info`, { method: 'GET' });
    },

    modifyUsername: (user_id: string, newName: string) => {
        return http<DetailResponse>(`/users/${user_id}/username?new_name=${newName}`, { method: 'PATCH' });
    },

    modifyEmail: (user_id: string, newEmail: string) => {
        return http<DetailResponse>(`/users/${user_id}/email?new_email=${newEmail}`, { method: 'PATCH' });
    },

    modifyPassword: (user_id: string, params: UpdatePasswordParams) => {
        return http<DetailResponse>(`/users/${user_id}/password`, { method: 'PATCH', body: params });
    },

    modifyAvatar: (user_id: string, avatar_data: File) => {
        const formData = new FormData();
        formData.append('upload_file', avatar_data);
        return http<DetailResponse>(`/users/${user_id}/avatar`, { method: 'PUT', body: formData });
    },

    async getAvatarBlob(user_id: string): Promise<Blob> {
        return http<Blob>(`/users/${user_id}/avatar`, { method: 'GET' });
    },

    inactive: (user_id: string, password: string) => {
        return http<DetailResponse>(`/users/${user_id}/inactive/password?password=${password}`, { method: 'PUT', });
    },
};