import axios from 'axios';
import type {
  AIAssistantConfig,
  ChatRequest,
  ChatResponse,
  ChatSession,
  ChatHistoryQuery,
  ChatHistoryResponse
} from '../types/ai-chat';

const API_BASE_URL = '/api/v1/ai-chat';

// 创建axios实例
const aiChatApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30秒超时，因为AI响应可能较慢
});

// 请求拦截器
aiChatApi.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
aiChatApi.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('AI Chat API Error:', error);
    return Promise.reject(error);
  }
);

export const aiChatService = {
  // 获取AI助手配置
  async getAssistants(): Promise<AIAssistantConfig> {
    const response = await aiChatApi.get('/assistants');
    return response.data;
  },

  // 发送聊天消息
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await aiChatApi.post('/chat', request);
    return response.data;
  },

  // 获取会话历史
  async getSessionHistory(sessionId: string): Promise<ChatSession | null> {
    const response = await aiChatApi.get(`/sessions/${sessionId}`);
    return response.data;
  },

  // 搜索聊天历史
  async searchChatHistory(query: ChatHistoryQuery): Promise<ChatHistoryResponse> {
    const response = await aiChatApi.post('/history/search', query);
    return response.data;
  },

  // 获取统计信息
  async getStatistics(): Promise<any> {
    const response = await aiChatApi.get('/statistics');
    return response.data;
  },

  // 管理员API - 获取所有会话
  async adminGetAllSessions(params: {
    page?: number;
    page_size?: number;
    assistant_type?: string;
    keyword?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<ChatHistoryResponse> {
    const response = await aiChatApi.get('/admin/sessions', { params });
    return response.data;
  },

  // 管理员API - 获取详细统计
  async adminGetDetailedStatistics(): Promise<any> {
    const response = await aiChatApi.get('/admin/statistics/detailed');
    return response.data;
  },

  // 删除单个会话
  async deleteSession(sessionId: string): Promise<{ success: boolean; message: string }> {
    const response = await aiChatApi.delete(`/sessions/${sessionId}`);
    return response.data;
  },

  // 批量删除会话
  async batchDeleteSessions(sessionIds: string[]): Promise<{ 
    success: boolean; 
    message: string; 
    deleted_count: number; 
    total_requested: number 
  }> {
    const response = await aiChatApi.delete('/sessions/batch', { 
      data: { session_ids: sessionIds } 
    });
    return response.data;
  },

  // 保存用户消息
  async saveUserMessage(sessionId: string, message: string, userId?: string, userInfo?: any): Promise<{ success: boolean }> {
    const response = await aiChatApi.post(`/sessions/${sessionId}/save-user-message`, {
      message,
      user_id: userId,
      user_info: userInfo
    });
    return response.data;
  },

  // 保存助手消息
  async saveAssistantMessage(sessionId: string, message: string): Promise<{ success: boolean }> {
    const response = await aiChatApi.post(`/sessions/${sessionId}/save-message`, {
      message: message
    });
    return response.data;
  },

  // 创建带用户信息的会话
  async createSessionWithUser(sessionId: string, assistantType: string, userId?: string, userInfo?: any): Promise<{ success: boolean; session: any }> {
    const response = await aiChatApi.post('/sessions/create-with-user', {
      session_id: sessionId,
      assistant_type: assistantType,
      user_id: userId,
      user_info: userInfo
    });
    return response.data;
  }
}; 