import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: 'ChatGalaxy - AI智能聊天平台',
      },
    },
    {
      path: '/chat',
      name: 'chat',
      component: HomeView,
      meta: {
        title: 'ChatGalaxy - 聊天',
      },
    },
  ],
})

// 路由守卫：设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta?.title) {
    document.title = to.meta.title as string
  }
  next()
})

export default router
