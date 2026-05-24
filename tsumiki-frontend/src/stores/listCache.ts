import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DataItem } from '@/api/disk'

type ItemCache = {
    path: string,
    list: DataItem[] | null
}

export const useListCacheStore = defineStore('listCache', () => {
    const itemsCache = ref<ItemCache[]>([]);

    function matchCache(toPath: string, fromPath: string, dataList: DataItem[]): DataItem[] | null {
        // 目标路径是上次路径的子目录（进入子目录）
        const parentOfToPath = toPath.replace(/[^/]+\/$/, '')
        if (parentOfToPath === fromPath) {
            itemsCache.value?.push({ path: fromPath, list: dataList })
            return null
        }
        // 判断是否命中缓存
        while (itemsCache.value.length) {
            const itemCache = itemsCache.value.pop(); // 分步取出缓存
            if (itemCache?.path === toPath) {
                return itemCache.list; // 命中即返回缓存
            }
        }
        // 其他情况
        return null;
    }

    // 清除对应目录的缓存
    function removeCache(username: string, currentPath: string) {
        for (const itemCache of itemsCache.value) {
            if (itemCache.path === `/${username}/${currentPath}`) {
                itemCache.list = null;
                return;
            }
        }
    }

    function clearCache() { itemsCache.value = []; }

    return { itemsCache, matchCache, removeCache, clearCache }
})