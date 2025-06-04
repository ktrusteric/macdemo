import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/request'

// 管理员用户信息接口
interface AdminUser {
  id: string
  email: string
  username: string
  role: string
  is_active: boolean
  created_at: string
  has_initial_tags: boolean
  access_features: string[]
  register_city?: string
}

// 管理员登录响应接口
interface AdminLoginResponse {
  access_token: string
  token_type: string
  admin: AdminUser
  permissions: string[]
}

// 文章接口
interface Article {
  id: string
  title: string
  content: string
  type: string
  source: string
  publish_time: string
  link?: string
  basic_info_tags: string[]
  region_tags: string[]
  energy_type_tags: string[]
  business_field_tags: string[]
  beneficiary_tags: string[]
  policy_measure_tags: string[]
  importance_tags: string[]
  created_at: string
  updated_at: string
  view_count: number
}

// 文章列表响应接口
interface ArticleListResponse {
  items: Article[]
  total: number
  page: number
  page_size: number
  has_next: boolean
}

// 批量导入响应接口
interface BatchImportResponse {
  success: boolean
  total_articles: number
  imported_count: number
  updated_count: number
  failed_count: number
  failed_articles: Array<{
    index: number
    title: string
    error: string
  }>
  message: string
}

// 统计数据接口
interface AdminStats {
  articles: {
    total: number
    by_type: Record<string, number>
  }
  users: {
    total: number
    admins: number
    regular: number
  }
}

