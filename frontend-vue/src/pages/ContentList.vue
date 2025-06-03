<template>
  <div class="dashboard-container">
    <!-- 页面标题 -->
    <div class="header-section">
      <h1 class="page-title">
        <el-icon class="title-icon"><Document /></el-icon>
        内容资讯中心
      </h1>
      <p class="page-subtitle">全面的能源政策、行情动态和公告信息</p>
    </div>

    <!-- 筛选和搜索 -->
    <el-card class="filter-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="6">
          <el-select 
            v-model="activeCategory" 
            placeholder="选择分类"
            size="large"
            @change="handleCategoryChange"
            style="width: 100%"
          >
            <el-option label="全部内容" value="all" />
            <el-option label="📈 行情动态" value="market" />
            <el-option label="📋 政策法规" value="policy" />
            <el-option label="📢 公告信息" value="announcement" />
          </el-select>
        </el-col>
        <el-col :span="6" v-if="activeCategory === 'announcement'">
          <el-select 
            v-model="announcementType" 
            placeholder="公告类型"
            size="large"
            @change="loadContent"
            style="width: 100%"
          >
            <el-option label="全部公告" value="all" />
            <el-option label="📊 交易公告" value="trade" />
            <el-option label="💰 调价公告" value="price" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索标题或内容..."
            size="large"
            clearable
            @change="handleSearch"
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
            @click="loadContent"
            :loading="loading"
            style="width: 100%"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计信息 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" @click="selectCategory('market')">
          <el-statistic title="行情咨询" :value="stats.market" />
          <div class="stat-icon">📈</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" @click="selectCategory('policy')">
          <el-statistic title="政策法规" :value="stats.policy" />
          <div class="stat-icon">📋</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" @click="selectCategory('announcement', 'trade')">
          <el-statistic title="交易公告" :value="stats.tradeAnnouncement" />
          <div class="stat-icon">📊</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" @click="selectCategory('announcement', 'price')">
          <el-statistic title="调价公告" :value="stats.priceAnnouncement" />
          <div class="stat-icon">💰</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 内容列表 -->
    <el-card class="content-card">
      <template #header>
        <div class="content-header">
          <span class="content-title">
            {{ getCategoryTitle() }}
            <el-tag v-if="filteredContent.length" type="info" size="small">
              {{ filteredContent.length }} 条
            </el-tag>
          </span>
          <div class="content-actions">
            <el-select v-model="sortBy" size="small" @change="loadContent">
              <el-option label="最新发布" value="latest" />
              <el-option label="最多浏览" value="popularity" />
            </el-select>
          </div>
        </div>
      </template>

      <div v-loading="loading" class="content-list">
        <div v-if="filteredContent.length === 0 && !loading" class="empty-state">
          <el-empty description="暂无相关内容" />
        </div>
        
        <div v-else class="content-items">
          <el-card 
            v-for="(item, index) in paginatedContent" 
            :key="item.id || index"
            class="content-item"
            shadow="hover"
            @click="viewContent(item)"
          >
            <div class="content-item-body">
              <div class="content-main">
                <div class="content-meta">
                  <el-tag 
                    :type="getContentTypeColor(item.type)" 
                    size="small"
                    class="content-type-tag"
                  >
                    {{ getContentTypeLabel(item.type) }}
                  </el-tag>
                  <span class="content-date">{{ formatDate(item.publish_time) }}</span>
                  <span class="content-views">
                    <el-icon><View /></el-icon>
                    {{ item.view_count || 0 }}
                  </span>
                </div>
                <h3 class="content-title-text">{{ item.title }}</h3>
                <p class="content-summary">{{ item.content || '暂无摘要' }}</p>
                <div class="content-tags" v-if="getAllTags(item).length">
                  <el-tag 
                    v-for="tag in getAllTags(item).slice(0, 5)" 
                    :key="tag"
                    size="small"
                    class="content-tag"
                    :type="getTagColor(tag)"
                  >
                    {{ tag }}
                  </el-tag>
                  <span v-if="getAllTags(item).length > 5" class="more-tags">
                    +{{ getAllTags(item).length - 5 }}
                  </span>
                </div>
              </div>
              <div class="content-actions-area">
                <el-button type="primary" link @click.stop="viewContent(item)">
                  <el-icon><Reading /></el-icon>
                  阅读全文
                </el-button>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="filteredContent.length > pageSize">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="filteredContent.length"
            layout="total, prev, pager, next, jumper"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </el-card>

    <!-- 页面宽度占位符 - 不可见但确保页面宽度一致 -->
    <div class="width-placeholder" aria-hidden="true"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  Document, 
  Search, 
  Refresh, 
  View, 
  Reading 
} from '@element-plus/icons-vue'
import api from '@/api/request'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const activeCategory = ref('all')
const announcementType = ref('all')
const searchKeyword = ref('')
const sortBy = ref('latest')
const currentPage = ref(1)
const pageSize = ref(10)

