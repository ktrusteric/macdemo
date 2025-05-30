<template>
  <div class="app-layout">
    <el-header class="header-bar" v-if="!isLoginPage">
      <div class="header-left">
        <span class="logo">⛽ 石油天然气信息门户</span>
      </div>
      <div class="header-right">
        <template v-if="isLoggedIn && userInfo">
          <el-tag type="info" class="mr-2">{{ userInfo.username || userInfo.email }}</el-tag>
          <el-button type="default" icon="el-icon-bell" class="mr-2" @click="goNotifications">消息通知</el-button>
          <el-button type="primary" icon="el-icon-setting" @click="goSettings" class="mr-2">设置</el-button>
          <el-button type="danger" @click="logout">退出</el-button>
        </template>
        <template v-else>
          <el-button type="primary" @click="() => router.push('/login')">登录</el-button>
        </template>
      </div>
    </el-header>
    <div class="main-content">
      <el-aside width="180px" class="sidebar-nav" v-if="!isLoginPage && isLoggedIn">
        <el-menu :default-active="activeMenu" class="el-menu-vertical-demo" @select="handleMenuSelect" router>
          <el-menu-item index="/dashboard">
            <el-icon><i class="el-icon-menu"></i></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/tags">
            <el-icon><i class="el-icon-collection"></i></el-icon>
            <span>标签管理</span>
          </el-menu-item>
          <el-menu-item index="/content">
            <el-icon><i class="el-icon-document"></i></el-icon>
            <span>内容资讯</span>
          </el-menu-item>
          <el-menu-item index="/market">
            <el-icon><i class="el-icon-data-analysis"></i></el-icon>
            <span>行情信息</span>
          </el-menu-item>
          <el-menu-item index="/ai">
            <el-icon><i class="el-icon-robot"></i></el-icon>
            <span>AI助手</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <router-view />
      </el-main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/store/user'
import { useRouter, useRoute } from 'vue-router'
import { computed, onMounted } from 'vue'

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
const isLoginPage = computed(() => route.path === '/login' || route.path === '/register')

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
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
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
  padding: 32px 24px 24px 24px;
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
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
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
.header-left .logo {
  font-weight: bold;
  font-size: 22px;
  color: #1769aa;
  letter-spacing: 2px;
  display: flex;
  align-items: center;
}
.header-right {
  display: flex;
  align-items: center;
}
.mr-2 { margin-right: 12px; }
</style>
