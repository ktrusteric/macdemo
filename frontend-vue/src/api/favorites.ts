import api from './request'

const API_BASE_URL = '/api/v1'

export interface FavoriteRequest {
  content_id: string
}

export interface FavoriteResponse {
  success: boolean
  message: string
  learned_tags?: {
    energy_types: string[]
    regions: string[]
    business_fields: string[]
  }
  total_favorites: number
}

export interface FavoriteItem {
  _id: string
  content_id: string
  favorited_at: string
  title: string
  publish_date: string
  source: string
  type: string
  basic_info_tags: string[]
  region_tags: string[]
  energy_type_tags: string[]
  business_field_tags: string[]
  beneficiary_tags: string[]
  policy_measure_tags: string[]
  importance_tags: string[]
  link?: string
}

export interface UserBehaviorStats {
  user_id: string
  total_favorites: number
  energy_type_interests: Record<string, number>
  region_interests: Record<string, number>
  last_activity?: string
}

class FavoritesAPI {
  // 添加收藏
  async addFavorite(contentId: string): Promise<FavoriteResponse> {
    const response = await api.post(`/favorites/add`, {
      content_id: contentId
    })
    return response.data
  }

  // 取消收藏
  async removeFavorite(contentId: string): Promise<FavoriteResponse> {
    const response = await api.delete(`/favorites/remove/${contentId}`)
    return response.data
  }

  // 获取收藏列表
  async getFavoritesList(limit: number = 50): Promise<FavoriteItem[]> {
    const response = await api.get(`/favorites/list`, {
      params: { limit }
    })
    return response.data
  }

  // 搜索收藏文章
  async searchFavorites(query: string, limit: number = 50): Promise<FavoriteItem[]> {
    const response = await api.get(`/favorites/search`, {
      params: { query, limit }
    })
    return response.data
  }

  // 检查收藏状态
  async checkFavoriteStatus(contentId: string): Promise<boolean> {
    const response = await api.get(`/favorites/check/${contentId}`)
    return response.data.is_favorited
  }

  // 获取收藏总数
  async getFavoritesCount(): Promise<number> {
    const response = await api.get(`/favorites/count`)
    return response.data.count
  }

  // 获取用户行为统计
  async getUserBehaviorStats(): Promise<UserBehaviorStats> {
    const response = await api.get(`/favorites/stats`)
    return response.data
  }
}

export const favoritesAPI = new FavoritesAPI() 