export const useAdminStore = defineStore('admin', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('admin_token'))
  const adminInfo = ref<AdminUser | null>(
    localStorage.getItem('admin_info') 
      ? JSON.parse(localStorage.getItem('admin_info')!) 
      : null
  )
  const permissions = ref<string[]>(
    localStorage.getItem('admin_permissions')
      ? JSON.parse(localStorage.getItem('admin_permissions')!)
      : []
  )

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!adminInfo.value)
  const isAdmin = computed(() => adminInfo.value?.role === 'admin')

  // 登录
  const login = async (username: string, password: string) => {
    try {
      const response = await api.post<AdminLoginResponse>('/admin/login', {
        username,
        password
      })

      const { access_token, admin, permissions: userPermissions } = response.data

      // 保存到状态和本地存储
      token.value = access_token
      adminInfo.value = admin
      permissions.value = userPermissions

      localStorage.setItem('admin_token', access_token)
      localStorage.setItem('admin_info', JSON.stringify(admin))
      localStorage.setItem('admin_permissions', JSON.stringify(userPermissions))

      console.log('✅ 管理员登录成功，token已保存:', access_token.substring(0, 20) + '...')

      return response.data
    } catch (error: any) {
      console.error('管理员登录失败:', error)
      throw new Error(error.response?.data?.detail || '登录失败')
    }
  }

  // 登出
  const logout = () => {
    token.value = null
    adminInfo.value = null
    permissions.value = []

    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_info')
    localStorage.removeItem('admin_permissions')
  }

  // 检查权限
  const hasPermission = (permission: string) => {
    return permissions.value.includes(permission)
  }

  // 获取文章列表
  const getArticles = async (params: {
    page?: number
    page_size?: number
    search?: string
    type?: string
    energy_type?: string
    tag_search?: string
  } = {}) => {
    try {
      // 映射前端参数到后端期望的参数
      const apiParams = {
        page: params.page || 1,
        page_size: params.page_size || 20,
        search_keyword: params.search,
        content_type: params.type,
        energy_type: params.energy_type,
        tag_search: params.tag_search
      }
      
      const response = await api.get('/admin/articles', {
        params: apiParams
      })
      
      // 转换后端数据结构为前端期望的格式
      const data = response.data
      return {
        articles: data.items.map((item: any) => ({
          ...item,
          publish_date: item.publish_time // 映射时间字段
        })),
        total: data.total,
        page: data.page,
        page_size: data.page_size,
        total_pages: Math.ceil(data.total / data.page_size), // 计算总页数
        has_next: data.has_next
      }
    } catch (error: any) {
      console.error('获取文章列表失败:', error)
      throw new Error(error.response?.data?.detail || '获取文章列表失败')
    }
  }

  // 创建文章
  const createArticle = async (articleData: {
    title: string
    content: string
    type: string
    source?: string
    publish_time?: string
    link?: string
    basic_info_tags?: string[]
    region_tags?: string[]
    energy_type_tags?: string[]
    business_field_tags?: string[]
    beneficiary_tags?: string[]
    policy_measure_tags?: string[]
    importance_tags?: string[]
  }) => {
    try {
      const response = await api.post('/admin/articles', articleData)
      return response.data
    } catch (error: any) {
      console.error('创建文章失败:', error)
      throw new Error(error.response?.data?.detail || '创建文章失败')
    }
  }

  // 更新文章
  const updateArticle = async (articleId: string, updateData: any) => {
    try {
      const response = await api.put(`/admin/articles/${articleId}`, updateData)
      return response.data
    } catch (error: any) {
      console.error('更新文章失败:', error)
      throw new Error(error.response?.data?.detail || '更新文章失败')
    }
  }

  // 删除文章
  const deleteArticle = async (articleId: string) => {
    try {
      const response = await api.delete(`/admin/articles/${articleId}`)
      return response.data
    } catch (error: any) {
      console.error('删除文章失败:', error)
      throw new Error(error.response?.data?.detail || '删除文章失败')
    }
  }

  // 获取文章详情
  const getArticleDetail = async (articleId: string) => {
    try {
      const response = await api.get(`/admin/articles/${articleId}`)
      return response.data
    } catch (error: any) {
      console.error('获取文章详情失败:', error)
      throw new Error(error.response?.data?.detail || '获取文章详情失败')
    }
  }

  // 批量导入文章
  const batchImportArticles = async (articles: any[], options: {
    auto_parse_tags?: boolean
    overwrite_existing?: boolean
  } = {}) => {
    try {
      const response = await api.post('/admin/articles/batch-import', {
        articles,
        auto_parse_tags: options.auto_parse_tags ?? true,
        overwrite_existing: options.overwrite_existing ?? false
      })
      return response.data
    } catch (error: any) {
      console.error('批量导入文章失败:', error)
      throw new Error(error.response?.data?.detail || '批量导入文章失败')
    }
  }

  // 从JSON文件导入
  const importFromJsonFile = async (file: File, options: {
    auto_parse_tags?: boolean
    overwrite_existing?: boolean
  } = {}) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post(`/admin/articles/import-json-file?auto_parse_tags=${options.auto_parse_tags ?? true}&overwrite_existing=${options.overwrite_existing ?? false}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error: any) {
      console.error('从JSON文件导入失败:', error)
      throw new Error(error.response?.data?.detail || '从JSON文件导入失败')
    }
  }

  // 获取统计数据
  const getStats = async () => {
    try {
      const response = await api.get('/admin/stats')
      return response.data
    } catch (error: any) {
      console.error('获取统计数据失败:', error)
      throw new Error(error.response?.data?.detail || '获取统计数据失败')
    }
  }

  // 获取用户列表
  const getUsers = async (params: {
    page?: number
    page_size?: number
    search?: string
  } = {}) => {
    try {
      const response = await api.get('/admin/users', {
        params: {
          page: params.page || 1,
          page_size: params.page_size || 50,
          search: params.search
        }
      })
      return response.data
    } catch (error: any) {
      console.error('获取用户列表失败:', error)
      throw new Error(error.response?.data?.detail || '获取用户列表失败')
    }
  }

  // 获取用户标签
  const getUserTags = async (userId: string) => {
    try {
      const response = await api.get(`/users/${userId}/tags`)
      return response.data
    } catch (error: any) {
      console.error('获取用户标签失败:', error)
      throw new Error(error.response?.data?.detail || '获取用户标签失败')
    }
  }

  // 更新用户标签
  const updateUserTags = async (userId: string, tagsData: any) => {
    try {
      const response = await api.put(`/users/${userId}/tags`, tagsData)
      return response.data
    } catch (error: any) {
      console.error('更新用户标签失败:', error)
      throw new Error(error.response?.data?.detail || '更新用户标签失败')
    }
  }

  return {
    // 状态
    token,
    adminInfo,
    permissions,
    // 计算属性
    isLoggedIn,
    isAdmin,
    // 方法
    login,
    logout,
    hasPermission,
    getArticles,
    createArticle,
    updateArticle,
    deleteArticle,
    getArticleDetail,
    batchImportArticles,
    importFromJsonFile,
    getStats,
    getUsers,
    getUserTags,
    updateUserTags
  }
}) 