// 内容数据
const allContent = ref([])
const stats = ref({
  market: 0,
  policy: 0,
  tradeAnnouncement: 0,
  priceAnnouncement: 0
})

// 计算属性
const filteredContent = computed(() => {
  let filtered = [...allContent.value]
  
  // 按分类筛选
  if (activeCategory.value !== 'all') {
    switch (activeCategory.value) {
      case 'market':
        // 行情动态：精确匹配"行业资讯"标签
        filtered = filtered.filter(item => 
          (item.basic_info_tags || []).includes('行业资讯')
        )
        break
      case 'policy':
        // 政策法规：精确匹配"政策法规"标签
        filtered = filtered.filter(item => 
          (item.basic_info_tags || []).includes('政策法规')
        )
        break
      case 'announcement':
        // 公告信息：匹配"交易公告"或"调价公告"标签
        filtered = filtered.filter(item => 
          (item.basic_info_tags || []).includes('交易公告') ||
          (item.basic_info_tags || []).includes('调价公告')
        )
        break
    }
  }
  
  // 搜索筛选
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(item => 
      item.title.toLowerCase().includes(keyword) ||
      (item.content && item.content.toLowerCase().includes(keyword))
    )
  }
  
  // 排序
  if (sortBy.value === 'latest') {
    filtered.sort((a, b) => new Date(b.publish_time).getTime() - new Date(a.publish_time).getTime())
  } else if (sortBy.value === 'popularity') {
    filtered.sort((a, b) => (b.view_count || 0) - (a.view_count || 0))
  }
  
  return filtered
})

const paginatedContent = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredContent.value.slice(start, end)
})

// 工具函数
const getAllTags = (item) => {
  return [
    ...(item.basic_info_tags || []),
    ...(item.region_tags || []),
    ...(item.energy_type_tags || []),
    ...(item.business_field_tags || []),
    ...(item.beneficiary_tags || []),
    ...(item.policy_measure_tags || []),
    ...(item.importance_tags || [])
  ]
}

const getContentTypeLabel = (type) => {
  switch (type) {
    case 'NEWS': return '资讯'
    case 'POLICY': return '政策'
    case 'ANNOUNCEMENT': return '公告'
    case 'PRICE': return '调价'
    default: return '资讯'
  }
}

const getContentTypeColor = (type) => {
  switch (type) {
    case 'NEWS': return 'primary'
    case 'POLICY': return 'success'
    case 'ANNOUNCEMENT': return 'warning'
    case 'PRICE': return 'danger'
    default: return 'info'
  }
}

const getTagColor = (tag) => {
  if (tag.includes('公告')) return 'warning'
  if (tag.includes('政策')) return 'success'
  if (tag.includes('行情')) return 'primary'
  if (tag.includes('能源')) return 'danger'
  return ''
}

