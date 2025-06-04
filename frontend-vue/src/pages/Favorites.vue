<template>
  <div class="dashboard-container">
    <!-- 页面头部 -->
    <div class="header-section">
      <h1 class="page-title">
        <el-icon class="title-icon"><Star /></el-icon>
        我的收藏
      </h1>
      <p class="page-subtitle">管理您收藏的能源资讯文章</p>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="8">
          <el-input
            v-model="searchQuery"
            placeholder="搜索收藏的文章标题、来源、标签..."
            size="large"
            clearable
            @input="handleSearch"
            @clear="handleSearchClear"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-button 
            type="primary" 
            size="large" 
            @click="performSearch"
            :loading="loading"
            style="width: 100%"
          >
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button 
            size="large" 
            @click="resetSearch"
            style="width: 100%"
          >
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-col>
        <el-col :span="8">
          <div class="search-stats">
            <span class="search-result-text">
              <template v-if="searchQuery">
                搜索到 <strong>{{ favorites.length }}</strong> 篇文章
              </template>
              <template v-else>
                共 <strong>{{ favorites.length }}</strong> 篇收藏
              </template>
            </span>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计概览 -->
    <el-row :gutter="20" class="stats-section" v-if="!loading">
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="总收藏" :value="favorites.length" />
          <div class="stat-icon">💖</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="能源类型" :value="Object.keys(behaviorStats.energy_type_interests || {}).length" />
          <div class="stat-icon">⚡</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="关注地区" :value="Object.keys(behaviorStats.region_interests || {}).length" />
          <div class="stat-icon">🌍</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="最近收藏" :value="lastActivityText" />
          <div class="stat-icon">🔄</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-row :gutter="20">
      <!-- 左侧：收藏文章列表 -->
      <el-col :span="16">
        <el-card class="favorites-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">收藏文章</span>
              <el-button type="primary" @click="loadFavorites" :loading="loading">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <div v-loading="loading" class="favorites-list">
            <div v-if="favorites.length === 0 && !loading" class="empty-state">
              <el-empty description="还没有收藏任何文章">
                <el-button type="primary" @click="$router.push('/content')">
                  去发现内容
                </el-button>
              </el-empty>
            </div>

            <div v-else class="favorite-items">
              <el-card 
                v-for="item in favorites" 
                :key="item._id"
                class="favorite-item"
                shadow="hover"
              >
                <div class="favorite-item-body">
                  <div class="favorite-main">
                    <div class="favorite-meta">
                      <el-tag 
                        :type="getContentTypeColor(item.type)" 
                        size="small"
                        class="content-type-tag"
                      >
                        {{ getContentTypeLabel(item.type) }}
                      </el-tag>
                      <span class="favorite-source">{{ item.source }}</span>
                      <span class="favorite-date">收藏于 {{ formatDate(item.favorited_at) }}</span>
                    </div>
                    <h3 class="favorite-title">
                      <a 
                        v-if="item.link" 
                        :href="item.link" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        class="article-link"
                      >
                        {{ item.title }}
                        <el-icon class="external-link-icon"><TopRight /></el-icon>
                      </a>
                      <span v-else>{{ item.title }}</span>
                    </h3>
                    <p class="favorite-publish-date">发布于 {{ formatDate(item.publish_date) }}</p>
                    <div class="favorite-tags" v-if="getAllTags(item).length">
                      <el-tag 
                        v-for="tag in getAllTags(item).slice(0, 8)" 
                        :key="tag"
                        size="small"
                        class="favorite-tag"
                        :type="getTagColor(tag)"
                      >
                        {{ tag }}
                      </el-tag>
                      <span v-if="getAllTags(item).length > 8" class="more-tags">
                        +{{ getAllTags(item).length - 8 }}
                      </span>
                    </div>
                  </div>
                  <div class="favorite-actions">
                    <el-button type="danger" link @click="removeFavorite(item)">
                      <el-icon><Delete /></el-icon>
                      取消收藏
                    </el-button>
                  </div>
                </div>
              </el-card>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：收藏统计 -->
      <el-col :span="8">
        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">收藏统计</span>
            </div>
          </template>

          <div class="stats-content">
            <!-- 能源类型兴趣 -->
            <div class="interest-section" v-if="Object.keys(behaviorStats.energy_type_interests || {}).length">
              <h4 class="section-title">能源类型兴趣</h4>
              <div class="interest-list">
                <div 
                  v-for="(count, energyType) in behaviorStats.energy_type_interests" 
                  :key="energyType"
                  class="interest-item"
                >
                  <span class="interest-name">{{ energyType }}</span>
                  <div class="interest-bar">
                    <div 
                      class="interest-progress energy-progress"
                      :style="{ width: getPercentage(count, getMaxCount(behaviorStats.energy_type_interests)) + '%' }"
                    ></div>
                  </div>
                  <span class="interest-count">{{ count }}</span>
                </div>
              </div>
            </div>

            <!-- 地域兴趣 -->
            <div class="interest-section" v-if="Object.keys(behaviorStats.region_interests || {}).length">
              <h4 class="section-title">地域兴趣</h4>
              <div class="interest-list">
                <div 
                  v-for="(count, region) in behaviorStats.region_interests" 
                  :key="region"
                  class="interest-item"
                >
                  <span class="interest-name">{{ region }}</span>
                  <div class="interest-bar">
                    <div 
                      class="interest-progress region-progress"
                      :style="{ width: getPercentage(count, getMaxCount(behaviorStats.region_interests)) + '%' }"
                    ></div>
                  </div>
                  <span class="interest-count">{{ count }}</span>
                </div>
              </div>
            </div>

            <!-- 收藏提示 -->
            <div class="tips-section">
              <h4 class="section-title">💡 收藏小贴士</h4>
              <ul class="tips-list">
                <li>收藏文章会自动学习相关标签</li>
                <li>系统会基于收藏内容优化推荐</li>
                <li>取消收藏不会删除已学习标签</li>
                <li>多收藏感兴趣的内容提升精准度</li>
              </ul>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 页面宽度占位符 - 不可见但确保页面宽度一致 -->
    <div class="width-placeholder" aria-hidden="true"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { favoritesAPI, type FavoriteItem, type UserBehaviorStats } from '../api/favorites'

