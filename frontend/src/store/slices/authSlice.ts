import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { User, UserRegistration, UserLogin } from '../../types/user';
import { authService } from '../../services/authService';

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

// 从localStorage获取初始状态
const getInitialState = (): AuthState => {
  const token = localStorage.getItem('token');
  const userStr = localStorage.getItem('user');
  
  let user: User | null = null;
  try {
    if (userStr) {
      user = JSON.parse(userStr);
    }
  } catch (error) {
    console.warn('解析localStorage中的用户信息失败:', error);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
  }

  return {
    user,
    token,
    loading: false,
    error: null,
    isAuthenticated: !!(token && user)
  };
};

const initialState: AuthState = getInitialState();

export const registerUser = createAsyncThunk(
  'auth/register',
  async (userData: UserRegistration) => {
    const response = await authService.register(userData);
    return response;
  }
);

export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials: UserLogin, { rejectWithValue }) => {
    try {
      const response = await authService.login(credentials);
      localStorage.setItem('user', JSON.stringify(response.user));
      localStorage.setItem('token', response.access_token);
      return response;
    } catch (error: any) {
      // 提取具体错误信息
      let errorMessage = '登录失败，请稍后重试';
      
      if (error.code === 'ECONNABORTED' || error.message?.includes('超时')) {
        errorMessage = '网络连接超时，请检查网络连接后重试';
      } else if (error.code === 'ECONNREFUSED') {
        errorMessage = '无法连接到服务器，请检查后端服务是否运行';
      } else if (error.response?.status === 401) {
        errorMessage = '邮箱或密码错误，请检查后重试';
      } else if (error.response?.status === 422) {
        errorMessage = '请求数据格式错误，请检查输入';
      } else if (error.response?.status >= 500) {
        errorMessage = '服务器错误，请稍后重试';
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      return rejectWithValue(errorMessage);
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      authService.logout();
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      localStorage.removeItem('user');
      localStorage.removeItem('token');
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // 注册
      .addCase(registerUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '注册失败';
      })
      // 登录
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.access_token;
        state.isAuthenticated = true;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string || action.error.message || '登录失败';
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;