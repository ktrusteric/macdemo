<template>
  <div class="admin-login-page">
    <div class="login-background">
      <div class="background-shape shape-1"></div>
      <div class="background-shape shape-2"></div>
      <div class="background-shape shape-3"></div>
    </div>
    
    <div class="admin-login-container">
      <div class="login-content">
        <!-- 顶部标题区域 -->
        <div class="login-header">
          <div class="platform-logo">
            <div class="platform-icon">🔐</div>
          </div>
          <h1 class="platform-title">管理员登录</h1>
          <p class="platform-subtitle">上海石油天然气交易中心信息门户系统 - 管理后台</p>
        </div>

        <!-- 登录表单卡片 -->
        <div class="login-card">
          <form @submit.prevent="handleLogin" class="login-form">
            <div class="form-group">
              <label for="username">用户名或邮箱</label>
              <input
                id="username"
                v-model="loginForm.username"
                type="text"
                placeholder="请输入用户名或邮箱"
                required
                :disabled="loading"
              />
            </div>
            
            <div class="form-group">
              <label for="password">密码</label>
              <input
                id="password"
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                required
                :disabled="loading"
              />
            </div>
            
            <button type="submit" class="login-btn" :disabled="loading">
              <span v-if="loading">🔄 登录中...</span>
              <span v-else">🚀 登录</span>
            </button>
          </form>
          
          <div v-if="error" class="error-message">
            ❌ {{ error }}
          </div>
          
          <!-- 详细日志输出区域 -->
          <div v-if="debugLogs.length > 0" class="debug-logs">
            <h3>🔍 调试日志</h3>
            <div class="log-container">
              <div v-for="(log, index) in debugLogs" :key="index" :class="['log-entry', log.type]">
                <span class="log-time">{{ log.time }}</span>
                <span class="log-message">{{ log.message }}</span>
                <pre v-if="log.data" class="log-data">{{ JSON.stringify(log.data, null, 2) }}</pre>
              </div>
            </div>
            <button @click="clearLogs" class="clear-logs-btn">🗑️ 清除日志</button>
          </div>
          
          <div class="login-footer">
            <p>内置管理员账户:</p>
            <div class="admin-accounts">
              <div class="account-item">
                <strong>主管理员:</strong>
                <p>用户名: <code>admin</code> | 密码: <code>admin123456</code></p>
                <button @click="quickLogin('admin', 'admin123456')" class="quick-login-btn">快速登录</button>
              </div>
              <div class="account-item">
                <strong>超级管理员:</strong>
                <p>用户名: <code>superadmin</code> | 密码: <code>super123456</code></p>
                <button @click="quickLogin('superadmin', 'super123456')" class="quick-login-btn">快速登录</button>
              </div>
            </div>
            <p class="security-note">⚠️ 这些是系统内置管理员账户，无需单独创建</p>
            <p class="security-note">🔒 建议在生产环境中修改默认密码</p>
            
            <!-- 系统状态检查 -->
            <div class="system-status">
              <h4>🔧 系统状态检查</h4>
              <button @click="checkSystemStatus" class="status-check-btn">检查系统状态</button>
              <div v-if="systemStatus" class="status-result">
                <div :class="['status-item', systemStatus.backend ? 'success' : 'error']">
                  后端服务: {{ systemStatus.backend ? '✅ 正常' : '❌ 异常' }}
                </div>
                <div :class="['status-item', systemStatus.api ? 'success' : 'error']">
                  API接口: {{ systemStatus.api ? '✅ 正常' : '❌ 异常' }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 页面宽度占位符 - 不可见但确保页面宽度一致 -->
        <div class="width-placeholder" aria-hidden="true"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '../store/admin'

const router = useRouter()
const adminStore = useAdminStore()

const loading = ref(false)
const error = ref('')
const debugLogs = ref<Array<{time: string, type: string, message: string, data?: any}>>([])
const systemStatus = ref<{backend: boolean, api: boolean} | null>(null)

const loginForm = reactive({
  username: '',
  password: ''
})

// 添加调试日志
const addLog = (type: 'info' | 'success' | 'error' | 'warning', message: string, data?: any) => {
  const time = new Date().toLocaleTimeString()
  debugLogs.value.push({ time, type, message, data })
  console.log(`[${type.toUpperCase()}] ${time}: ${message}`, data || '')
}

// 清除日志
const clearLogs = () => {
  debugLogs.value = []
}

// 快速登录
const quickLogin = (username: string, password: string) => {
  loginForm.username = username
  loginForm.password = password
  addLog('info', `使用快速登录: ${username}`)
  handleLogin()
}

// 检查系统状态
const checkSystemStatus = async () => {
  addLog('info', '开始检查系统状态...')
  
  const status = { backend: false, api: false }
  
  try {
    // 检查后端服务
    addLog('info', '检查后端服务连接...')
    const backendResponse = await fetch('/api/v1/health', {
      method: 'GET'
    })
    
    if (backendResponse.ok) {
      status.backend = true
      addLog('success', '后端服务连接正常')
    } else {
      addLog('error', `后端服务响应异常: ${backendResponse.status}`)
    }
  } catch (err: any) {
    addLog('error', `后端服务连接失败: ${err.message}`)
  }
  
  try {
    // 检查管理员API - 使用一个不需要认证的端点或者正确处理认证错误
    addLog('info', '检查管理员API...')
    
    // 先尝试访问需要认证的API，403/401都表示API正常但需要认证
    const apiResponse = await fetch('/api/v1/admin/stats', {
      method: 'GET'
    })
    
    // 200 (成功), 401 (未认证), 403 (需要认证) 都表示API正常
    if (apiResponse.ok || apiResponse.status === 401 || apiResponse.status === 403) {
      status.api = true
      if (apiResponse.ok) {
        addLog('success', 'API接口正常 (已认证)')
      } else {
        addLog('success', 'API接口正常 (需要认证)')
      }
    } else if (apiResponse.status === 404) {
      addLog('error', 'API接口不存在 (404)')
    } else if (apiResponse.status >= 500) {
      addLog('error', `API服务器错误: ${apiResponse.status}`)
    } else {
      addLog('error', `API接口异常: ${apiResponse.status}`)
    }
  } catch (err: any) {
    addLog('error', `API接口连接失败: ${err.message}`)
    // 如果是网络错误，可能是代理问题，尝试直接访问后端
    try {
      addLog('info', '尝试直接访问后端API...')
      const directResponse = await fetch('http://localhost:8001/api/v1/admin/stats', {
        method: 'GET'
      })
      if (directResponse.status === 403 || directResponse.status === 401) {
        status.api = true
        addLog('success', 'API接口正常 (直接访问成功)')
      }
    } catch (directErr: any) {
      addLog('error', `直接访问也失败: ${directErr.message}`)
    }
  }
  
  systemStatus.value = status
  addLog('info', '系统状态检查完成', status)
}

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    error.value = '请填写用户名和密码'
    addLog('warning', '登录表单验证失败: 缺少用户名或密码')
    return
  }
  
  loading.value = true
  error.value = ''
  
  addLog('info', `开始管理员登录流程: ${loginForm.username}`)
  
  try {
    // 记录请求详情
    const requestData = {
      username: loginForm.username,
      password: '***' // 不记录真实密码
    }
    addLog('info', '发送登录请求', requestData)
    
    // 检查网络连接和后端服务状态
    addLog('info', '检查系统状态...')
    try {
      // 使用Promise.race实现超时控制
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('请求超时')), 5000)
      })
      
      const healthResponse = await Promise.race([
        fetch('/api/v1/health', { method: 'GET' }),
        timeoutPromise
      ]) as Response
      
      if (!healthResponse.ok) {
        addLog('error', `后端服务异常: HTTP ${healthResponse.status}`)
        throw new Error('后端服务不可用，请检查服务器状态')
      }
      
      addLog('success', '后端服务连接正常')
    } catch (networkError: any) {
      addLog('error', '网络连接检查失败', {
        error: networkError.message,
        suggestion: '请检查后端服务是否启动'
      })
      
      if (networkError.message.includes('fetch') || networkError.message.includes('超时')) {
        throw new Error('无法连接到后端服务，请确认：\n1. 后端服务是否已启动\n2. 端口8001是否可访问\n3. 网络连接是否正常')
      }
      throw networkError
    }
    
    // 执行登录
    addLog('info', '调用管理员Store登录方法...')
    await adminStore.login(loginForm.username, loginForm.password)
    
    addLog('success', '管理员登录成功!')
    addLog('info', '准备跳转到管理后台...')
    
    // 登录成功，跳转到管理后台
    router.push('/admin/dashboard')
    
  } catch (err: any) {
    let errorMessage = '登录失败，请检查用户名和密码'
    
    // 详细错误分析和用户友好提示
    if (err.message?.includes('网络') || err.message?.includes('fetch') || err.message?.includes('连接')) {
      errorMessage = '网络连接失败，请检查后端服务是否启动'
      addLog('error', '网络错误分析', {
        error: err.message,
        solutions: [
          '确认后端服务已启动 (python main.py)',
          '检查端口8001是否被占用',
          '验证API地址配置是否正确'
        ]
      })
    } else if (err.message?.includes('401') || err.message?.includes('认证') || err.message?.includes('unauthorized')) {
      errorMessage = '用户名或密码错误，请检查登录凭据'
      addLog('error', '认证错误分析', {
        error: err.message,
        suggestions: [
          '确认用户名拼写正确',
          '确认密码正确',
          '尝试使用快速登录按钮'
        ]
      })
    } else if (err.message?.includes('403') || err.message?.includes('权限')) {
      errorMessage = '权限不足，该账号可能不是管理员账号'
      addLog('error', '权限错误分析', {
        error: err.message,
        suggestion: '请使用具有管理员权限的账号登录'
      })
    } else if (err.message?.includes('500') || err.message?.includes('服务器')) {
      errorMessage = '服务器内部错误，请稍后重试'
      addLog('error', '服务器错误分析', {
        error: err.message,
        solutions: [
          '检查后端服务日志',
          '确认数据库连接正常',
          '重启后端服务'
        ]
      })
    } else if (err.message?.includes('timeout') || err.message?.includes('超时')) {
      errorMessage = '请求超时，服务器响应缓慢'
      addLog('error', '超时错误分析', {
        error: err.message,
        suggestion: '请稍后重试或检查网络连接'
      })
    } else {
      // 使用原始错误信息
      errorMessage = err.message || errorMessage
    }
    
    error.value = errorMessage
    
    addLog('error', '管理员登录失败', {
      error: errorMessage,
      originalError: err.message,
      stack: err.stack,
      response: err.response?.data
    })
    
    console.error('管理员登录失败:', err)
  } finally {
    loading.value = false
    addLog('info', '登录流程结束')
  }
}

