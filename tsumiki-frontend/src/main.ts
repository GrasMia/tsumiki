import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

L2Dwidget?.init({
    model: {
        jsonPath: 'https://unpkg.com/live2d-widget-model-tsumiki@1.0.5/assets/tsumiki.model.json',
        scale: 1
    },
    display: {
        width: 240,
        height: 800,
        position: 'right',
        hOffset: 70,
        vOffset: -225,
    },
    mobile: { show: false, scale: 1 },
    dialog: {
        enable: true,
        hitokoto: true,
        script: { 'every idle 1m': '$hitokoto$' }
    }
});
