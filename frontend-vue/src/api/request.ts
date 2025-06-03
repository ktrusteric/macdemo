import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8001/api/v1',
  timeout: 10000,
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 检查当前路径，优先使用对应的token
    const currentPath = window.location.pathname
    
    if (currentPath.startsWith('/admin')) {
      // 管理员路由，使用管理员token
      const adminToken = localStorage.getItem('admin_token')
      if (adminToken) {
        config.headers.Authorization = `Bearer ${adminToken}`
      }
    } else {
      // 普通用户路由，使用普通用户token
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      const currentPath = window.location.pathname
      
      if (currentPath.startsWith('/admin')) {
        // 管理员页面401错误，清除管理员token并跳转到管理员登录
        localStorage.removeItem('admin_token')
        localStorage.removeItem('admin_info')
        window.location.href = '/admin/login'
      } else {
        // 普通用户页面401错误，清除用户token并跳转到用户登录
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        window.location.href = '/login'
      }
    }
    
    const message = error.response?.data?.message || error.message || '请求失败'
    ElMessage.error(message)
    
    return Promise.reject(error)
  }
)

export default api 