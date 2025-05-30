<template>
  <el-card class="login-card">
    <h2>用户登录</h2>
    <el-form :model="form" :rules="rules" ref="loginForm" @submit.prevent="onSubmit">
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" autocomplete="off" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" autocomplete="off" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit" :loading="loading">登录</el-button>
        <el-link type="primary" class="ml-2" @click="goRegister">没有账号？注册</el-link>
      </el-form-item>
      <el-alert v-if="error" :title="error" type="error" show-icon />
    </el-form>
    <el-divider>或者</el-divider>
    <el-button type="success" @click="useDemoUser" class="mb-2">进入演示模式（无需登录）</el-button>
    <el-card class="demo-info" v-if="showDemoInfo">
      <div class="mb-2"><b>演示用户信息：</b></div>
      <div v-for="user in demoUsers" :key="user.email" class="mb-1">
        <el-tag type="info">{{ user.username }}</el-tag>
        <span class="ml-2">邮箱: {{ user.email }}</span>
        <span class="ml-2">密码: demo123</span>
      </div>
      <div class="mt-2 text-xs text-gray-500">* 可用任意演示账号直接登录体验</div>
    </el-card>
    <el-divider>测试账号</el-divider>
    <el-card class="demo-info">
      <div class="mb-2"><b>可用测试账号（可直接登录体验）：</b></div>
      <div class="mb-1"><el-tag type="info">张先生</el-tag> <span class="ml-2">zhang@newenergy.com</span> <span class="ml-2">标签：电力、生物柴油、天然气</span></div>
      <div class="mb-1"><el-tag type="info">李女士</el-tag> <span class="ml-2">li@traditional.com</span> <span class="ml-2">标签：原油、天然气、液化天然气(LNG)、煤炭</span></div>
      <div class="mb-1"><el-tag type="info">王先生</el-tag> <span class="ml-2">wang@carbon.com</span> <span class="ml-2">标签：电力、生物柴油、天然气</span></div>
      <div class="mb-1"><el-tag type="info">陈女士</el-tag> <span class="ml-2">chen@power.com</span> <span class="ml-2">标签：电力、煤炭、天然气</span></div>
      <div class="mb-1"><el-tag type="info">刘先生</el-tag> <span class="ml-2">liu@policy.com</span> <span class="ml-2">标签：原油、天然气、电力、煤炭</span></div>
      <div class="mt-2 text-xs text-gray-500">* 可用任意测试账号直接登录体验，体验不同标签和权限。</div>
    </el-card>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/request'

const router = useRouter()
const loginForm = ref()
const form = ref({ email: '', password: '' })
const loading = ref(false)
const error = ref('')
const showDemoInfo = ref(false)

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const demoUsers = [
  { username: '张先生', email: 'zhang@newenergy.com' },
  { username: '李女士', email: 'li@traditional.com' },
  { username: '王先生', email: 'wang@carbon.com' },
  { username: '陈女士', email: 'chen@power.com' },
  { username: '刘先生', email: 'liu@policy.com' }
]

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
    
    // 跳转到仪表盘
    router.push('/dashboard')
    
  } catch (e: any) {
    console.error('登录失败:', e)
    error.value = e.response?.data?.detail || e.response?.data?.message || '登录失败，请检查邮箱和密码'
  } finally {
    loading.value = false
  }
}

const goRegister = () => {
  alert('注册功能正在开发中...')
}

const useDemoUser = () => {
  showDemoInfo.value = !showDemoInfo.value
}
</script>

<style scoped>
.login-card { max-width: 400px; margin: 80px auto; }
.demo-info { margin-top: 16px; background: #f6f8fa; }
.ml-2 { margin-left: 8px; }
.mb-1 { margin-bottom: 4px; }
.mb-2 { margin-bottom: 8px; }
.mt-2 { margin-top: 8px; }
</style> 