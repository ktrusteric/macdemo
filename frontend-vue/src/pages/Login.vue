<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="platform-title">
          <el-icon class="platform-icon"><Platform /></el-icon>
          上海石油天然气交易中心
        </h1>
        <p class="platform-subtitle">能源资讯智能咨询系统</p>
      </div>

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
              style="width: 100%"
            >
              <el-icon><Key /></el-icon>
              登录系统
            </el-button>
          </el-form-item>
        </el-form>

        <el-alert v-if="error" :title="error" type="error" show-icon class="error-alert" />

        <div class="login-footer">
          <el-link type="primary" @click="goRegister" :underline="false">
            <el-icon><Plus /></el-icon>
            还没有账号？立即注册
          </el-link>
        </div>
      </el-card>

      <!-- 测试账号区域 -->
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
                :size="40" 
                :style="{ backgroundColor: user.color }"
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
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 900px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
  color: white;
}

.platform-title {
  font-size: 32px;
  font-weight: bold;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.platform-icon {
  font-size: 36px;
  color: #FFD700;
}

.platform-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.login-form-card {
  margin-bottom: 24px;
  border-radius: 16px;
  overflow: hidden;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
}

.form-icon {
  color: #409EFF;
}

.form-title {
  color: #303133;
}

.error-alert {
  margin-top: 16px;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #EBEEF5;
}

.demo-accounts-card {
  border-radius: 16px;
  overflow: hidden;
}

.demo-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
}

.demo-icon {
  color: #67C23A;
}

.demo-title {
  flex: 1;
  color: #303133;
}

.demo-users-grid {
  display: grid;
  gap: 12px;
}

.demo-user-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border: 2px solid #EBEEF5;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  background: #FAFAFA;
}

.demo-user-card:hover {
  border-color: #409EFF;
  background: #ECF5FF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.user-email {
  font-size: 13px;
  color: #909399;
  margin-bottom: 6px;
}

.user-tags {
  display: flex;
  gap: 6px;
}

.quick-login-icon {
  color: #C0C4CC;
  font-size: 16px;
  transition: all 0.3s;
}

.demo-user-card:hover .quick-login-icon {
  color: #409EFF;
  transform: translateX(4px);
}

.demo-footer {
  text-align: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #EBEEF5;
}

:deep(.el-card__header) {
  background: #F8F9FA;
  border-bottom: 1px solid #EBEEF5;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: bold;
}
</style> 