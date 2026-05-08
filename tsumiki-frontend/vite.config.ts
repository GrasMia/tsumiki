import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
    plugins:
        [vue(),
        vueDevTools({
            launchEditor: 'code',  // 点击组件时用 VS Code 打开
        })],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    server: {
        host: '0.0.0.0',
        port: 3000,
        proxy: {
            '/auth': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
            '/users': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
            '/disk': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            }
        },
        // https: {
        //     key: fs.readFileSync(path.resolve(__dirname, 'your_key_path')),
        //     cert: fs.readFileSync(path.resolve(__dirname, 'your_cert_path')),
        // },
    },
    build: {
        chunkSizeWarningLimit: 500,
        rollupOptions: {
            output: {
                manualChunks(id) {
                    if (id.includes('naive-ui')) {
                        if (id.includes('data-table')) {
                            return 'naive-table'
                        }
                        return 'naive-ui'
                    }
                }
            }
        }
    }
})
