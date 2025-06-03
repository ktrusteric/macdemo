<template>
  <div class="admin-layout">
    <!-- 顶部导航栏 -->
    <div class="admin-header">
      <div class="header-left">
        <h1>🛠️ 管理员后台</h1>
        <p>上海石油天然气交易中心信息门户系统</p>
      </div>
      <div class="header-right">
        <span class="admin-info">
          👤 {{ adminInfo?.username || '管理员' }}
        </span>
        <button @click="handleLogout" class="logout-btn">
          🚪 退出登录
        </button>
      </div>
    </div>

    <div class="admin-body">
      <!-- 侧边导航栏 -->
      <div class="admin-sidebar">
        <nav class="sidebar-nav">
          <router-link 
            v-for="item in menuItems" 
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: $route.path === item.path }"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-text">{{ item.name }}</span>
          </router-link>
        </nav>
      </div>

      <!-- 主内容区域 -->
      <div class="admin-main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/store/admin'

const router = useRouter()
const adminStore = useAdminStore()

const adminInfo = computed(() => adminStore.adminInfo)

// 菜单项配置
const menuItems = [
  { path: '/admin/dashboard', name: '仪表盘', icon: '📊' },
  { path: '/admin/articles', name: '内容管理', icon: '📝' },
  { path: '/admin/users', name: '用户管理', icon: '👥' }
]

// 处理登出
const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    adminStore.logout()
    router.push('/admin/login')
  }
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #f5f7fa;
}

.admin-header {
  background: white;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left h1 {
  margin: 0 0 4px 0;
  color: #2d3748;
  font-size: 24px;
  font-weight: 600;
}

.header-left p {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-info {
  color: #4a5568;
  font-weight: 500;
}

.logout-btn {
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.logout-btn:hover {
  background: #c53030;
}

.admin-body {
  display: flex;
  min-height: calc(100vh - 80px);
}

.admin-sidebar {
  width: 240px;
  background: white;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  padding: 20px 0;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 16px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  text-decoration: none;
  color: #4a5568;
  transition: all 0.2s;
  font-weight: 500;
}

.nav-item:hover {
  background: #f7fafc;
  color: #2d3748;
}

.nav-item.active {
  background: #e3f2fd;
  color: #1976d2;
}

.nav-icon {
  font-size: 18px;
  width: 20px;
  text-align: center;
}

.nav-text {
  font-size: 14px;
}

.admin-main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-sidebar {
    width: 200px;
  }
  
  .admin-main {
    padding: 16px;
  }
  
  .header-left h1 {
    font-size: 20px;
  }
}
</style> 