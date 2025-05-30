import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { 
    path: '/dashboard', 
    component: () => import('@/pages/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  { 
    path: '/tags', 
    component: () => import('@/pages/TagsManagement.vue'),
    meta: { requiresAuth: true }
  },
  { 
    path: '/content', 
    component: () => import('@/pages/ContentList.vue'),
    meta: { requiresAuth: true }
  },
  { 
    path: '/market', 
    component: () => import('@/pages/Market.vue'),
    meta: { requiresAuth: true }
  },
  { 
    path: '/ai', 
    component: () => import('@/pages/AIAssistants.vue'),
    meta: { requiresAuth: true }
  },
  { path: '/login', component: () => import('@/pages/Login.vue') },
  { path: '/register', component: () => import('@/pages/Register.vue') },
  { 
    path: '/settings', 
    component: () => import('@/pages/Settings.vue'),
    meta: { requiresAuth: true }
  },
  { path: '/:pathMatch(.*)*', component: () => import('@/pages/NotFound.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  // 首先从localStorage初始化状态
  const token = userStore.token || localStorage.getItem('token')
  const userInfo = userStore.userInfo || JSON.parse(localStorage.getItem('userInfo') || 'null')
  
  // 如果localStorage有数据但store没有，同步到store
  if (token && !userStore.token) {
    userStore.setToken(token)
  }
  if (userInfo && !userStore.userInfo) {
    userStore.setUserInfo(userInfo)
  }
  
  // 检查路由是否需要认证
  if (to.meta.requiresAuth && !token) {
    console.log('需要登录，重定向到登录页面')
    next('/login')
  } else {
    next()
  }
})

export default router 