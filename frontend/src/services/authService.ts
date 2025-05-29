import api from './api';
import type { User, UserRegistration, UserLogin } from '../types/user';

class AuthService {
  async register(userData: UserRegistration): Promise<User> {
    try {
      const { confirm_password, initial_regions, initial_energy_types, ...userBasic } = userData;
      
      const response = await api.post<any, User>('/users/register', userBasic, {
        params: {
          regions: initial_regions,
          energy_types: initial_energy_types
        }
      });
      
      return response;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  async login(credentials: UserLogin): Promise<{ user: User; access_token: string }> {
    try {
      const response = await api.post<any, { user: User; access_token: string; token_type: string }>(
        '/users/login',
        credentials
      );
      
      // 保存令牌到本地存储
      localStorage.setItem('token', response.access_token);
      
      return {
        user: response.user,
        access_token: response.access_token
      };
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  logout(): void {
    localStorage.removeItem('token');
  }

  getCurrentUser(): User | null {
    const userJson = localStorage.getItem('user');
    if (userJson) {
      return JSON.parse(userJson);
    }
    return null;
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }
}

export const authService = new AuthService();