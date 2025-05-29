import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Content } from '../../types';
import { ContentType } from '../../types';
import { contentService } from '../../services/contentService';
import { recommendationService } from '../../services/recommendationService';

interface ContentState {
  contents: Content[];
  recommendations: Content[];
  trending: Content[];
  currentContent: Content | null;
  loading: boolean;
  error: string | null;
  filters: {
    contentType?: ContentType;
    tags?: string[];
  };
}

const initialState: ContentState = {
  contents: [],
  recommendations: [],
  trending: [],
  currentContent: null,
  loading: false,
  error: null,
  filters: {},
};

// 异步actions
export const fetchContents = createAsyncThunk(
  'content/fetchList',
  async (params: { content_type?: ContentType; tags?: string[]; skip?: number; limit?: number }) => {
    return await contentService.getContentList(params);
  }
);

export const fetchContentDetail = createAsyncThunk(
  'content/fetchContentDetail',
  async (contentId: string) => {
    return await contentService.getContentById(contentId);
  }
);

export const fetchUserRecommendations = createAsyncThunk(
  'content/fetchUserRecommendations', 
  async ({ userId, limit }: { userId: string; limit: number }) => {
    return await recommendationService.getRecommendations(userId, limit);
  }
);

export const fetchTrendingContent = createAsyncThunk(
  'content/fetchTrendingContent',
  async ({ skip, limit }: { skip: number; limit: number }) => {
    return await contentService.getContentList({ 
      page: Math.floor(skip / limit) + 1, 
      page_size: limit, 
      sort_by: 'popularity' 
    });
  }
);

const contentSlice = createSlice({
  name: 'content',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<ContentState['filters']>) => {
      state.filters = action.payload;
    },
    clearCurrentContent: (state) => {
      state.currentContent = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // fetchContents
      .addCase(fetchContents.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchContents.fulfilled, (state, action) => {
        state.loading = false;
        state.contents = action.payload.items as any;
      })
      .addCase(fetchContents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch content list';
      })
      // fetchContentDetail
      .addCase(fetchContentDetail.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchContentDetail.fulfilled, (state, action) => {
        state.loading = false;
        state.currentContent = action.payload as any;
      })
      .addCase(fetchContentDetail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch content detail';
      })
      // fetchUserRecommendations
      .addCase(fetchUserRecommendations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserRecommendations.fulfilled, (state, action) => {
        state.loading = false;
        state.recommendations = action.payload.map(item => ({
          ...item,
          content: '',
          source: 'recommendation',
          is_published: true,
          created_at: item.publish_time,
          basic_info_tags: [],
          region_tags: [],
          energy_type_tags: [],
          business_field_tags: [],
          beneficiary_tags: [],
          policy_measure_tags: [],
          importance_tags: item.tags || [],
          type: ContentType.NEWS
        })) as any;
      })
      .addCase(fetchUserRecommendations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch recommendations';
      })
      // fetchTrendingContent
      .addCase(fetchTrendingContent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTrendingContent.fulfilled, (state, action) => {
        state.loading = false;
        state.trending = action.payload.items as any;
      })
      .addCase(fetchTrendingContent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch trending content';
      });
  },
});

export const { setFilters, clearCurrentContent, clearError } = contentSlice.actions;
export default contentSlice.reducer; 