import { defineStore } from 'pinia';
import { ref, toRaw } from 'vue';
import { type UploadFileInfo } from 'naive-ui';

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

    const removeUpload = (item: UploadItem) => {
        uploadQueue.value = uploadQueue.value.filter(i => toRaw(i) !== item);
    };

    return { uploadQueue, addUpload, updateProgress, removeUpload };
});