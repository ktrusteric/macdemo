<template>
  <div class="login-page">
    <div class="login-background">
      <div class="background-shape shape-1"></div>
      <div class="background-shape shape-2"></div>
      <div class="background-shape shape-3"></div>
    </div>
    
    <div class="login-container">
      <div class="login-content">
        <!-- 顶部标题区域 -->
        <div class="login-header">
          <div class="platform-logo">
            <el-icon class="platform-icon"><Platform /></el-icon>
          </div>
          <h1 class="platform-title">上海石油天然气交易中心</h1>
          <p class="platform-subtitle">能源资讯智能推荐系统</p>
        </div>

        <!-- 登录表单卡片 -->
        <el-card class="login-form-card" shadow="always">
          <template #header>
            <div class="form-header">
              <el-icon class="form-icon"><User /></el-icon>
              <span class="form-title">用户登录</span>
            </div>
          </template>

          <el-form :model="form" :rules="rules" ref="loginForm" @submit.prevent="onSubmit" size="large">
            <el-form-item prop="email">
              <el-input 
                v-model="form.email" 
                placeholder="请输入邮箱地址"
                autocomplete="off"
                clearable
              >
                <template #prefix>
                  <el-icon><Message /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input 
                v-model="form.password" 
                type="password" 
                placeholder="请输入密码"
                autocomplete="off"
                show-password
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                @click="onSubmit" 
                :loading="loading"
                size="large"
                class="login-button"
              >
                <el-icon><Key /></el-icon>
                登录系统
              </el-button>
            </el-form-item>
          </el-form>

          <el-alert v-if="error" :title="error" type="error" show-icon class="error-alert" />

          <div class="login-footer">
            <el-link type="primary" @click="goRegister" :underline="false" class="register-link">
              <el-icon><Plus /></el-icon>
              还没有账号？立即注册
            </el-link>
          </div>
        </el-card>

        <!-- 演示账号区域 -->
        <el-card class="demo-accounts-card" shadow="hover">
          <template #header>
            <div class="demo-header">
              <el-icon class="demo-icon"><Avatar /></el-icon>
              <span class="demo-title">演示账号</span>
              <el-tag type="success" size="small">可直接登录</el-tag>
            </div>
          </template>

          <div class="demo-users-grid">
            <div 
              v-for="user in demoUsers" 
              :key="user.email" 
              class="demo-user-card"
              @click="quickLogin(user)"
            >
              <div class="user-info">
                <el-avatar 
                  :size="44" 
                  :style="{ backgroundColor: user.color }"
                  class="user-avatar"
                >
                  {{ user.username[0] }}
                </el-avatar>
                <div class="user-details">
                  <div class="user-name">{{ user.username }}</div>
                  <div class="user-email">{{ user.email }}</div>
                  <div class="user-tags">
                    <el-tag size="small" type="info">{{ user.city }}</el-tag>
                    <el-tag size="small" type="warning">{{ user.energy }}</el-tag>
                  </div>
                </div>
              </div>
              <el-icon class="quick-login-icon"><Right /></el-icon>
            </div>
          </div>

          <div class="demo-footer">
            <el-text type="info" size="small">
              <el-icon><InfoFilled /></el-icon>
              点击任意账号即可快速登录体验，密码统一为 demo123
            </el-text>
          </div>
        </el-card>

        <!-- 页面宽度占位符 - 不可见但确保页面宽度一致 -->
        <div class="width-placeholder" aria-hidden="true"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/request'
