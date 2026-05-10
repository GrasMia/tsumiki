<template>
    <n-layout class="home-container">
        <!-- 头部导航 -->
        <n-layout-header bordered class="header">
            <div class="header-left">
                <n-h2 style="margin: 0;">Tsumiki</n-h2>
            </div>
            <div class="header-right">
                <n-space align='center'>
                    <n-text>{{ userStore.user.username }}</n-text>
                    <n-avatar :size="32" :src="userStore.avatarBlobUrl" object-fit="cover" />
                    <n-dropdown :options="userMenuOptions" @select="handleUserMenuSelect">
                        <n-button text>
                            <n-icon size="20"><chevron-down-outline /></n-icon>
                        </n-button>
                    </n-dropdown>
                </n-space>
            </div>
        </n-layout-header>

        <!-- 面包屑 -->
        <div class="breadcrumb-bar">
            <n-breadcrumb>
                <n-breadcrumb-item @click="navigateTo('')">根目录</n-breadcrumb-item>
                <n-breadcrumb-item v-for="(part, idx) in breadcrumbItems" :key="idx"
                    @click="navigateTo(breadcrumbItems.slice(0, idx + 1).join('/'))">
                    {{ part }}
                </n-breadcrumb-item>
            </n-breadcrumb>
        </div>

        <n-layout-content class="content">
            <!-- 统计卡片 -->
            <div class="stats-cards">
                <n-card size="small" class="stat-card">
                    <n-statistic label="已用空间" :value="formatStorage(userStore.user.used_space)" />
                </n-card>
                <n-card size="small" class="stat-card">
                    <n-statistic label="总空间" :value="formatStorage(userStore.user.total_space)" />
                </n-card>
                <n-card size="small" class="stat-card">
                    <n-statistic label="当前目录文件数量" :value="fileCount" />
                </n-card>
            </div>

            <!-- 操作栏 -->
            <div class="toolbar">
                <div class="toolbar-actions">
                    <n-button @click="showCreateDirDialog = true">
                        <template #icon><n-icon><add-outline /></n-icon></template>
                        新建目录
                    </n-button>
                    <n-upload ref="uploadRef" :show-file-list="false" :multiple="true" :custom-request="customUpload"
                        accept="*/*">
                        <n-button type="primary">
                            <template #icon><n-icon><cloud-upload-outline /></n-icon></template>
                            上传文件
                        </n-button>
                    </n-upload>
                    <n-button @click="throttledRefreshFileList" type="tertiary">
                        <template #icon><n-icon><refresh-outline /></n-icon></template>
                        刷新
                    </n-button>
                </div>
                <n-input v-model:value="searchKeyword" placeholder="搜索文件" clearable class="toolbar-search"
                    @mouseenter="live2dAlert('ファイルを検索したいんですか', 0.1)" @keydown="preventSpace">
                    <template #prefix><n-icon><search-outline /></n-icon></template>
                </n-input>
            </div>

            <!-- 上传进度 -->
            <div v-if="uploadStore.uploadQueue.length > 0" class="progress-container">
                <div v-for="item in uploadStore.uploadQueue" :key="item.name" class="progress-item">
                    <span>{{ item.name }}</span>
                    <n-progress type="line" :percentage="item.progress" :processing="item.progress !== 100"
                        :status="item.progress === 100 ? 'success' : 'default'" style="width: 200px" />
                </div>
            </div>

            <!-- 文件列表 -->
            <div class="table-container">
                <file-table :data="filteredFileList" :loading="loading" :row-key="(row: DataItem) => row.name"
                    :bordered="true" :striped="true" @rename="handleRename" @enter-dir="enterDir"
                    @download-file="throttledHandleDownload" @delete="handleDelete" @row-dblclick="handleRowDblclick" />
            </div>

            <!-- 新建目录对话框 -->
            <n-modal v-model:show="showCreateDirDialog" preset="dialog" title="新建目录" :style="{ width: '400px' }"
                draggable>
                <n-form>
                    <n-form-item label="目录名称" required>
                        <n-input v-model:value="newDirName" placeholder="请输入目录名称" @keyup.enter="createDir"
                            @keydown="preventSpace" />
                    </n-form-item>
                </n-form>
                <template #action>
                    <n-space>
                        <n-button @click="showCreateDirDialog = false">取消</n-button>
                        <n-button type="primary" @click="createDir" :loading="createDirLoading">确定</n-button>
                    </n-space>
                </template>
            </n-modal>

            <!-- 文件详情对话框 -->
            <n-modal v-model:show="showFileDetail" preset="dialog" title="文件详情" :style="{ width: '540px' }" draggable>
                <div class="file-detail">
                    <div class="detail-row"><span class="detail-label">文件名：</span><span class="detail-value">{{
                        selectedFile?.name
                            }}</span></div>
                    <div class="detail-row"><span class="detail-label">大小：</span><span class="detail-value">{{
                        formatStorage(selectedFile?.size || 0) }}</span></div>
                    <div class="detail-row"><span class="detail-label">SHA256：</span><span
                            class="detail-value sha256">{{
                                selectedFile?.sha256 || '-' }}</span></div>
                    <div class="detail-row"><span class="detail-label">创建时间：</span><span class="detail-value">{{ new
                        Date(selectedFile?.created_at || '').toLocaleString() }}</span></div>
                    <div class="detail-row"><span class="detail-label">修改时间：</span><span class="detail-value">{{ new
                        Date(selectedFile?.modified_at || '').toLocaleString() }}</span></div>
                    <div class="detail-row"><span class="detail-label">状态：</span><n-tag
                            :type="selectedFile?.deleted_at ? 'error' : 'success'" size="small">{{
                                selectedFile?.deleted_at ? '已删除'
                                    : '正常' }}</n-tag></div>
                </div>
                <template #action>
                    <n-space>
                        <n-button @click="showFileDetail = false">关闭</n-button>
                        <n-button type="primary" @click="downloadSelectedFile">下载文件</n-button>
                    </n-space>
                </template>
            </n-modal>
        </n-layout-content>
    </n-layout>
