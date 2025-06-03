<template>
  <div class="dashboard-container">
    <!-- 能源行情区块 -->
    <el-card class="mb-4 market-card-enhanced">
      <template #header>
        <div class="market-header-enhanced">
          <div class="header-left">
            <el-icon class="market-icon"><TrendCharts /></el-icon>
            <span class="market-title">能源行情中心</span>
            <el-tag type="success" size="small" class="ml-2">实时</el-tag>
          </div>
          <div class="header-right">
            <span class="update-time">{{ new Date().toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'}) }}</span>
            <el-button type="primary" size="small" text @click="goToMarket">
              查看详情 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="market-content-enhanced">
        <el-row :gutter="16" align="middle">
          <el-col :span="4" v-for="(item, index) in marketData.slice(0, 5)" :key="item.name">
            <el-card class="market-item-enhanced" :class="{ 'up': item.change > 0, 'down': item.change < 0, 'flat': item.change === 0 }" shadow="hover">
              <div class="market-item-content">
                <div class="market-name">{{ item.shortName }}</div>
                <div class="market-price-main" :class="{ 'up': item.change > 0, 'down': item.change < 0 }">
                  {{ item.price }}
                </div>
                <div class="market-change-enhanced" :class="{ 'up': item.change > 0, 'down': item.change < 0 }">
                  <el-icon v-if="item.change > 0" class="trend-icon"><CaretTop /></el-icon>
                  <el-icon v-else-if="item.change < 0" class="trend-icon"><CaretBottom /></el-icon>
                  <el-icon v-else class="trend-icon"><Minus /></el-icon>
                  {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                </div>
                <div class="market-volume">{{ item.volume }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="4" v-if="marketData.length > 5">
            <el-card class="market-more-enhanced" @click="goToMarket" shadow="hover">
              <div class="more-content-enhanced">
                <el-icon class="more-icon"><Plus /></el-icon>
                <div class="more-text">查看更多</div>
                <div class="more-desc">{{ marketData.length }} 个品种</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 主要内容区域 -->
    <el-row :gutter="20">
      <!-- 左侧：猜你喜欢 -->
      <el-col :span="16">
        <!-- 猜你喜欢 -->
        <el-card class="mb-4">
          <template #header>
            <div class="card-header">
              <span>猜你喜欢</span>
              <el-button type="primary" link @click="refreshRecommendations">刷新</el-button>
            </div>
            <!-- 推荐分类按钮组 -->
            <div class="recommendation-filter">
              <el-button-group>
                <el-button 
                  :type="recommendationFilter === 'all' ? 'primary' : ''"
                  size="small"
                  @click="setRecommendationFilter('all')"
                >
                  全部推荐
                </el-button>
                <el-button 
                  :type="recommendationFilter === 'market' ? 'primary' : ''"
                  size="small"
                  @click="setRecommendationFilter('market')"
                >
                  📈 行情
                </el-button>
                <el-button 
                  :type="recommendationFilter === 'policy' ? 'primary' : ''"
                  size="small"
                  @click="setRecommendationFilter('policy')"
                >
                  📋 政策
                </el-button>
                <el-button 
                  :type="recommendationFilter === 'announcement' ? 'primary' : ''"
                  size="small"
                  @click="setRecommendationFilter('announcement')"
                >
                  📢 公告
                </el-button>
              </el-button-group>
            </div>
          </template>
          <div class="recommendations">
            <el-timeline v-if="filteredRecommendations.length">
              <el-timeline-item
                v-for="(item, index) in filteredRecommendations"
                :key="index"
                :timestamp="formatDate(item.publish_time)"
                :type="getTimelineType(item.type)"
              >
                <el-card class="recommendation-card">
                  <h4>
                    <a 
                      v-if="item.link" 
                      :href="item.link" 
                      target="_blank" 
                      style="color: #409EFF; text-decoration: none; font-weight: bold;"
                      @mouseover="($event.target as HTMLElement).style.color='#66b1ff'"
                      @mouseout="($event.target as HTMLElement).style.color='#409EFF'"
                    >
                      {{ item.title }}
                    </a>
                    <span v-else style="font-weight: bold;">{{ item.title }}</span>
                  </h4>
                  <p>{{ item.content }}</p>
                  <div class="tags">
                    <el-tag 
                      v-for="tag in getAllTags(item)" 
                      :key="tag" 
                      size="small" 
                      class="mr-2"
                      :type="getTagType(tag)"
                    >
                      {{ tag }}
                    </el-tag>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else :description="getEmptyDescription()" />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：咨询概览、交易公告、调价公告、标签统计 -->
      <el-col :span="8">
        <!-- 咨询概览 -->
        <el-card class="mb-4">
          <template #header>
            <div class="card-header">
              <span>咨询概览</span>
              <el-button type="primary" link @click="goToContent">查看全部</el-button>
            </div>
          </template>
          <div class="content-overview">
            <el-row :gutter="16">
              <el-col :span="8" v-for="(stat, index) in contentStats" :key="index">
                <div class="stat-overview-item" @click="goToContentByType(stat.type)">
                  <h3>{{ stat.value }}</h3>
                  <p>{{ stat.title }}</p>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <!-- 最新交易公告 -->
        <el-card class="mb-4">
          <template #header>
            <div class="card-header">
              <span>最新交易公告</span>
            </div>
          </template>
          <div class="announcements">
            <el-scrollbar height="150px">
              <div v-for="(item, index) in tradeAnnouncements" :key="index" class="announcement-item">
                <a :href="item.link" target="_blank" style="font-weight:bold;">{{ item.title }}</a>
                <p class="text-gray-600">{{ formatDate(item.publish_time) }}</p>
              </div>
              <el-empty v-if="!tradeAnnouncements.length" description="暂无交易公告" />
            </el-scrollbar>
          </div>
        </el-card>

        <!-- 最新调价公告 -->
        <el-card class="mb-4">
          <template #header>
            <div class="card-header">
              <span>最新调价公告</span>
            </div>
          </template>
          <div class="announcements">
            <el-scrollbar height="150px">
              <div v-for="(item, index) in priceAnnouncements" :key="index" class="announcement-item">
                <a :href="item.link" target="_blank" style="font-weight:bold;">{{ item.title }}</a>
                <p class="text-gray-600">{{ formatDate(item.publish_time) }}</p>
              </div>
              <el-empty v-if="!priceAnnouncements.length" description="暂无调价公告" />
            </el-scrollbar>
          </div>
        </el-card>

        <!-- 我的标签统计 -->
        <el-card>
          <template #header>
            <div class="card-header">
              <span>我的标签统计</span>
              <el-button type="primary" link @click="goToTags">管理标签</el-button>
            </div>
          </template>
          <div class="tag-stats">
            <el-row :gutter="12">
              <el-col :span="12" v-for="(stat, index) in tagStats.filter(s => s.count > 0).slice(0, 6)" :key="index">
                <div class="stat-item-compact">
                  <h4>{{ stat.count }}</h4>
                  <p>{{ stat.label }}</p>
                </div>
              </el-col>
            </el-row>
            <el-empty v-if="!tagStats.some(stat => stat.count > 0)" description="暂无标签数据" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 市场行情快览 -->
    <el-card v-if="marketData.length" class="market-card">
      <!-- ... existing code ... -->
    </el-card>

    <!-- 页面宽度占位符 - 不可见但确保页面宽度一致 -->
    <div class="width-placeholder" aria-hidden="true"></div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/store/user'
import { useRouter } from 'vue-router'
import { ref, computed, onMounted } from 'vue'
import { 
  Document, 
  Setting, 
  DataAnalysis, 
  Bell,
  TrendCharts,
  CaretTop,
  CaretBottom,
  Minus,
  Plus,
  ArrowRight
} from '@element-plus/icons-vue'
import { getUserTags, getUserRecommendations, getAnnouncements, getContentStats } from '@/api/user'
import axios from 'axios'
import api from '@/api/request'

const userStore = useUserStore()
const router = useRouter()

// 个性化欢迎语
const welcomeMessage = computed(() => {
  const username = userStore.userInfo?.username || '用户'
  const hour = new Date().getHours()
  let greeting = ''
  if (hour < 6) greeting = '凌晨好'
  else if (hour < 9) greeting = '早上好'
  else if (hour < 12) greeting = '上午好'
  else if (hour < 14) greeting = '中午好'
  else if (hour < 17) greeting = '下午好'
  else if (hour < 19) greeting = '傍晚好'
  else greeting = '晚上好'
  return `${greeting}，${username}`
})

// 用户头像
const userAvatar = ref('')

// 标签统计
const tagStats = ref([
  { label: '城市标签', key: 'city', count: 0 },
  { label: '省份标签', key: 'province', count: 0 },
  { label: '区域标签', key: 'region', count: 0 },
  { label: '能源品种', key: 'energy_type', count: 0 },
  { label: '业务领域', key: 'business_field', count: 0 },
  { label: '受益主体', key: 'beneficiary', count: 0 },
  { label: '关键措施', key: 'policy_measure', count: 0 },
  { label: '重要性', key: 'importance', count: 0 },
  { label: '基础信息', key: 'basic_info', count: 0 }
])

// 响应式数据
const userTags = ref([])
const recommendations = ref([])
const filteredRecommendations = ref([])
const recommendationFilter = ref('all')
const tradeAnnouncements = ref([])
const priceAnnouncements = ref([])

// 资讯概览
const contentStats = ref([
  { title: '今日资讯', value: 0, type: 'news' },
  { title: '本周政策', value: 0, type: 'policy' },
  { title: '总内容数', value: 0, type: 'announcement' }
])

// 行情数据
const marketData = ref([
  {
    name: '管道天然气(PNG)',
    shortName: 'PNG',
    price: '3.85元/m³',
    change: 2.5,
    high: '3.92元/m³',
    low: '3.75元/m³',
    volume: '1.2亿m³'
  },
  {
    name: '液化天然气(LNG)',
    shortName: 'LNG',
    price: '4.25元/m³',
    change: -1.2,
    high: '4.35元/m³',
    low: '4.15元/m³',
    volume: '0.8亿m³'
  },
  {
    name: '原油',
    shortName: '原油',
    price: '78.5$/桶',
    change: 0.8,
    high: '79.2$/桶',
    low: '77.8$/桶',
    volume: '150万桶'
  },
  {
    name: '液化石油气(LPG)',
    shortName: 'LPG',
    price: '5.2元/kg',
    change: 1.5,
    high: '5.3元/kg',
    low: '5.1元/kg',
    volume: '50万吨'
  },
  {
    name: '汽油',
    shortName: '汽油',
    price: '7.85元/L',
    change: -0.5,
    high: '7.95元/L',
    low: '7.75元/L',
    volume: '200万吨'
  },
  {
    name: '柴油',
    shortName: '柴油', 
    price: '7.45元/L',
    change: 0.3,
    high: '7.55元/L',
    low: '7.35元/L',
    volume: '180万吨'
  }
])

// 获取所有标签
const getAllTags = (item: any) => {
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

// 获取标签类型
const getTagType = (tag: string) => {
  if (tag.includes('城市')) return 'success'
  if (tag.includes('能源')) return 'warning'
  if (tag.includes('业务')) return 'info'
  if (tag.includes('受益')) return 'danger'
  if (tag.includes('措施')) return 'primary'
  if (tag.includes('重要')) return 'success'
  if (tag.includes('省份')) return 'info'
  if (tag.includes('区域')) return 'warning'
  return ''
}

// 获取时间线类型
const getTimelineType = (type: string) => {
  switch (type) {
    case 'POLICY': return 'primary'
    case 'NEWS': return 'success'
    case 'PRICE': return 'warning'
    case 'ANNOUNCEMENT': return 'danger'
    default: return 'info'
  }
}

// 格式化日期
const formatDate = (date: string) => {
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).replace(/\//g, '-')
}

// 加载用户标签
const loadUserTags = async (userId) => {
  try {
    const res = await getUserTags(userId)
    const tags = res.data.data.tags
    tagStats.value = tagStats.value.map(stat => {
      const count = tags.filter(tag => tag.category === stat.key).length
      return { ...stat, count }
    })
  } catch (error) {
    tagStats.value = tagStats.value.map(stat => ({ ...stat, count: 0 }))
  }
}

// 加载推荐内容
const loadRecommendedContent = async () => {
  try {
    const userId = userStore.userInfo?.id
    if (!userId) {
      console.log('用户未登录，无法加载推荐内容')
      recommendations.value = []
      return
    }
    
    console.log('🎯 开始加载推荐内容，用户ID:', userId)
    
    // 获取用户标签
    const userRes = await api.get(`/users/${userId}/tags`)
    console.log('📥 用户标签响应:', userRes.data)
    
    const userTags = userRes.data.data?.tags || []
    
    if (userTags.length === 0) {
      console.log('⚠️ 用户无标签，无法生成推荐')
      recommendations.value = []
      return
    }
    
    console.log('🏷️ 用户标签:', userTags)
    
    // 调用个性化推荐API
    const res = await api.get(`/users/${userId}/recommendations`, {
      params: {
        page: 1,
        page_size: 10
      }
    })
    
    console.log('📄 推荐内容响应:', res.data)
    
    if (res.data && res.data.items) {
      recommendations.value = res.data.items || []
      console.log('✅ 推荐内容加载成功，数量:', recommendations.value.length)
      
      // 应用当前筛选条件
      filterRecommendations()
    } else {
      console.error('❌ 推荐内容加载失败:', res.data?.message || '未知错误')
      recommendations.value = []
      filteredRecommendations.value = []
    }
  } catch (error) {
    console.error('❌ 推荐内容加载异常:', error)
    recommendations.value = []
    filteredRecommendations.value = []
  }
}

// 加载交易公告
const loadAnnouncements = async () => {
  try {
    // 拉取所有内容，前端筛选basic_info_tags
    const res = await getAnnouncements('', 1, 100)
    const allItems = res.data.items || []
    // 按basic_info_tags筛选
    priceAnnouncements.value = allItems
      .filter(item => (item.basic_info_tags || []).includes('调价公告'))
      .sort((a, b) => new Date(b.publish_time).getTime() - new Date(a.publish_time).getTime())
    tradeAnnouncements.value = allItems
      .filter(item => (item.basic_info_tags || []).includes('交易公告'))
      .sort((a, b) => new Date(b.publish_time).getTime() - new Date(a.publish_time).getTime())
  } catch (error) {
    priceAnnouncements.value = []
    tradeAnnouncements.value = []
  }
}

// 加载内容统计
const loadContentStats = async () => {
  try {
    console.log('📊 开始加载内容统计...')
    
    // 获取所有内容进行分类统计
    const contentRes = await api.get('/content/', {
      params: {
        page: 1,
        page_size: 100,
        sort_by: 'latest'
      }
    })
    
    const allContent = contentRes.data.items || []
    console.log('📄 获取到内容总数:', allContent.length)
    
    // 按分类统计
    const marketCount = allContent.filter(item => 
      (item.basic_info_tags || []).includes('行业资讯')
    ).length
    
    const policyCount = allContent.filter(item => 
      (item.basic_info_tags || []).includes('政策法规')
    ).length
    
    const announcementCount = allContent.filter(item => 
      (item.basic_info_tags || []).includes('交易公告') ||
      (item.basic_info_tags || []).includes('调价公告')
    ).length
    
    contentStats.value = [
      { title: '行情', value: marketCount, type: 'news' },
      { title: '政策', value: policyCount, type: 'policy' },
      { title: '公告', value: announcementCount, type: 'announcement' }
    ]
    
    console.log('✅ 内容统计完成:', {
      market: marketCount,
      policy: policyCount,
      announcement: announcementCount
    })
    
  } catch (error) {
    console.error('❌ 加载内容统计失败:', error)
    contentStats.value = [
      { title: '行情', value: 0, type: 'news' },
      { title: '政策', value: 0, type: 'policy' },
      { title: '公告', value: 0, type: 'announcement' }
    ]
  }
}

// 刷新推荐内容
const refreshRecommendations = () => {
  const userId = userStore.userInfo?.id
  if (userId) {
    loadRecommendedContent()
  }
}

// 刷新行情数据
const refreshMarketData = () => {
  // TODO: 实现行情数据刷新逻辑
  console.log('刷新行情数据')
}

// 页面跳转方法
const handleQuickLink = (route: string) => {
  router.push(route)
}

const goToTags = () => {
  router.push('/tags')
}

const goToContent = () => {
  router.push('/content')
}

const goToContentByType = (contentType: string) => {
  router.push({
    path: '/content',
    query: { type: contentType }
  })
}

const goToMarket = () => {
  router.push('/market')
}

// 设置推荐筛选
const setRecommendationFilter = (filter: string) => {
  recommendationFilter.value = filter
  filterRecommendations()
}

// 筛选推荐内容
const filterRecommendations = () => {
  if (recommendationFilter.value === 'all') {
    filteredRecommendations.value = recommendations.value
    return
  }
  
  filteredRecommendations.value = recommendations.value.filter(item => {
    const basicInfoTags = item.basic_info_tags || []
    
    switch (recommendationFilter.value) {
      case 'market':
        // 行情：精确匹配"行业资讯"标签
        return basicInfoTags.includes('行业资讯')
      case 'policy':
        // 政策：精确匹配"政策法规"标签
        return basicInfoTags.includes('政策法规')
      case 'announcement':
        // 公告：匹配"交易公告"或"调价公告"标签
        return basicInfoTags.includes('交易公告') || 
               basicInfoTags.includes('调价公告')
      default:
        return true
    }
  })
}

// 获取空状态描述
const getEmptyDescription = () => {
  switch (recommendationFilter.value) {
    case 'market':
      return '暂无行情类推荐内容'
    case 'policy':
      return '暂无政策类推荐内容' 
    case 'announcement':
      return '暂无公告类推荐内容'
    default:
      return '暂无推荐内容'
  }
}

onMounted(() => {
  // 登录态校验
  if (!userStore.token) {
    const token = localStorage.getItem('token')
    const userInfo = localStorage.getItem('userInfo')
    if (token && userInfo) {
      userStore.setToken(token)
      userStore.setUserInfo(JSON.parse(userInfo))
    } else {
      router.push('/login')
      return
    }
  }
  // 加载数据
  const userId = userStore.userInfo?.id
  if (userId) {
    loadUserTags(userId)
    loadRecommendedContent()
  }
  loadAnnouncements()
  loadContentStats()
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  max-width: 1280px;
  margin: 0 auto;
}

.welcome-card {
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  color: white;
  margin-bottom: 20px;
}

.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.welcome-left h2 {
  margin: 0;
  font-size: 24px;
}

.text-gray-600 {
  color: rgba(255, 255, 255, 0.8);
}

.quick-link-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.quick-link-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.quick-link-icon {
  font-size: 32px;
  margin-bottom: 12px;
  color: #1890ff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #ebeef5;
}

.tag-stats {
  padding: 20px;
  min-height: 200px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 16px;
}

.stat-item h3 {
  margin: 0;
  font-size: 24px;
  color: #1890ff;
}

.stat-item p {
  margin: 8px 0 0;
  color: #666;
}

.recommendation-card {
  margin-bottom: 16px;
}

.recommendation-card h4 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #303133;
}

.tags {
  margin-top: 12px;
}

.announcement-item {
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
}

.announcement-item:last-child {
  border-bottom: none;
}

.announcement-item h4 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #303133;
}

.mb-4 {
  margin-bottom: 16px;
}

.mr-2 {
  margin-right: 8px;
}

:deep(.el-card__header) {
  padding: 0;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-timeline-item__node) {
  background-color: #1890ff;
}

:deep(.el-timeline-item__tail) {
  border-left: 2px solid #e4e7ed;
}

:deep(.el-statistic__head) {
  margin-bottom: 8px;
}

:deep(.el-statistic__content) {
  color: #1890ff;
}

.market-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px #e4e7ed33;
  margin-bottom: 24px;
}
.market-item-new {
  height: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  box-shadow: none;
  transition: box-shadow 0.2s;
  cursor: pointer;
  margin-bottom: 0;
  padding: 8px 0;
}
.market-item-new:hover {
  box-shadow: 0 4px 16px 0 rgba(24,144,255,0.12);
}
.market-name {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 4px;
  color: #333;
  text-align: center;
}
.market-price-main {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 2px;
  text-align: center;
}
.market-price-main.up {
  color: #67c23a;
}
.market-price-main.down {
  color: #f56c6c;
}
.market-change {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
  text-align: center;
  border-radius: 4px;
  padding: 2px 8px;
  display: inline-block;
}
.market-change.up {
  color: #67c23a;
  background: #f0f9eb;
}
.market-change.down {
  color: #f56c6c;
  background: #fef0f0;
}
.market-info-row {
  display: flex;
  justify-content: space-between;
  width: 100%;
  font-size: 12px;
  color: #888;
  margin-top: 4px;
  padding: 0 4px;
}
.more-item-new {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: #f5f7fa;
  height: 180px;
}
.more-item-new:hover {
  box-shadow: 0 2px 12px 0 rgba(24,144,255,0.12);
  background: #e6f7ff;
}
.more-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.more-text {
  margin-top: 8px;
  font-size: 16px;
  color: #1890ff;
  font-weight: bold;
}

.market-card-enhanced {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px #e4e7ed33;
  margin-bottom: 24px;
}

.market-header-enhanced {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.market-icon {
  font-size: 24px;
  margin-right: 8px;
  color: #1890ff;
}

.market-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.market-content-enhanced {
  padding: 20px;
}

.market-item-enhanced {
  height: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  box-shadow: none;
  transition: box-shadow 0.2s;
  cursor: pointer;
  margin-bottom: 0;
  padding: 8px 0;
}

.market-item-enhanced:hover {
  box-shadow: 0 4px 16px 0 rgba(24,144,255,0.12);
}

.market-item-content {
  text-align: center;
}

.market-name {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 4px;
  color: #333;
}

.market-price-main {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 2px;
  text-align: center;
}

.market-price-main.up {
  color: #67c23a;
}

.market-price-main.down {
  color: #f56c6c;
}

.market-change-enhanced {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
  text-align: center;
  border-radius: 4px;
  padding: 2px 8px;
  display: inline-block;
}

.market-change-enhanced.up {
  color: #67c23a;
  background: #f0f9eb;
}

.market-change-enhanced.down {
  color: #f56c6c;
  background: #fef0f0;
}

.market-volume {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
}

.market-more-enhanced {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: #f5f7fa;
  height: 180px;
}

.market-more-enhanced:hover {
  box-shadow: 0 2px 12px 0 rgba(24,144,255,0.12);
  background: #e6f7ff;
}

.more-content-enhanced {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.more-text {
  margin-top: 8px;
  font-size: 16px;
  color: #1890ff;
  font-weight: bold;
}

.more-desc {
  margin-top: 8px;
  font-size: 12px;
  color: #888;
}

.more-icon {
  font-size: 24px;
  margin-right: 8px;
  color: #1890ff;
}

.stat-overview-item {
  text-align: center;
  padding: 16px 8px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.stat-overview-item:hover {
  background: #e6f7ff;
  border-color: #1890ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px 0 rgba(24,144,255,0.15);
}

.stat-overview-item h3 {
  margin: 0;
  font-size: 24px;
  color: #1890ff;
  font-weight: bold;
}

.stat-overview-item p {
  margin: 8px 0 0;
  color: #666;
  font-size: 14px;
}

.stat-item-compact {
  text-align: center;
  padding: 12px 8px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 8px;
  transition: all 0.2s;
}

.stat-item-compact:hover {
  background: #e6f7ff;
  transform: translateY(-1px);
}

.stat-item-compact h4 {
  margin: 0;
  font-size: 18px;
  color: #1890ff;
  font-weight: bold;
}

.stat-item-compact p {
  margin: 4px 0 0;
  color: #666;
  font-size: 12px;
}

/* 推荐筛选样式 */
.recommendation-filter {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.recommendations {
  min-height: 400px;
}

.announcements {
  min-height: 150px;
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