import { 
  Platform, 
  User, 
  Message, 
  Lock, 
  Key, 
  Plus, 
  Avatar, 
  Right, 
  InfoFilled 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loginForm = ref()
const form = ref({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

// 更新后的演示用户信息 - 基于后端实际数据
const demoUsers = [
  { 
    username: '张工程师', 
    email: 'zhang@shanghai.com',
    city: '上海',
    energy: '天然气',
    color: '#409EFF',
    description: '天然气市场分析师'
  },
  { 
    username: '李经理', 
    email: 'li@beijing.com',
    city: '北京', 
    energy: '原油',
    color: '#67C23A',
    description: '石油贸易专家'
  },
  { 
    username: '王主任', 
    email: 'wang@shenzhen.com',
    city: '深圳',
    energy: 'LNG',
    color: '#E6A23C',
    description: 'LNG项目经理'
  },
  { 
    username: '陈总监', 
    email: 'chen@guangzhou.com',
    city: '广州',
    energy: 'PNG',
    color: '#F56C6C',
    description: '管道天然气专家'
  },
  { 
    username: '刘研究员', 
    email: 'liu@chengdu.com',
    city: '成都',
    energy: '电力',
    color: '#909399',
    description: '电力系统研究员'
  }
]

const quickLogin = (user: any) => {
  form.value.email = user.email
  form.value.password = 'demo123'
  ElMessage.success(`已选择${user.description}账号`)
  onSubmit()
}

const onSubmit = async () => {
  if (!loginForm.value) return
  
  try {
    await loginForm.value.validate()
  } catch (e) {
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    // 调用后端登录API
    const response = await api.post('/users/login', {
      email: form.value.email,
      password: form.value.password
    })
    
    // 保存登录信息
    const { access_token, user_info } = response.data
    localStorage.setItem('token', access_token)
    localStorage.setItem('userInfo', JSON.stringify(user_info))
    
    ElMessage.success(`欢迎回来，${user_info.username}！`)
    
    // 跳转到仪表盘
    router.push('/dashboard')
    
  } catch (e: any) {
    console.error('登录失败:', e)
    error.value = e.response?.data?.detail || e.response?.data?.message || '登录失败，请检查邮箱和密码'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

const goRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-page {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  z-index: 9999;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  overflow: hidden;
}

.background-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 20s ease-in-out infinite;
}

.shape-1 {
  width: 300px;
  height: 300px;
  background: white;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 200px;
  height: 200px;
  background: white;
  top: 60%;
  right: 15%;
  animation-delay: 7s;
}

.shape-3 {
  width: 150px;
  height: 150px;
  background: white;
  bottom: 20%;
  left: 70%;
  animation-delay: 14s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  33% { transform: translateY(-30px) rotate(120deg); }
  66% { transform: translateY(30px) rotate(240deg); }
}

.login-container {
  position: relative;
  z-index: 10;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.login-content {
  width: 100%;
  max-width: 1280px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

.login-header {
  text-align: center;
  color: white;
  margin-bottom: 16px;
}

.platform-logo {
  margin-bottom: 16px;
}

.platform-icon {
  font-size: 64px;
  color: #FFD700;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
}

.platform-title {
  font-size: 36px;
  font-weight: 700;
  margin: 16px 0 8px 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
  letter-spacing: 1px;
}

.platform-subtitle {
  font-size: 18px;
  opacity: 0.9;
  margin: 0;
  font-weight: 300;
}

.login-form-card {
  width: 100%;
  max-width: 440px;
  border-radius: 20px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.form-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  justify-content: center;
}

.form-icon {
  color: #409EFF;
  font-size: 24px;
}

.form-title {
  color: #303133;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(45deg, #409EFF, #67C23A);
  border: none;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

.error-alert {
  margin-top: 16px;
  border-radius: 8px;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #EBEEF5;
}

.register-link {
  font-size: 15px;
  font-weight: 500;
}

.demo-accounts-card {
  width: 100%;
  max-width: 600px;
  border-radius: 20px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.demo-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
}

.demo-icon {
  color: #67C23A;
  font-size: 22px;
}

.demo-title {
  flex: 1;
  color: #303133;
}

.demo-users-grid {
  display: grid;
  gap: 16px;
}

.demo-user-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border: 2px solid #EBEEF5;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #FAFAFA, #F5F7FA);
}

.demo-user-card:hover {
  border-color: #409EFF;
  background: linear-gradient(135deg, #ECF5FF, #F0F9FF);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.2);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.user-avatar {
  border: 3px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
  font-size: 16px;
}

.user-email {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.user-tags {
  display: flex;
  gap: 8px;
}

.quick-login-icon {
  color: #C0C4CC;
  font-size: 18px;
  transition: all 0.3s ease;
}

.demo-user-card:hover .quick-login-icon {
  color: #409EFF;
  transform: translateX(6px);
}

.demo-footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #EBEEF5;
}

:deep(.el-card__header) {
  background: linear-gradient(135deg, #F8F9FA, #FFFFFF);
  border-bottom: 1px solid #EBEEF5;
  padding: 20px;
}

:deep(.el-card__body) {
  padding: 24px;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 0 16px;
  height: 48px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

/* 页面宽度占位符 - 不可见但确保页面宽度一致 */
.width-placeholder {
  width: 1280px;
  min-width: 1280px;
  height: 1px;
  visibility: hidden;
  pointer-events: none;
  position: relative;
  margin: 0 auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 20px 10px;
  }
  
  .platform-title {
    font-size: 28px;
  }
  
  .platform-subtitle {
    font-size: 16px;
  }
  
  .demo-users-grid {
    gap: 12px;
  }
  
  .demo-user-card {
    padding: 16px;
  }
}
</style> 