const getCategoryTitle = () => {
  switch (activeCategory.value) {
    case 'market': return '📈 行情动态'
    case 'policy': return '📋 政策法规'
    case 'announcement': 
      if (announcementType.value === 'trade') return '📊 交易公告'
      if (announcementType.value === 'price') return '💰 调价公告'
      return '📢 公告信息'
    default: return '📄 全部内容'
  }
}

const formatDate = (date) => {
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).replace(/\//g, '-')
}

// 方法
const loadContent = async () => {
  loading.value = true
  try {
    console.log('🔄 加载内容列表...')
    const response = await api.get('/content/', {
      params: {
        page: 1,
        page_size: 100, // 修复：增加到100确保获取所有数据
        sort_by: sortBy.value
      }
    })
    
    allContent.value = response.data.items || []
    console.log('✅ 内容加载成功:', allContent.value.length, '条')
    
    // 更新统计数据
    updateStats()
    
  } catch (error) {
    console.error('❌ 加载内容失败:', error)
    ElMessage.error('加载内容失败')
    allContent.value = []
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  const content = allContent.value
  
  stats.value = {
    // 行情动态：精确匹配"行业资讯"标签
    market: content.filter(item => 
      (item.basic_info_tags || []).includes('行业资讯')
    ).length,
    // 政策法规：精确匹配"政策法规"标签  
    policy: content.filter(item => 
      (item.basic_info_tags || []).includes('政策法规')
    ).length,
    // 交易公告：精确匹配"交易公告"标签
    tradeAnnouncement: content.filter(item => 
      (item.basic_info_tags || []).includes('交易公告')
    ).length,
    // 调价公告：精确匹配"调价公告"标签
    priceAnnouncement: content.filter(item => 
      (item.basic_info_tags || []).includes('调价公告')
    ).length
  }
}

const selectCategory = (category, subType = 'all') => {
  activeCategory.value = category
  if (category === 'announcement') {
    announcementType.value = subType
  } else {
    announcementType.value = 'all'
  }
  currentPage.value = 1
}

const handleCategoryChange = () => {
  announcementType.value = 'all'
  currentPage.value = 1
}

const handleSearch = () => {
  currentPage.value = 1
}

const handlePageChange = () => {
  // 页面变化时自动滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const viewContent = (item) => {
  console.log('查看内容:', item.title)
  // TODO: 实现内容详情页面跳转
  ElMessage.info('内容详情功能开发中...')
}

// 监听路由参数
watch(() => route.query.type, (newType) => {
  if (newType) {
    switch (newType) {
      case 'news':
        activeCategory.value = 'market'
        break
      case 'policy':
        activeCategory.value = 'policy'
        break
      case 'announcement':
        activeCategory.value = 'announcement'
        break
    }
  }
}, { immediate: true })

// 页面挂载
onMounted(() => {
  loadContent()
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  max-width: 1280px;
  margin: 0 auto;
}

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

.filter-card {
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  cursor: pointer;
  background: white;
  border: 1px solid #ebeef5;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.stat-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 32px;
  opacity: 0.3;
  color: #909399;
}

.content-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  background: white;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.content-list {
  min-height: 600px;
}

.content-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 500px;
}

.content-item {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
}

.content-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.content-item-body {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.content-main {
  flex: 1;
}

.content-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.content-type-tag {
  font-weight: bold;
}

.content-date {
  color: #909399;
  font-size: 14px;
}

.content-views {
  color: #909399;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.content-title-text {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.content-summary {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.content-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.content-tag {
  font-size: 12px;
}

.more-tags {
  color: #909399;
  font-size: 12px;
}

.content-actions-area {
  margin-left: 16px;
  display: flex;
  align-items: center;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.empty-state {
  padding: 60px 0;
}

:deep(.el-statistic__head) {
  color: #606266;
  margin-bottom: 8px;
}

:deep(.el-statistic__content) {
  color: #303133;
  font-weight: bold;
}

/* 页面宽度占位符 - 不可见但确保页面宽度一致 */
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