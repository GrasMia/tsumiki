import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from "@/stores/user"
import Login from '@/views/Login.vue';
import Register from '@/views/Register.vue';
import Home from '@/views/Home.vue';
import Profile from '@/views/Profile.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', component: Home },
        { path: '/login', component: Login },
        { path: '/register', component: Register },
        { path: '/:username/', component: Home },
        { path: '/:username/profile', component: Profile },
        { path: '/:username/:pathMatch(.*)', component: Home }
        // :path 或 :path/ 表示参数是 to/from.params.path 的字符串值
        // :path(.*) 表示 path 是一个字符串并可以包含 /（包括尾部的 / ）
        // :path(.*)* 表示 path 是一个字符串数组并不包含任何 /（如果尾部出现 / 数组最后一项将是 '' ）
    ]
});


router.beforeEach(async (to, from) => {
    const userStore = useUserStore();

    // 未登录
    if (!userStore.user_id || !userStore.token) {
        if (to.path !== '/login' && to.path !== '/register') {
            return '/login';
        }
    }

    // 已登陆
    if (userStore.user_id && userStore.token) {
        // 如果用户已登录但 userStore 中没有用户信息，尝试从 localStorage 恢复用户信息
        if (!userStore.user.username) {
            await userStore.fetchUser();
            await userStore.loadAvatar();
        }

        // 当直接访问 http(s)://host:port 时 to.path 和 from.path 均是 /    →    即默认访问URL是 http(s)://host:port/
        if (to.path === '/') {
            return `/${userStore.user.username}/`;
        }

        if (to.params.username !== userStore.user.username) {
            if (typeof to.params.username === 'string') {
                return to.path.replace(to.params.username, userStore.user.username);
            }
        }

        if (!to.params.pathMatch && to.path.endsWith('/profile/')) {
            return `/${userStore.user.username}/profile`;
        }

        if (from.path === to.path && to.path === `/${userStore.user.username}/profile`){
            return `/${userStore.user.username}/`;
        }

        if (typeof to.params.pathMatch === 'string') {
            if (!to.params.pathMatch.endsWith('/')) {
                return `/${userStore.user.username}/${to.params.pathMatch}/`;
            }
        }
    }

    // console.log('来自路径:', from.path);
    // console.log('去往路径:', to.path);
    // console.log('username:', to.params.username);
    // console.log('pathMatch:', to.params.pathMatch);
    // console.log("userStore.user.username", userStore.user.username);

    return true;
});

export default router;