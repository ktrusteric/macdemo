import api from './api';

export interface RecommendedContent {
  id: string;
  title: string;
  type: string;
  publish_time: string;
  tags: string[];
  relevance_score?: number;
  view_count?: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
}

export interface ContentListResponse {
  items: RecommendedContent[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

class RecommendationService {
  async getRecommendations(userId: string, limit: number = 10): Promise<RecommendedContent[]> {
    try {
      console.log('🎯 开始获取推荐内容...', { userId, limit });
      
      const response = await api.get(`/users/${userId}/recommendations`, {
        params: {
          page: 1,
          page_size: limit
        }
      });

      console.log('📊 推荐API响应:', response);

      // 检查响应结构 - 推荐API直接返回ContentListResponse
      if (!response || !response.data) {
        console.warn('⚠️ 推荐API响应无效');
        return [];
      }

      // 检查是否是包装的ApiResponse
      if (response.data.data && response.data.data.items) {
        console.log('✅ 获取包装格式的推荐内容:', response.data.data.items.length);
        return response.data.data.items || [];
      }
      
      // 检查是否是直接的ContentListResponse
      if (response.data.items) {
        console.log('✅ 获取直接格式的推荐内容:', response.data.items.length);
        return response.data.items || [];
      }

      console.warn('⚠️ 推荐API响应结构异常，返回空数组');
      return [];
      
    } catch (error) {
      console.error('❌ Failed to fetch recommendations:', error);
      return [];
    }
  }

  async getSimilarContent(userId: string, contentId: string, limit: number = 5): Promise<RecommendedContent[]> {
    try {
      const response = await api.get(`/users/${userId}/similar-content/${contentId}`, {
        params: { limit }
      });
      
      // 处理相似内容的响应结构
      if (response?.data?.data) {
        return response.data.data || [];
      }
      
      return response?.data || [];
    } catch (error) {
      console.error('Failed to fetch similar content:', error);
      return [];
    }
  }

  async getUserInsights(userId: string) {
    try {
      const response = await api.get(`/users/${userId}/insights`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user insights:', error);
      return null;
    }
  }
}

export const recommendationService = new RecommendationService(); 