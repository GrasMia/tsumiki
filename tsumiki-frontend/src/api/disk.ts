import { http, type DetailResponse } from './index';

export interface DataItem {
    name: string
    size?: number
    sha256?: string
    created_at: Date
    modified_at: Date
}

export interface DirInfo {
    name: string
    created_at: Date
    modified_at: Date
}

export interface FileInfo {
    name: string
    size: number
    sha256: string
    created_at?: Date
    modified_at?: Date
    deleted_at?: Date
    expires_at?: Date
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

export const diskApi = {
    get_list: (user_id: string, path: string = '') => {
        const url = path
            ? `/disk/${user_id}/${path}`
            : `/disk/${user_id}/`;
        return http<Array<DataItem>>(url, { method: 'GET' });
    },

    createDir: (user_id: string, path: string = '', newDirName: string) => {
        let url = path ?
            `/disk/${user_id}/${path}?new_dir_name=${newDirName}` :
            `/disk/${user_id}/?new_dir_name=${newDirName}`;

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

    deleteDir: (user_id: string, path: string = '', hashSHA256: string = '') => {
        let url = path ? `/disk/${user_id}/${path}` : `/disk/${user_id}/`;
        url = hashSHA256 ? `${url}?dir_name=${hashSHA256}` : url;

        return http<DetailResponse>(url, { method: 'DELETE' });
    },

    deleteFile: (user_id: string, path: string = '', fileName: string) => {
        let url = path ? `/disk/${user_id}/${path}?file_name=${fileName}` : `/disk/${user_id}/?file_name=${fileName}`;

        return http<DetailResponse>(url, { method: 'DELETE' });
    },

    renameDir: (user_id: string, path: string = '', dirName: string, newName: string) => {
        let url = path ?
            `/disk/${user_id}/${path}?dir_name=${dirName}&new_name=${newName}` :
            `/disk/${user_id}/?dir_name=${dirName}&new_name=${newName}`;

        return http<DetailResponse>(url, { method: 'PUT' });
    },

    renameFile: (user_id: string, path: string = '', fileName: string, newName: string) => {
        let url = path ?
            `/disk/${user_id}/${path}?file_name=${fileName}&new_name=${newName}` :
            `/disk/${user_id}/?file_name=${fileName}&new_name=${newName}`;

        return http<DetailResponse>(url, { method: 'PUT' });
    }
};