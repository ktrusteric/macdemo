<template>
  <div class="page-container">
    <div class="login-container">
      <h1>OpenResty 负载均衡管理平台</h1>
      <div class="login-form">
        <h2>用户登录</h2>
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label>邮箱:</label>
            <input v-model="email" type="email" required />
          </div>
          <div class="form-group">
            <label>密码:</label>
            <input v-model="password" type="password" required />
          </div>
          <button type="submit" class="login-btn">登录</button>
        </form>
        <div class="demo-accounts">
          <h3>测试账号</h3>
          <p>zhang@newenergy.com / demo123</p>
          <p>li@traditional.com / demo123</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const password = ref('')

const handleLogin = () => {
  console.log('Login attempt:', email.value, password.value)
  // 简单模拟登录
  if (email.value && password.value) {
    alert('登录功能正在开发中...')
    router.push('/')
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-container {
  max-width: 400px;
  width: 100%;
  text-align: center;
}

.login-form {
  background: #f8f9fa;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 15px;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

.login-btn:hover {
  background: #0056b3;
}

.demo-accounts {
  margin-top: 20px;
  padding: 15px;
  background: #e9ecef;
  border-radius: 4px;
  text-align: left;
}

.demo-accounts h3 {
  margin-top: 0;
  color: #495057;
}

.demo-accounts p {
  margin: 5px 0;
  font-family: monospace;
  font-size: 14px;
}
</style> 