</template>

<script setup lang="ts">
    import { ref, useTemplateRef, computed, watch, onMounted } from 'vue';
    import { useRoute, useRouter } from 'vue-router';
    import { useUserStore } from '@/stores/user';
    import { useUploadStore } from '@/stores/upload';
    import { type ChunkMetadata, type DataItem, type FileInfo, Status, diskApi } from '@/api/disk';
    import { useMessage, useDialog, NButton, NSpace, NInput, NIcon, NLayout, NLayoutHeader, NLayoutContent } from 'naive-ui'
    import { NCard, NStatistic, NH2, NText, NAvatar, NDropdown, NBreadcrumb, NBreadcrumbItem, } from 'naive-ui'
    import { NModal, NTag, NUpload, NProgress, NForm, NFormItem, type UploadCustomRequestOptions } from 'naive-ui';
    import { CloudUploadOutline, RefreshOutline, SearchOutline, ChevronDownOutline, AddOutline } from '@vicons/ionicons5';
    import { live2dAlert } from '@/stores/live2d';
    import FileTable from '@/components/FileTable.vue';
    import { calculateChunkMD5, calculateSHA256, type Chunk } from '@/utils/crypto';
    import { formatStorage, preventSpace } from '@/utils/format';
    import { debounce, throttle } from '@/utils/frequency';

    const route = useRoute();
    const router = useRouter();
    const userStore = useUserStore();
    const uploadStore = useUploadStore();
    const message = useMessage();
    const dialog = useDialog();

    // 状态
    const loading = ref(false);
    const dataList = ref<DataItem[]>([]);
    const uploadRef = useTemplateRef('uploadRef');

    // 新建目录
    const showCreateDirDialog = ref(false);
    const newDirName = ref('');
    const createDirLoading = ref(false);

    // 文件详情
    const showFileDetail = ref(false);
    const selectedFile = ref<FileInfo | null>(null);
    const selectedFileRow = ref<DataItem | null>(null);

    // 计算属性
    const currentPath = computed(() => {
        const pathMatch = route.params.pathMatch;
        if (!pathMatch)
            return '';
        return Array.isArray(pathMatch) ? pathMatch.join('/') + '/' : pathMatch;
    });

    const breadcrumbItems = computed(() => {
        if (!currentPath.value)
            return [];
        return currentPath.value.split('/').filter(p => p);
    });

    const fileCount = computed(() => {
        return dataList.value.filter(item => item.size !== undefined).length;
    });

    // 文件列表过滤 + 搜索防抖
    const searchKeyword = ref('');
    const debouncedSearchKeyword = ref('');
    const updateSearchKeyword = debounce((value: string) => { debouncedSearchKeyword.value = value; }, 500);
    watch(searchKeyword, (newKeyword) => { updateSearchKeyword(newKeyword); });
    const filteredFileList = computed(() => {
        const keyword = debouncedSearchKeyword.value.toLowerCase();
        if (!keyword) return dataList.value;
        return dataList.value.filter(item => item.name.toLowerCase().includes(keyword));
    });

    const userMenuOptions = [
        { label: '个人设置', key: 'profile' }, { label: '退出登录', key: 'logout' }
    ];

    const loadDirectory = async (path: string) => {
        try {
            dataList.value = await diskApi.get_list(userStore.user_id, path);
        } catch (e: any) {
            dataList.value = [];
            message.error(e instanceof Error ? e.message : String(e));
        }
    };

    const refreshFileList = async () => {
        await loadDirectory(currentPath.value);
        message.success('刷新成功');
    };
    const throttledRefreshFileList = throttle(refreshFileList, 1500);

    const navigateTo = (path: string) => {
        if (path) router.push(`/${userStore.user.username}/${path}`);
        else router.push(`/${userStore.user.username}/`);
    };

    const enterDir = (dirName: string) => {
        const newPath = currentPath.value ? `${currentPath.value}${dirName}` : dirName;
        router.push(`/${userStore.user.username}/${newPath}`);
    };

    // 新建目录
    const createDir = async () => {
        if (!newDirName.value.trim()) {
            message.warning('请输入目录名称');
            return;
        }

        createDirLoading.value = true;
        try {
            const res = await diskApi.createDir(userStore.user_id, currentPath.value, newDirName.value.trim());
            message.success(res.detail);
            showCreateDirDialog.value = false;
            newDirName.value = '';
            await loadDirectory(currentPath.value);
        } catch (error: any) {
            message.error(error instanceof Error ? error.message : String(error));
        } finally {
            createDirLoading.value = false;
        }
    };

    const chunkSize = parseInt(import.meta.env.VITE_UPLOAD_FILE_CHUNK_SIZE) * 1024 * 1024;
    // 文件上传
    const customUpload = async ({ file }: UploadCustomRequestOptions) => {
        // 清除文件列表
        uploadRef.value?.clear()

        const uploadFile = file.file;
        if (!uploadFile) throw new Error("无效的文件");

        // 初始化上传会话
        try {
            var originalPath = currentPath.value
            var currentFileSHA256 = await calculateSHA256(uploadFile)
            var initRes = await diskApi.createFile(userStore.user_id, originalPath, {
                name: uploadFile.name,
                size: uploadFile.size,
                sha256: currentFileSHA256
            });
        }
        // 异常捕获
        catch (error: any) {
            message.error(error instanceof Error ? error.message : String(error));
            return;
        }

        // 秒传
        if (diskApi.isDetailResponse(initRes)) {
            const item = { name: uploadFile.name, progress: 33 }
            uploadStore.addUpload(item);
            await new Promise(resolve => setTimeout(resolve, 1000));
            uploadStore.updateProgress(item, 66);
            await new Promise(resolve => setTimeout(resolve, 1000));
            uploadStore.updateProgress(item, 100);

            await userStore.fetchUser();
            if (currentPath.value === originalPath) {
                await loadDirectory(currentPath.value);
            }
            message.success(initRes.detail);
            uploadStore.removeUpload(item);
        }

        // 新上传 / 断点续传
        else {
            const chunks = await calculateChunkMD5(uploadFile, chunkSize, initRes.chunk_index);

            const item = { name: uploadFile.name, progress: Math.round(((initRes.chunk_index) / initRes.total_chunks) * 100) };
            uploadStore.addUpload(item);

            const firstChunk = chunks[initRes.chunk_index - initRes.chunk_index] as Chunk
            const currentChunkMetadata: ChunkMetadata = {
                'id': initRes.id,
                'chunk_index': initRes.chunk_index,
                'md5': firstChunk.md5,
                'upload_file': firstChunk.blob
            }

            if (initRes.chunk_index === 0) {
                message.info(`开始上传 ${uploadFile.name}`);
            } else {
                message.info(`正在从 ${item.progress}% 继续上传 ${uploadFile.name}`);
            }

            let currentStatus = initRes.status;
            try {
                while (currentStatus === Status.UPLOADING) {
                    const res = await diskApi.chunk_upload(userStore.user_id, currentChunkMetadata)

                    // 更新进度
                    uploadStore.updateProgress(item, Math.round(((res.chunk_index) / res.total_chunks) * 100));

                    if ((currentStatus = res.status) === Status.FINISHED) {
                        const res = await diskApi.createFile(userStore.user_id, originalPath, {
                            name: uploadFile.name,
                            size: uploadFile.size,
                            sha256: currentFileSHA256
                        });
                        if (diskApi.isDetailResponse(res)) {
                            await userStore.fetchUser();
                            if (currentPath.value === originalPath) {
                                await loadDirectory(currentPath.value);
                            }
                            message.success(res.detail);
                            uploadStore.removeUpload(item);
                        }
                        return;
                    }

                    const currentChunk = chunks[res.chunk_index - initRes.chunk_index] as Chunk
                    currentChunkMetadata.id = res.id
                    currentChunkMetadata.chunk_index = res.chunk_index
                    currentChunkMetadata.md5 = currentChunk?.md5
                    currentChunkMetadata.upload_file = currentChunk?.blob
                }
            } catch (error: any) {
                message.error(error instanceof Error ? error.message : String(error));
                uploadStore.removeUpload(item);
            }
        }
    };

    // 文件操作
    const getFileDetail = async (row: DataItem) => {
        if (row.size && row.sha256) {
            selectedFile.value = { ...row } as FileInfo;
            selectedFileRow.value = row;
            showFileDetail.value = true;
        }
    };

    const handleDownload = (fileName: string) => {
        diskApi.downloadFile(userStore.user_id, currentPath.value, fileName, userStore.token)
    };
    const throttledHandleDownload = throttle(handleDownload, 200);

    const downloadSelectedFile = () => {
        if (selectedFileRow.value) {
            throttledHandleDownload(selectedFileRow.value.name);
            showFileDetail.value = false;
        }
    };

    const handleRename = async (row: DataItem, newName: string) => {
        const oldName = row.name;
        row.name = newName;

        try {
            if (row.size) {
                const res = await diskApi.renameFile(userStore.user_id, currentPath.value, oldName, newName);
                message.success(res.detail);
            } else {
                const res = await diskApi.renameDir(userStore.user_id, currentPath.value, oldName, newName);
                message.success(res.detail);
            }
        } catch (error: any) {
            message.error(error instanceof Error ? error.message : String(error));
            row.name = oldName;
        }
    };

    const handleRowDblclick = (row: DataItem) => {
        if (row.size)
            getFileDetail(row);
        else
            enterDir(row.name)
    };

    const handleDelete = (row: DataItem) => {
        dialog.warning({
            title: '确认删除',
            content: `确定要删除${row.size ? "文件" : "目录"} ${row.name} 吗？`,
            positiveText: '确定',
            negativeText: '取消',
            onPositiveClick: async () => {
                try {
                    if (row.size) {
                        const res = await diskApi.deleteFile(userStore.user_id, currentPath.value, row.name);
                        message.success(res.detail);
                    }
                    else {
                        const res = await diskApi.deleteDir(userStore.user_id, currentPath.value, row.name);
                        message.success(res.detail);
                    }
                    await userStore.fetchUser();
                    dataList.value = dataList.value.filter((item) => item.name !== row.name);
                } catch (error: any) {
                    message.error(error instanceof Error ? error.message : String(error));
                }
            },
        });
    };

    const handleLogoutPositiveClick = async () => {
        const res = await userStore.logout();
        router.push('/login');
        message.success(res.detail);
    }
    const throttledLogout = throttle(handleLogoutPositiveClick, 500);

    const handleUserMenuSelect = (key: string) => {
        if (key === 'logout') {
            live2dAlert("もう離れるの")

            dialog.warning({
                title: '确认退出',
                content: '确定要退出登录吗？',
                positiveText: '确定',
                negativeText: '取消',
                blockScroll: true,
                closeOnEsc: true,
                onPositiveClick: throttledLogout
            });
        }
        if (key === 'profile') {
            router.push(`/${userStore.user.username}/profile`);
        }
    };

    // 生命周期
    onMounted(async () => {
        try {
            await loadDirectory(currentPath.value);
        } catch (e) {
            throw e
        }
    });

    watch(() => route.path, async (toPath, fromPath) => {
        if (toPath.endsWith("/"))
            await loadDirectory(currentPath.value);
    });