// 响应式数据
const loading = ref(true)
const favorites = ref<FavoriteItem[]>([])
const totalFavorites = ref(0)
const behaviorStats = ref<UserBehaviorStats>({
  user_id: '',
  total_favorites: 0,
  energy_type_interests: {},
  region_interests: {}
})

// 搜索相关
const searchQuery = ref('')
const isSearching = ref(false)

// 加载收藏数据
const loadFavorites = async () => {
  try {
    loading.value = true
    const [favoritesList, count, stats] = await Promise.all([
      favoritesAPI.getFavoritesList(),
      favoritesAPI.getFavoritesCount(),
      favoritesAPI.getUserBehaviorStats()
    ])
    
    favorites.value = favoritesList
    totalFavorites.value = count
    behaviorStats.value = stats
  } catch (error) {
    console.error('加载收藏数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索收藏文章
const performSearch = async () => {
  try {
    loading.value = true
    isSearching.value = true
    
    let favoritesList
    if (searchQuery.value.trim()) {
      favoritesList = await favoritesAPI.searchFavorites(searchQuery.value.trim())
    } else {
      favoritesList = await favoritesAPI.getFavoritesList()
    }
    
    favorites.value = favoritesList
  } catch (error) {
    console.error('搜索收藏失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索输入处理
const handleSearch = () => {
  // 可以添加防抖逻辑
  if (searchQuery.value.trim() === '') {
    resetSearch()
  }
}

// 清空搜索
const handleSearchClear = () => {
  searchQuery.value = ''
  resetSearch()
}

// 重置搜索
const resetSearch = async () => {
  searchQuery.value = ''
  isSearching.value = false
  await loadFavorites()
}

// 取消收藏
const removeFavorite = async (item: FavoriteItem) => {
  try {
    const result = await favoritesAPI.removeFavorite(item.content_id)
    if (result.success) {
      // 从列表中移除
      favorites.value = favorites.value.filter(fav => fav.content_id !== item.content_id)
      
      // 重新加载统计数据
      behaviorStats.value = await favoritesAPI.getUserBehaviorStats()
    }
  } catch (error) {
    console.error('取消收藏失败:', error)
  }
}

// 获取所有标签
const getAllTags = (item: FavoriteItem) => {
  const allTags = [
    ...(item.energy_type_tags || []),
    ...(item.region_tags || [])
  ]
  return allTags.filter(tag => tag && tag.trim() !== '')
}

// 获取内容类型颜色
const getContentTypeColor = (type: string) => {
  const typeColors = {
    'policy': 'warning',
    'news': 'primary',
    'price': 'danger',
    'announcement': 'success'
  }
  return typeColors[type as keyof typeof typeColors] || 'info'
}

// 获取内容类型标签
const getContentTypeLabel = (type: string) => {
  const typeLabels = {
    'policy': '政策法规',
    'news': '行业资讯',
    'price': '调价公告',
    'announcement': '交易公告'
  }
  return typeLabels[type as keyof typeof typeLabels] || '其他'
}

// 获取标签颜色
const getTagColor = (tag: string) => {
  const energyTypes = ['天然气', '原油', '液化天然气(LNG)', '管道天然气(PNG)', '电力', '煤炭']
  const regions = ['上海', '北京', '广州', '深圳', '华东', '华北', '华南', '全国']
  
  if (energyTypes.includes(tag)) {
    return 'warning'
  } else if (regions.includes(tag)) {
    return 'success'
  } else {
    return 'info'
  }
}

// 计算百分比
const getPercentage = (count: number, maxCount: number) => {
  return maxCount > 0 ? Math.round((count / maxCount) * 100) : 0
}

// 获取最大计数
const getMaxCount = (interests: Record<string, number>) => {
  const values = Object.values(interests)
  return values.length > 0 ? Math.max(...values) : 0
}

// 最后活动时间文本
const lastActivityText = computed(() => {
  if (behaviorStats.value.last_activity) {
    return formatDate(behaviorStats.value.last_activity)
  }
  return '暂无'
})

// 工具函数
const getTypeClass = (type: string) => {
  const typeClasses = {
    'policy': 'type-policy',
    'news': 'type-news',
    'price': 'type-price',
    'announcement': 'type-announcement'
  }
  return typeClasses[type as keyof typeof typeClasses] || 'type-default'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 组件挂载时加载数据
onMounted(() => {
  loadFavorites()
})
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
  background-color: #f5f7fa;  /* 🔥 参考内容资讯页面的背景色 */
  min-height: calc(100vh - 64px);
}

/* 页面头部 - 参考内容资讯页面样式 */
.header-section {
  text-align: center;
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.page-title {
  font-size: 32px;
  font-weight: bold;
  color: #1769aa;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.title-icon {
  font-size: 36px;
  color: #1890ff;
}

.page-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

/* 搜索卡片样式 */
.search-card {
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  background: white;
}

.search-stats {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
}

.search-result-text {
  font-size: 14px;
  color: #606266;
}

.search-result-text strong {
  color: #1890ff;
  font-weight: bold;
}

/* 统计卡片 - 参考行情页面的卡片样式 */
.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  overflow: hidden;
  border-radius: 16px;  /* 🔥 使用行情页面的圆角 */
  background: white;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);  /* 🔥 使用行情页面的阴影效果 */
  border: none;
  transition: all 0.3s ease;
  cursor: pointer;  /* 🔥 添加指针样式 */
}

.stat-card:hover {
  transform: translateY(-4px);  /* 🔥 参考行情页面的悬停效果 */
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.stat-card .stat-icon {
  position: absolute;
  top: 50%;
  right: 16px;
  transform: translateY(-50%);
  font-size: 32px;  /* 🔥 参考行情页面的图标大小 */
  opacity: 0.3;
  color: #909399;
}

/* 主要内容区域 - 参考内容资讯页面 */
.favorites-card,
.stats-card {
  border-radius: 12px;  /* 🔥 使用内容资讯页面的圆角 */
  background: white;
  border: none;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);  /* 🔥 使用内容资讯页面的阴影 */
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.card-title {
  font-size: 18px;
  font-weight: bold;  /* 🔥 加粗标题 */
  color: #303133;  /* 🔥 使用参考页面的标题颜色 */
}

/* 收藏列表 - 参考内容资讯页面的内容项样式 */
.favorite-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 500px;  /* 🔥 参考内容资讯页面的最小高度 */
}

.favorite-item {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;  /* 🔥 使用内容资讯页面的圆角 */
  background: white;
  border: 1px solid #ebeef5;  /* 🔥 使用参考页面的边框颜色 */
  overflow: hidden;
}

.favorite-item:hover {
  transform: translateY(-2px);  /* 🔥 参考内容资讯页面的悬停效果 */
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.favorite-item-body {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;  /* 🔥 使用舒适的内边距 */
  gap: 16px;
}

.favorite-main {
  flex: 1;
}

.favorite-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;  /* 🔥 参考内容资讯页面的间距 */
}

.content-type-tag {
  font-weight: bold;  /* 🔥 参考内容资讯页面的标签样式 */
  border-radius: 6px;
}

.favorite-source {
  color: #909399;  /* 🔥 使用参考页面的次要文字颜色 */
  font-size: 14px;
  font-weight: 500;
}

.favorite-date {
  color: #909399;
  font-size: 14px;
}

.favorite-title {
  margin: 0 0 8px 0;  /* 🔥 参考内容资讯页面的标题间距 */
  font-size: 18px;  /* 🔥 使用参考页面的标题字体大小 */
  font-weight: bold;  /* 🔥 加粗标题 */
  line-height: 1.4;
  color: #303133;  /* 🔥 使用参考页面的标题颜色 */
}

.article-link {
  color: #303133;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;  /* 🔥 参考内容资讯页面的链接样式 */
  transition: all 0.3s ease;
}

.article-link:hover {
  color: #1890ff;  /* 🔥 使用主题蓝色 */
  text-decoration: none;
}

.external-link-icon {
  font-size: 14px;
  opacity: 0.6;
  transition: all 0.3s ease;
}

.article-link:hover .external-link-icon {
  opacity: 1;
  transform: translateX(2px) translateY(-2px);  /* 🔥 参考内容资讯页面的动画效果 */
}

.favorite-publish-date {
  color: #606266;  /* 🔥 使用参考页面的文字颜色 */
  font-size: 14px;
  line-height: 1.6;  /* 🔥 参考内容资讯页面的行高 */
  margin: 6px 0;
}

.favorite-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;  /* 🔥 参考内容资讯页面的标签间距 */
  align-items: center;
  margin-top: 12px;
}

.favorite-tag {
  font-size: 12px;  /* 🔥 参考内容资讯页面的标签字体 */
  border-radius: 4px;
  font-weight: 500;
  margin: 0;
  padding: 4px 8px;
  height: 24px;
  line-height: 16px;
  display: inline-flex;
  align-items: center;
  box-sizing: border-box;
}

.more-tags {
  color: #909399;  /* 🔥 使用参考页面的颜色 */
  font-size: 12px;
  font-weight: 500;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
}

.favorite-actions {
  margin-left: 16px;  /* 🔥 参考内容资讯页面的操作区域样式 */
  display: flex;
  align-items: center;
  flex-direction: column;
  gap: 8px;
}

/* 统计内容 - 参考行情页面的信息展示 */
.stats-content {
  padding: 0;
}

.interest-section {
  margin-bottom: 32px;  /* 🔥 增加间距 */
}

.section-title {
  margin: 0 0 20px 0;  /* 🔥 增加标题下方间距 */
  font-size: 16px;
  font-weight: bold;  /* 🔥 加粗标题 */
  color: #303133;
}

.interest-list {
  display: flex;
  flex-direction: column;
  gap: 16px;  /* 🔥 增加项目间距 */
}

.interest-item {
  display: grid;
  grid-template-columns: 1fr 100px 40px;  /* 🔥 调整列宽 */
  align-items: center;
  gap: 12px;
  padding: 8px 0;  /* 🔥 添加垂直内边距 */
}

.interest-name {
  font-size: 14px;
  font-weight: 600;  /* 🔥 加粗名称 */
  color: #303133;  /* 🔥 使用主要文字颜色 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.interest-bar {
  height: 10px;  /* 🔥 增加进度条高度 */
  background-color: #f0f2f5;  /* 🔥 调整背景色 */
  border-radius: 8px;  /* 🔥 增加圆角 */
  overflow: hidden;
}

.interest-progress {
  height: 100%;
  border-radius: 8px;
  transition: width 0.4s ease;
}

.energy-progress {
  background: linear-gradient(135deg, #f59e0b, #f97316);
}

.region-progress {
  background: linear-gradient(135deg, #10b981, #059669);
}

.interest-count {
  font-size: 14px;
  font-weight: bold;  /* 🔥 加粗数字 */
  color: #303133;
  text-align: right;
}

/* 收藏小贴士 - 参考页面的信息提示样式 */
.tips-section {
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);  /* 🔥 使用渐变背景 */
  padding: 20px;  /* 🔥 增加内边距 */
  border-radius: 12px;  /* 🔥 增加圆角 */
  border: 1px solid #e2e8f0;
  margin-top: 24px;
}

.tips-list {
  margin: 0;
  padding-left: 16px;
  color: #64748b;
  font-size: 14px;
  line-height: 1.8;  /* 🔥 增加行高 */
}

.tips-list li {
  margin-bottom: 8px;  /* 🔥 增加项目间距 */
}

/* 空状态 - 参考内容资讯页面 */
.empty-state {
  text-align: center;
  padding: 60px 0;  /* 🔥 参考内容资讯页面的空状态样式 */
  border-radius: 8px;
  background: #f8fafc;
}

/* Element Plus 样式重写 */
:deep(.el-statistic__head) {
  color: #606266;
  margin-bottom: 8px;
}

:deep(.el-statistic__content) {
  color: #303133;
  font-weight: bold;
}

/* 动画效果 - 参考行情页面 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.favorite-item {
  animation: fadeInUp 0.6s ease;
}

.stat-card {
  animation: fadeInUp 0.4s ease;
}

/* 响应式设计 - 参考页面的响应式处理 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .favorite-item-body {
    flex-direction: column;
    gap: 12px;
    padding: 16px;
  }
  
  .favorite-meta {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .interest-item {
    grid-template-columns: 1fr 80px 30px;
    gap: 8px;
  }
  
  .favorite-actions {
    margin-left: 0;
    flex-direction: row;
    justify-content: flex-end;
  }
}

/* 页面宽度占位符 - 保持与参考页面一致 */
.width-placeholder {
  width: 1280px;
  min-width: 1280px;
  height: 1px;
  visibility: hidden;
  pointer-events: none;
  position: relative;
  margin: 0 auto;
}
</style> 