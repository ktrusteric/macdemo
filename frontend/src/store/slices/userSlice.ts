import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { UserTags } from '../../types';
import { userService } from '../../services/userService';

interface UserState {
  currentUserId: string | null;
  userTags: UserTags | null;
  loading: boolean;
  error: string | null;
  isDemoMode: boolean;
}

const initialState: UserState = {
  currentUserId: null,
  userTags: null,
  loading: false,
  error: null,
  isDemoMode: false,
};

// 获取用户标签
export const fetchUserTags = createAsyncThunk(
  'user/fetchTags',
  async (userId: string) => {
    const response = await userService.getUserTags(userId);
    return response;
  }
);

// 更新用户标签
export const updateUserTags = createAsyncThunk(
  'user/updateTags',
  async ({ userId, tags }: { userId: string; tags: any[] }) => {
    const response = await userService.updateUserTags(userId, tags);
    return response;
  }
);

// 初始化用户标签
export const initializeUserTags = createAsyncThunk(
  'user/initializeTags',
  async ({ userId, region }: { userId: string; region?: string }) => {
    const response = await userService.initializeUserTags(userId, region);
    return response.data;
  }
);

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setCurrentUserId: (state, action: PayloadAction<string>) => {
      state.currentUserId = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearUserData: (state) => {
      state.currentUserId = null;
      state.userTags = null;
      state.error = null;
      state.isDemoMode = false;
    },
    // 从认证状态同步用户ID
    syncUserIdFromAuth: (state, action: PayloadAction<string | null>) => {
      if (action.payload) {
        state.currentUserId = action.payload;
        state.isDemoMode = false;
      }
    },
    // 设置演示用户模式
    setDemoUser: (state, action: PayloadAction<string>) => {
      state.currentUserId = action.payload;
      state.isDemoMode = true;
    },
    // 切换到演示模式
    enableDemoMode: (state) => {
      state.isDemoMode = true;
      if (!state.currentUserId) {
        state.currentUserId = 'user001'; // 默认演示用户
      }
    },
    // 退出演示模式
    disableDemoMode: (state) => {
      state.isDemoMode = false;
      state.currentUserId = null;
      state.userTags = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // fetchUserTags
      .addCase(fetchUserTags.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserTags.fulfilled, (state, action) => {
        state.loading = false;
        state.userTags = action.payload as any;
      })
      .addCase(fetchUserTags.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch user tags';
      })
      // updateUserTags
      .addCase(updateUserTags.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateUserTags.fulfilled, (state, action) => {
        state.loading = false;
        state.userTags = action.payload as any;
      })
      .addCase(updateUserTags.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update user tags';
      })
      // initializeUserTags
      .addCase(initializeUserTags.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(initializeUserTags.fulfilled, (state, action) => {
        state.loading = false;
        state.userTags = action.payload as any;
      })
      .addCase(initializeUserTags.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to initialize user tags';
      });
  },
});

export const { 
  setCurrentUserId, 
  clearError,
  clearUserData,
  syncUserIdFromAuth,
  setDemoUser,
  enableDemoMode,
  disableDemoMode
} = userSlice.actions;
export default userSlice.reducer;