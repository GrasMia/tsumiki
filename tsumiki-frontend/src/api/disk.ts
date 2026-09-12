import { http } from './index';

interface BaseItem {
    name: string
    created_at: Date
    modified_at: Date
}

export interface DataItem extends BaseItem {
    size?: number
    sha256?: string
}

export interface FileItem extends BaseItem {
    size: number
    sha256: string
}

export interface FileMetadata {
    name: string
    size: number
    sha256: string
}

export enum Status {
    UPLOADING = "uploading",
    FINISHED = "finished",
    FAILED = "failed"
}

export interface ChunkInfo {
    id: string
    chunk_index: number
    total_chunks: number
    status: Status
}

export interface ChunkMetadata {
    id: string
    chunk_index: number
    md5: string
    upload_file: Blob
}

type DetailResponse = {
    detail: string
}

export const diskApi = {
    getDirItems: (user_id: string, path: string = '') => {
        const url = path
            ? `/disk/${user_id}/${path}`
            : `/disk/${user_id}/`;
        return http<Array<DataItem>>(url, { method: 'GET' });
    },

    createDir: (user_id: string, path: string = '', new_dir_name: string) => {
        let url = path ?
            `/disk/${user_id}/${path}?new_dir_name=${encodeURIComponent(new_dir_name)}` :
            `/disk/${user_id}/?new_dir_name=${encodeURIComponent(new_dir_name)}`;

        return http<DetailResponse>(url, { method: 'POST' });
    },

    createFile: (user_id: string, path: string = '', fileMetadata: FileMetadata) => {
        const url = path ? `/disk/${user_id}/${path}` : `/disk/${user_id}/`;
        return http<DetailResponse | ChunkInfo>(url, { method: 'POST', body: fileMetadata });
    },
    isDetailResponse(response: DetailResponse | ChunkInfo): response is DetailResponse {
        return 'detail' in response;
    },

    chunk_upload: (user_id: string, chunkMetadata: ChunkMetadata) => {
        const formData = new FormData();
        formData.append('id', chunkMetadata.id);
        formData.append('chunk_index', chunkMetadata.chunk_index.toString());
        formData.append('md5', chunkMetadata.md5);
        formData.append('upload_file', chunkMetadata.upload_file);
        return http<ChunkInfo>(`/disk/${user_id}/`, { method: 'PATCH', body: formData });
    },

    downloadFile: (user_id: string, path: string = '', fileName: string, token: string) => {
        const url = `/disk/${user_id}/${path}${fileName}?token=${token}`;
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        a.click();
    },

    renameDir: (user_id: string, path: string = '', dir_name: string, new_name: string) => {
        let url = path ?
            `/disk/${user_id}/${path}?dir_name=${encodeURIComponent(dir_name)}&new_name=${encodeURIComponent(new_name)}` :
            `/disk/${user_id}/?dir_name=${encodeURIComponent(dir_name)}&new_name=${encodeURIComponent(new_name)}`;

        return http<DetailResponse>(url, { method: 'PUT' });
    },

    renameFile: (user_id: string, path: string = '', file_name: string, new_name: string) => {
        let url = path ?
            `/disk/${user_id}/${path}?file_name=${encodeURIComponent(file_name)}&new_name=${encodeURIComponent(new_name)}` :
            `/disk/${user_id}/?file_name=${encodeURIComponent(file_name)}&new_name=${encodeURIComponent(new_name)}`;

        return http<DetailResponse>(url, { method: 'PUT' });
    },

    moveDir: (target_path: string, original_path: string, dir_name: string) => {
        target_path = encodeURIComponent(target_path);
        original_path = encodeURIComponent(original_path);
        dir_name = encodeURIComponent(dir_name);
        let url = `/disk/?target_path=${target_path}&original_path=${original_path}&dir_name=${dir_name}`;

        return http<DetailResponse>(url, { method: 'PUT' });
    },

    moveFile: (target_path: string, original_path: string, file_name: string) => {
        target_path = encodeURIComponent(target_path);
        original_path = encodeURIComponent(original_path);
        file_name = encodeURIComponent(file_name);
        let url = `/disk/?target_path=${target_path}&original_path=${original_path}&file_name=${file_name}`;

        return http<DetailResponse>(url, { method: 'PUT' });
    },

    deleteDir: (user_id: string, path: string = '', dir_name: string = '') => {
        let url = path ? `/disk/${user_id}/${path}` : `/disk/${user_id}/`;
        url = dir_name ? `${url}?dir_name=${encodeURIComponent(dir_name)}` : url;

        return http<DetailResponse>(url, { method: 'DELETE' });
    },

    deleteFile: (user_id: string, path: string = '', file_name: string) => {
        let url = path ? `/disk/${user_id}/${path}?file_name=${encodeURIComponent(file_name)}`
            : `/disk/${user_id}/?file_name=${encodeURIComponent(file_name)}`;

        return http<DetailResponse>(url, { method: 'DELETE' });
    },
};