</script>

<style scoped>
    .home-container {
        min-height: 100vh;
        background: #f5f7fa;
    }

    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 24px;
        background: white;
        height: 60px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    }

    .header-left,
    .header-right {
        display: flex;
        align-items: center;
    }

    .breadcrumb-bar {
        padding: 12px 24px;
        background: white;
        border-bottom: 1px solid #eee;
    }

    .content {
        padding: 24px;
    }

    /* 状态栏 */
    .stats-cards {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }

    .stat-card {
        text-align: center;
        overflow: hidden;
    }

    @media (max-width: 768px) {
        .stats-cards {
            gap: 8px;
        }

        .stat-card :deep(.n-statistic__label) {
            font-size: 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .stat-card :deep(.n-statistic__value) {
            font-size: 8px;
        }
    }

    /* 新建目录、搜索框 */
    .toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        gap: 12px;
        flex-wrap: wrap;
    }

    /* PC 端：按钮靠左 */
    .toolbar-actions {
        display: flex;
        gap: 12px;
    }

    .toolbar-search {
        width: 250px;
    }

    /* 移动端：按钮均匀分布 */
    @media (max-width: 768px) {
        .toolbar {
            flex-direction: column;
            align-items: stretch;
        }

        .toolbar-actions {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            width: 100%;
        }

        .toolbar-actions>* {
            flex: 1;
            /* 三个按钮等宽均匀分布 */
        }

        .toolbar-search {
            width: 100%;
        }
    }


    .progress-container {
        margin-bottom: 16px;
        padding: 12px;
        background: #f5f5f5;
        border-radius: 8px;
    }

    .progress-item {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }

    .progress-item:last-child {
        margin-bottom: 0;
    }

    .progress-name {
        width: 120px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 12px;
    }

    .progress-size {
        font-size: 12px;
        color: #666;
        white-space: nowrap;
    }


    .table-container {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        /* iOS 平滑滚动 */
    }

    /* 表格最小宽度，防止过度压缩 */
    .table-container :deep(.n-data-table) {
        min-width: 600px;
    }


    .file-detail {
        padding: 8px 0;
    }

    .detail-row {
        display: flex;
        margin-bottom: 12px;
        line-height: 1.5;
    }

    .detail-label {
        width: 70px;
        flex-shrink: 0;
        color: #666;
        font-size: 14px;
    }

    .detail-value {
        flex: 1;
        color: #333;
        font-size: 14px;
        word-break: break-all;
    }

    .sha256 {
        font-family: monospace;
        line-height: 20px;
        /* 或具体数值，如 20px */
        font-size: 12px;
        color: #00CC66;
    }
</style>
