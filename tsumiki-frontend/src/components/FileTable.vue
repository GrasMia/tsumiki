<template>
    <n-data-table :columns="columns" :data="displayData" :row-key="rowKey" :bordered="bordered" :striped="striped"
        :row-props="getRowProps" />
</template>

<script setup lang="ts">
    import { h, computed, ref, nextTick } from 'vue';
    import { NButton, NSpace, NIcon, NDataTable, NInput, type DataTableColumns } from 'naive-ui';
    import { DownloadOutline, TrashOutline, CreateOutline, MoveOutline } from '@vicons/ionicons5';
    import type { DataItem } from '@/api/disk';
    import { formatStorage } from '@/utils/format';

    const props = defineProps<{
        data: DataItem[];
        bordered?: boolean;
        striped?: boolean;
        moving?: boolean;
    }>();

    const emit = defineEmits<{
        (e: 'rename', row: DataItem, newName: string): void;
        (e: 'delete', row: DataItem): void;
        (e: 'downloadFile', fileName: string): void;
        (e: 'rowDblclick', row: DataItem): void;
        (e: 'move', row: DataItem): void;
    }>();

    const displayData = computed(() => {
        if (!props.moving) return props.data;
        return props.data.filter(row => row.size === undefined); // 移动时只显示目录
    });

    // 正在编辑的行
    const editingRow = ref<DataItem | null>(null);
    const editingName = ref('');

    const startRename = (row: DataItem) => {
        editingRow.value = row;
        editingName.value = row.name;

        nextTick(() => {
            const input = document.querySelector('.rename-input input') as HTMLInputElement;
            if (!input) return;

            input.focus();

            // 如果是文件且有后缀名，只选中文件名部分（不含后缀）
            if (row.size !== undefined) {
                const lastDotIndex = row.name.lastIndexOf('.');
                if (lastDotIndex > 0) {
                    input.setSelectionRange(0, lastDotIndex);
                    return;
                }
            }

            // 目录或无后缀的文件：全选
            input.select();
        });
    };

    const cancelRename = () => {
        editingRow.value = null;
        editingName.value = '';
    };

    const confirmRename = (row: DataItem) => {
        if (editingName.value && editingName.value !== row.name) {
            emit('rename', row, editingName.value);
        }
        cancelRename();
    };

    const rowKey = (row: DataItem) => row.name;

    const getRowProps = (row: DataItem) => {
        if (editingRow.value === row) {
            return {
                style: 'cursor: default',
            };
        }
        return {
            onDblclick: () => {
                emit('rowDblclick', row);
            },
            style: 'cursor: pointer',
        };
    };

    const columns = computed<DataTableColumns<DataItem>>(() => [
        {
            title: '文件名',
            key: 'name',
            resizable: true,
            ellipsis: true,
            render(row) {
                if (editingRow.value === row) {
                    return h(NInput, {
                        value: editingName.value,
                        onUpdateValue: (val: string) => { editingName.value = val; },
                        size: 'small',
                        class: 'rename-input',
                        onBlur: () => confirmRename(row),
                        onKeyup: (e: KeyboardEvent) => {
                            if (e.key === 'Enter') confirmRename(row);
                            if (e.key === 'Escape') cancelRename();
                        }
                    });
                }

                return h('div', { style: 'display: flex; align-items: center; gap: 8px' }, [
                    h('span', row.size === undefined ? '📁' : '📄'),
                    h('span', row.name),
                ]);
            }
        },
        {
            title: '大小',
            key: 'size',
            width: 120,
            render(row) {
                if (row.size === undefined) return '-';
                return formatStorage(row.size);
            }
        },
        {
            title: '修改时间',
            key: 'modified_at',
            width: 180,
            render(row) {
                return new Date(row.modified_at).toLocaleString();
            }
        },
        {
            title: '操作',
            key: 'actions',
            width: 230,
            align: 'center',
            render(row) {
                if (editingRow.value === row || props.moving) { return null; }

                const buttons = [
                    // 下载按钮（仅文件）
                    ...(row.size === undefined ? [] : [h(NButton, {
                        size: 'small',
                        quaternary: true,
                        onClick: () => emit('downloadFile', row.name),
                    }, { icon: () => h(NIcon, null, { default: () => h(DownloadOutline) }) })]),

                    // 重命名按钮
                    h(NButton, {
                        size: 'small',
                        quaternary: true,
                        onClick: () => startRename(row),
                    }, { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }) }),

                    // 移动按钮
                    h(NButton, {
                        size: 'small',
                        quaternary: true,
                        onClick: () => emit('move', row),
                    }, { icon: () => h(NIcon, null, { default: () => h(MoveOutline) }) }),

                    // 删除按钮
                    h(NButton, {
                        size: 'small',
                        quaternary: true,
                        type: 'error',
                        onClick: () => emit('delete', row),
                    }, { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) }),
                ];

                return h(NSpace, { justify: 'end' }, {
                    default: () => buttons
                });
            }
        }
    ]);
</script>