// 页面加载时自动检查系统状态
onMounted(() => {
  addLog('info', '管理员登录页面已加载')
  addLog('info', '当前URL: ' + window.location.href)
  addLog('info', '后端API地址: /api/v1/')
  
  // 自动检查系统状态
  setTimeout(() => {
    checkSystemStatus()
  }, 1000)
})
</script>

<style scoped>
.admin-login-page {
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

.admin-login-container {
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

.login-card {
  width: 100%;
  max-width: 500px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 40px;
  max-height: 90vh;
  overflow-y: auto;
}

.login-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.3s ease;
  box-sizing: border-box;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.login-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(45deg, #409EFF, #67C23A);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.error-message {
  background: #fee;
  color: #c53030;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
  font-size: 14px;
}

.debug-logs {
  margin: 20px 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.debug-logs h3 {
  margin: 0 0 15px 0;
  color: #495057;
  font-size: 16px;
}

.log-container {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 10px;
}

.log-entry {
  padding: 8px;
  margin-bottom: 5px;
  border-radius: 4px;
  font-size: 12px;
  border-left: 3px solid;
}

.log-entry.info {
  background: #e3f2fd;
  border-color: #2196f3;
  color: #1565c0;
}

.log-entry.success {
  background: #e8f5e8;
  border-color: #4caf50;
  color: #2e7d32;
}

.log-entry.error {
  background: #ffebee;
  border-color: #f44336;
  color: #c62828;
}

.log-entry.warning {
  background: #fff3e0;
  border-color: #ff9800;
  color: #ef6c00;
}

.log-time {
  font-weight: bold;
  margin-right: 10px;
}

.log-data {
  margin-top: 5px;
  padding: 5px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
  font-size: 10px;
  overflow-x: auto;
}

.clear-logs-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.quick-login-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  margin-left: 10px;
}

.status-check-btn {
  background: #17a2b8;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  margin-top: 10px;
}

.system-status {
  margin-top: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.system-status h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #495057;
}

.status-result {
  margin-top: 10px;
}

.status-item {
  padding: 5px;
  margin: 5px 0;
  border-radius: 4px;
  font-size: 12px;
}

.status-item.success {
  background: #d4edda;
  color: #155724;
}

.status-item.error {
  background: #f8d7da;
  color: #721c24;
}

.login-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e1e5e9;
  font-size: 12px;
  color: #666;
}

.login-footer code {
  background: #f1f3f4;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  color: #333;
}

.security-note {
  color: #e53e3e !important;
  font-weight: 500;
  margin-top: 10px !important;
}

.admin-accounts {
  margin-bottom: 20px;
}

.account-item {
  margin-bottom: 10px;
}

.account-item strong {
  font-weight: 600;
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
  .admin-login-container {
    padding: 20px 10px;
  }
  
  .platform-title {
    font-size: 28px;
  }
  
  .platform-subtitle {
    font-size: 16px;
  }
  
  .login-card {
    padding: 30px 20px;
  }
}
</style> 