import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes: RouteRecordRaw[] = [
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
    path: '/favorites', 
    component: () => import('@/pages/Favorites.vue'),
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
  // 管理员登录页面（独立页面）
  { 
    path: '/admin/login', 
    component: () => import('@/pages/AdminLogin.vue'),
    meta: { requiresGuest: true }
  },
  // 管理员后台路由（使用布局组件）
  {
    path: '/admin',
    component: () => import('@/components/AdminLayout.vue'),
    meta: { requiresAdminAuth: true },
    children: [
      {
        path: 'dashboard',
        component: () => import('@/pages/AdminDashboard.vue'),
        meta: { requiresAdminAuth: true }
      },
      {
        path: 'articles',
        component: () => import('@/pages/AdminArticles.vue'),
        meta: { requiresAdminAuth: true }
      },
      {
        path: 'users',
        component: () => import('@/pages/AdminUsers.vue'),
        meta: { requiresAdminAuth: true }
      },
      {
        path: 'chat-history',
        component: () => import('@/pages/admin/ChatHistoryManagement.vue'),
        meta: { requiresAdminAuth: true }
      }
    ]
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
  const adminToken = localStorage.getItem('admin_token')
  const adminInfo = JSON.parse(localStorage.getItem('admin_info') || 'null')
  
  // 如果localStorage有数据但store没有，同步到store
  if (token && !userStore.token) {
    userStore.setToken(token)
  }
  if (userInfo && !userStore.userInfo) {
    userStore.setUserInfo(userInfo)
  }
  
  // 检查管理员路由权限
  if (to.meta.requiresAdminAuth) {
    if (!adminToken || !adminInfo) {
      console.log('需要管理员登录，重定向到管理员登录页面')
      next('/admin/login')
      return
    }
  }
  
  // 检查访客路由（如登录页面）
  if (to.meta.requiresGuest) {
    if (adminToken && adminInfo && to.path.startsWith('/admin')) {
      console.log('管理员已登录，重定向到管理员仪表板')
      next('/admin/dashboard')
      return
    }
    if (token && userInfo && !to.path.startsWith('/admin')) {
      console.log('用户已登录，重定向到用户仪表板')
      next('/dashboard')
      return
    }
  }
  
  // 检查普通用户路由权限
  if (to.meta.requiresAuth && !token) {
    console.log('需要登录，重定向到登录页面')
    next('/login')
  } else {
    next()
  }
})

export default router 