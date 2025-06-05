<template>
  <div class="app-layout">
    <!-- 登录、注册和管理员页面使用独立布局 -->
    <div v-if="isAuthPage || isAdminPage" class="auth-layout">
      <router-view />
    </div>
    
    <!-- 主应用布局（仅在普通用户页面显示） -->
    <template v-else>
      <el-header class="header-bar">
        <div class="header-left">
          <img src="@/logo.png" alt="上海石油天然气交易中心" class="header-logo" />
          <span class="logo">上海石油天然气交易中心信息门户系统</span>
        </div>
        <div class="header-right">
          <template v-if="isLoggedIn && userInfo">
            <div class="user-info">
              <span class="user-greeting">
                <el-icon class="user-icon"><i class="el-icon-user"></i></el-icon>
                {{ userInfo.username || userInfo.email }}{{ getGreeting() }}
              </span>
            </div>
            <div class="action-buttons">
              <el-button type="info" @click="goNotifications">
                <el-icon><i class="el-icon-bell"></i></el-icon>
                <span>消息</span>
              </el-button>
              <el-button type="primary" @click="goSettings">
                <el-icon><i class="el-icon-setting"></i></el-icon>
                <span>设置</span>
              </el-button>
              <el-button type="danger" @click="logout">
                <el-icon><i class="el-icon-switch-button"></i></el-icon>
                <span>退出</span>
              </el-button>
            </div>
          </template>
          <template v-else>
            <el-button type="primary" class="login-btn" @click="() => router.push('/login')">
              <el-icon><i class="el-icon-user"></i></el-icon>
              <span>登录</span>
            </el-button>
          </template>
        </div>
      </el-header>
      <div class="main-content">
        <el-aside width="180px" class="sidebar-nav" v-if="isLoggedIn">
          <el-menu :default-active="activeMenu" class="el-menu-vertical-demo" @select="handleMenuSelect" router>
            <el-menu-item index="/dashboard">
              <el-icon><i class="el-icon-menu"></i></el-icon>
              <span> 📊 仪表盘</span>
            </el-menu-item>
            <el-menu-item index="/content">
              <el-icon><i class="el-icon-document"></i></el-icon>
              <span> 📝 行业资讯</span>
            </el-menu-item>
            <!-- 我的收藏功能已集成到设置页面，暂时隐藏独立菜单项 -->
            <!-- <el-menu-item index="/favorites">
              <el-icon><i class="fas fa-heart"></i></el-icon>
              <span> 📖 我的收藏</span>
            </el-menu-item> -->
            <el-menu-item index="/market">
              <el-icon><i class="el-icon-data-analysis"></i></el-icon>
              <span> 📈 行情信息</span>
            </el-menu-item>
            <el-menu-item index="/ai">
              <el-icon><i class="el-icon-robot"></i></el-icon>
              <span> 🤖 A I 助手</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <router-view />
        </el-main>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/store/user'
import { useRouter, useRoute } from 'vue-router'
import { computed, onMounted } from 'vue'
// import AIAssistantFloat from '@/components/AIAssistantFloat.vue'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

// 在组件挂载时初始化状态
onMounted(() => {
  // 从localStorage初始化用户状态
  userStore.initializeFromStorage()
  console.log('应用初始化 - 用户状态:', {
    isLoggedIn: userStore.isLoggedIn,
    hasToken: !!userStore.token,
    hasUserInfo: !!userStore.userInfo
  })
})

const userInfo = computed(() => userStore.currentUser)
const isLoggedIn = computed(() => userStore.isLoggedIn)
const activeMenu = computed(() => route.path)

// 更明确地定义认证页面（登录、注册等）和管理员页面
const isAuthPage = computed(() => {
  const authPaths = ['/login', '/register', '/login-simple', '/admin/login']
  return authPaths.includes(route.path)
})

// 检查是否是管理员页面
const isAdminPage = computed(() => {
  return route.path.startsWith('/admin')
})

// 是否显示普通用户布局
const showUserLayout = computed(() => {
  return !isAuthPage.value && !isAdminPage.value
})

const logout = () => {
  userStore.logout()
  router.push('/login')
}

const goSettings = () => {
  router.push('/settings')
}

