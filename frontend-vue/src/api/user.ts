import api from './request'

export const login = async (email: string, password: string) => {
  return api.post('/users/login', { email, password })
}

export const register = async (email: string, password: string, username?: string) => {
  return api.post('/users/register', { email, password, username })
}

export const getUserTags = async (userId: string) => {
  return api.get(`/users/${userId}/tags`)
}

export const getUserRecommendations = async (userId: string) => {
  return api.get(`/users/${userId}/recommendations`)
}

// 获取交易公告
export const getAnnouncements = async (content_type: string = 'ANNOUNCEMENT', page: number = 1, pageSize: number = 10) => {
  return api.get('/content', {
    params: {
      page,
      page_size: pageSize,
      content_type
    }
  })
}

// 获取内容统计
export const getContentStats = async () => {
  return api.get('/content/stats')
} 