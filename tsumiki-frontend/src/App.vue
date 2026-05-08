<template>
    <n-config-provider :locale="zhCN" :date-locale="dateZhCN">
        <n-dialog-provider>
            <n-message-provider>
                <n-notification-provider>
                    <router-view />
                </n-notification-provider>
            </n-message-provider>
        </n-dialog-provider>
    </n-config-provider>
</template>

<script setup lang="ts">
    import {
        NConfigProvider,
        NDialogProvider,
        NMessageProvider,
        NNotificationProvider,
        zhCN,
        dateZhCN,
        jaJP,
        dateJaJP
    } from 'naive-ui';
</script>