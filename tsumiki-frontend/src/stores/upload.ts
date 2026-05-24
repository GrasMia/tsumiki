import { defineStore } from 'pinia';
import { ref, toRaw } from 'vue';
import { useListCacheStore } from './listCache';

interface UploadItem {
    name: string;
    progress: number;
}

export const useUploadStore = defineStore('upload', () => {
    const uploadQueue = ref<UploadItem[]>([]);

    const addUpload = (item: UploadItem) => {
        uploadQueue.value.push(item);
    };

    const updateProgress = (item: UploadItem, progress: number) => {
        const currentItem = uploadQueue.value.find(i => toRaw(i) === item);
        if (currentItem) {
            currentItem.progress = progress;
        }
    };

    const removeUpload = (item: UploadItem, username: string, currentPath: string) => {
        uploadQueue.value = uploadQueue.value.filter(i => toRaw(i) !== item);

        // 清除上传了文件的目录的缓存
        useListCacheStore().removeCache(username, currentPath);
    };

    return { uploadQueue, addUpload, updateProgress, removeUpload };
});