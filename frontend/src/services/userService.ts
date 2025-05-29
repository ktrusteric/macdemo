import api from './api';

export interface UserTag {
  category: string;
  name: string;
  weight: number;
  source: string;
  created_at: string;
}

export interface UserTags {
  user_id: string;
  tags: UserTag[];
  updated_at: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
}

class UserService {
  async getUserTags(userId: string): Promise<UserTags | null> {
    try {
      const response = await api.get<ApiResponse<UserTags>>(`/users/${userId}/tags`);
      return response.data.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async updateUserTags(userId: string, tags: UserTag[]): Promise<UserTags> {
    const response = await api.put<ApiResponse<UserTags>>(`/users/${userId}/tags`, { tags });
    return response.data.data;
  }

  async getUserProfile(userId: string) {
    const response = await api.get(`/users/${userId}/profile`);
    return response;
  }

  async initializeUserTags(userId: string, region: string = '全国'): Promise<ApiResponse<UserTags>> {
    try {
      const response = await api.post<any, ApiResponse<UserTags>>(`/users/${userId}/initialize`, null, {
        params: { region }
      });
      return response;
    } catch (error) {
      console.error('Failed to initialize user tags:', error);
      throw error;
    }
  }
}

export const userService = new UserService(); 