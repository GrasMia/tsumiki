<template>
    <n-data-table :columns="columns" :data="data" :loading="loading" :row-key="rowKey" :bordered="bordered"
        :striped="striped" :row-props="getRowProps" />
</template>

<script setup lang="ts">
    import { h, computed, ref, nextTick } from 'vue';
    import { NButton, NSpace, NIcon, NDataTable, NInput, type DataTableColumns } from 'naive-ui';
    import { DownloadOutline, TrashOutline, CreateOutline } from '@vicons/ionicons5';
    import type { DataItem } from '@/api/disk';
    import { formatStorage } from '@/utils/format';

    const props = defineProps<{
        data: DataItem[];
        loading?: boolean;
        bordered?: boolean;
        striped?: boolean;
    }>();

    const emit = defineEmits<{
        (e: 'rename', row: DataItem, newName: string): void;
        (e: 'delete', row: DataItem): void;
        (e: 'downloadFile', fileName: string): void;
        (e: 'rowDblclick', row: DataItem): void;
    }>();

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
                const isDir = row.size === undefined;
                const isEditing = editingRow.value === row;

                if (isEditing) {
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
                    h('span', isDir ? '📁' : '📄'),
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
            width: 165,
            align: 'center',
            render(row) {
                const isDir = row.size === undefined;
                const isEditing = editingRow.value === row;

                if (isEditing) {
                    return null; // 编辑时隐藏操作按钮
                }

                if (isDir) {
                    return h(NSpace, { justify: "end" }, {
                        default: () => [
                            h(NButton, {
                                size: 'small',
                                quaternary: true,
                                onClick: () => startRename(row),
                            }, { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }) }),
                            h(NButton, {
                                size: 'small',
                                quaternary: true,
                                type: 'error',
                                onClick: () => emit('delete', row),
                            }, { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) }),
                        ]
                    });
                }
                return h(NSpace, { justify: 'end' }, {
                    default: () => [
                        h(NButton, {
                            size: 'small',
                            quaternary: true,
                            onClick: () => emit('downloadFile', row.name),
                        }, { icon: () => h(NIcon, null, { default: () => h(DownloadOutline) }) }),
                        h(NButton, {
                            size: 'small',
                            quaternary: true,
                            onClick: () => startRename(row),
                        }, { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }) }),
                        h(NButton, {
                            size: 'small',
                            quaternary: true,
                            type: 'error',
                            onClick: () => emit('delete', row),
                        }, { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) })
                    ]
                });
            }
        }
    ]);
</script>