import api from './api';

export interface ContentTag {
  category: string;
  name: string;
  confidence?: number;
}

export interface Content {
  id: string;
  title: string;
  content: string;
  type: string;
  tags: ContentTag[];
  publish_time: string;
  author: string;
  is_published: boolean;
  relevance_score?: number;
  view_count?: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
}

export interface ContentListParams {
  page?: number;
  page_size?: number;
  tag_filters?: string[];
  content_type?: string;
  sort_by?: 'latest' | 'relevance' | 'popularity';
  search_keyword?: string;
}

export interface ContentListResponse {
  items: Content[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface UserBehavior {
  user_id: string;
  action: 'view' | 'click' | 'like' | 'share';
  content_id: string;
  timestamp: string;
  duration?: number; // 浏览时长（秒）
}

class ContentService {
  async getContentList(params: ContentListParams = {}): Promise<ContentListResponse> {
    try {
      console.log('📋 开始获取内容列表...', params);
      
      const response = await api.get<ApiResponse<ContentListResponse>>('/content', {
        params: {
          page: params.page || 1,
          page_size: params.page_size || 10,
          tag_filters: params.tag_filters?.join(','),
          content_type: params.content_type,
          sort_by: params.sort_by || 'latest',
          search_keyword: params.search_keyword
        }
      });

      console.log('✅ 内容列表API响应:', response);

      // 检查响应结构
      if (!response || !response.data) {
        console.warn('⚠️ API响应无效，使用默认数据');
        return {
          items: [],
          total: 0,
          page: params.page || 1,
          page_size: params.page_size || 10,
          has_next: false
        };
      }

      // 检查嵌套的data属性
      const result = response.data.data || response.data;
      
      if (!result) {
        console.warn('⚠️ 响应数据为空，使用默认数据');
        return {
          items: [],
          total: 0,
          page: params.page || 1,
          page_size: params.page_size || 10,
          has_next: false
        };
      }

      console.log('📊 成功获取内容列表:', result.items?.length || 0, '条');
      
      return {
        items: result.items || [],
        total: result.total || 0,
        page: result.page || (params.page || 1),
        page_size: result.page_size || (params.page_size || 10),
        has_next: result.has_next || false
      };

    } catch (error) {
      console.error('❌ Failed to fetch content list:', error);
      
      // 返回默认的空响应而不是抛出错误
      return {
        items: [],
        total: 0,
        page: params.page || 1,
        page_size: params.page_size || 10,
        has_next: false
      };
    }
  }

  async getContentById(id: string): Promise<Content | null> {
    try {
      const response = await api.get<ApiResponse<Content>>(`/content/${id}`);
      return response.data.data;
    } catch (error) {
      console.error('Failed to fetch content:', error);
      return null;
    }
  }

  async getPersonalizedContent(userId: string, params: ContentListParams = {}): Promise<ContentListResponse> {
    try {
      const response = await api.get<ApiResponse<ContentListResponse>>(`/users/${userId}/recommendations`, {
        params: {
          page: params.page || 1,
          page_size: params.page_size || 10,
          tag_filters: params.tag_filters?.join(','),
          content_type: params.content_type
        }
      });
      return response.data.data || {
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
        has_next: false
      };
    } catch (error) {
      console.error('Failed to fetch personalized content:', error);
      return {
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
        has_next: false
      };
    }
  }

  async recordUserBehavior(behavior: UserBehavior): Promise<void> {
    try {
      await api.post('/user-behavior', behavior);
    } catch (error) {
      console.error('Failed to record user behavior:', error);
    }
  }

  async getAvailableTags(): Promise<string[]> {
    try {
      console.log('🏷️ 开始获取可用标签...');
      const response = await api.get('/content/tags');
      console.log('📊 标签API响应:', response);

      // 检查响应结构
      if (!response || !response.data) {
        console.warn('⚠️ 标签API响应无效，使用默认标签');
        return this.getDefaultTags();
      }

      // 检查是否是包装的ApiResponse格式
      if (response.data.data) {
        const tags = Array.isArray(response.data.data) ? response.data.data : [];
        console.log('✅ 获取包装格式的标签:', tags.length);
        return tags.length > 0 ? tags : this.getDefaultTags();
      }

      // 检查是否是直接的数组格式
      if (Array.isArray(response.data)) {
        console.log('✅ 获取直接格式的标签:', response.data.length);
        return response.data.length > 0 ? response.data : this.getDefaultTags();
      }

      console.warn('⚠️ 标签API响应结构异常，使用默认标签');
      return this.getDefaultTags();
      
    } catch (error) {
      console.error('❌ Failed to fetch available tags:', error);
      return this.getDefaultTags();
    }
  }

  private getDefaultTags(): string[] {
    return [
      '天然气',
      'LNG',
      '华东地区',
      '华北地区',
      '华南地区',
      '市场动态',
      '价格变化',
      '政策解读',
      '基础设施',
      '清洁能源',
      '能源转型',
      '交易公告'
    ];
  }

  async createContent(content: Partial<Content>): Promise<Content> {
    const response = await api.post<ApiResponse<Content>>('/content', content);
    return response.data.data;
  }

  async updateContent(id: string, content: Partial<Content>): Promise<Content> {
    const response = await api.put<ApiResponse<Content>>(`/content/${id}`, content);
    return response.data.data;
  }
}

export const contentService = new ContentService(); 