const goNotifications = () => {
  router.push('/notifications')
}

const handleMenuSelect = (index: string) => {
  router.push(index)
}

const getGreeting = () => {
  const now = new Date()
  const hours = now.getHours()
  
  if (hours >= 5 && hours < 12) {
    return '，上午好！'
  } else if (hours >= 12 && hours < 14) {
    return '，中午好！'
  } else if (hours >= 14 && hours < 18) {
    return '，下午好！'
  } else {
    return '，晚上好！'
  }
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 认证页面独立布局 - 全屏无干扰 */
.auth-layout {
  min-height: 100vh;
  width: 100%;
  position: relative;
  z-index: 1000;
}

/* 主应用布局 */
.main-content {
  display: flex;
  flex: 1;
  background: #f5f7fa;
}

.el-aside.sidebar-nav {
  background: #fff;
  border-right: 1px solid #e4e7ed;
  box-shadow: 2px 0 8px #e4e7ed22;
  min-height: calc(100vh - 56px);
  padding-top: 16px;
}

.el-main {
  flex: 1;
  padding: 24px;
  background: #f5f7fa;
}

.el-menu-vertical-demo {
  border-right: none;
}

.el-menu-item {
  font-size: 16px;
  height: 48px;
  line-height: 48px;
}

.el-menu-item.is-active {
  background: #e6f7ff !important;
  color: #1769aa !important;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  height: 56px;
  background: linear-gradient(90deg, #e0e7ef 0%, #f5f7fa 100%);
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px #e4e7ed33;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-logo {
  width: 40px;
  height: auto;
  max-height: 36px;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.logo {
  font-weight: bold;
  font-size: 18px;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-greeting {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 6px;
}

.user-icon {
  font-size: 16px;
  color: #409eff;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-buttons :deep(.el-button) {
  height: 32px !important;
  padding: 0 8px !important;
  border-radius: 6px !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  border: none !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1) !important;
  min-width: auto !important;
  width: auto !important;
}

.action-buttons :deep(.el-button .el-icon) {
  font-size: 14px !important;
  margin-right: 4px !important;
}

.action-buttons :deep(.el-button span) {
  line-height: 1 !important;
}

.action-buttons :deep(.el-button:hover) {
  transform: translateY(-1px) !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15) !important;
}

/* 消息通知按钮 */
.action-buttons :deep(.el-button--info) {
  background: #17a2b8 !important;
  color: #ffffff !important;
}

.action-buttons :deep(.el-button--info:hover) {
  background: #138496 !important;
}

/* 个人设置按钮 */
.action-buttons :deep(.el-button--primary) {
  background: #409eff !important;
  color: #ffffff !important;
}

.action-buttons :deep(.el-button--primary:hover) {
  background: #337ecc !important;
}

/* 退出登录按钮 */
.action-buttons :deep(.el-button--danger) {
  background: #f56c6c !important;
  color: #ffffff !important;
}

.action-buttons :deep(.el-button--danger:hover) {
  background: #e53e3e !important;
}

/* 登录按钮样式 */
.login-btn {
  height: 36px;
  padding: 0 16px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  background: #409eff;
  color: #ffffff;
  border: none;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.login-btn:hover {
  background: #337ecc;
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(64, 158, 255, 0.3);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-right {
    gap: 12px;
  }
  
  .action-buttons {
    gap: 6px;
  }
  
  .action-buttons :deep(.el-button) {
    padding: 0 6px !important;
    font-size: 12px !important;
  }
  
  .user-greeting {
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  .header-right {
    gap: 8px;
  }
  
  .action-buttons :deep(.el-button) {
    height: 28px !important;
    padding: 0 6px !important;
    font-size: 11px !important;
  }
  
  .action-buttons :deep(.el-button span) {
    display: none !important;
  }
  
  .user-greeting {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .action-buttons :deep(.el-button) {
    height: 26px !important;
    padding: 0 4px !important;
    border-radius: 4px !important;
  }
  
  .user-greeting {
    font-size: 11px;
  }
  
  .user-icon {
    font-size: 14px;
  }
}

.mr-2 { 
  margin-right: 12px; 
}
</style>
