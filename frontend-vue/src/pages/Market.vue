<template>
  <div class="dashboard-container">
    <div class="header-section">
      <h1 class="page-title">
        <el-icon class="title-icon"><TrendCharts /></el-icon>
        能源行情中心
      </h1>
      <p class="page-subtitle">实时监控能源市场价格动态，助力投资决策</p>
      <div class="refresh-info">
        <el-tag type="success" size="small">实时更新</el-tag>
        <span class="update-time">{{ updateTime }}</span>
        <el-button 
          type="primary" 
          size="small" 
          :icon="Refresh" 
          circle 
          @click="refreshData"
          :loading="refreshing"
        />
      </div>
    </div>

    <!-- 市场概览统计 -->
    <el-row class="stats-row" :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="涨跌幅最大" :value="maxChangeItem.change" :precision="1" suffix="%">
            <template #title>
              <div style="display: inline-flex; align-items: center">
                <el-icon style="margin-right: 4px; color: #f56c6c"><ArrowUp /></el-icon>
                涨跌幅最大
              </div>
            </template>
          </el-statistic>
          <div class="stat-desc">{{ maxChangeItem.name }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="上涨品种" :value="upCount">
            <template #title>
              <div style="display: inline-flex; align-items: center">
                <el-icon style="margin-right: 4px; color: #67c23a"><TrendCharts /></el-icon>
                上涨品种
              </div>
            </template>
          </el-statistic>
          <div class="stat-desc">{{ marketData.length }} 个品种中</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="下跌品种" :value="downCount">
            <template #title>
              <div style="display: inline-flex; align-items: center">
                <el-icon style="margin-right: 4px; color: #f56c6c"><Bottom /></el-icon>
                下跌品种
              </div>
            </template>
          </el-statistic>
          <div class="stat-desc">{{ marketData.length }} 个品种中</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="平均涨跌" :value="avgChange" :precision="2" suffix="%">
            <template #title>
              <div style="display: inline-flex; align-items: center">
                <el-icon style="margin-right: 4px; color: #909399"><DataAnalysis /></el-icon>
                平均涨跌
              </div>
            </template>
          </el-statistic>
          <div class="stat-desc">市场整体表现</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 行情数据展示 -->
    <el-card class="market-list-card">
      <template #header>
        <div class="card-header">
          <span style="font-weight: bold; font-size: 16px;">市场行情</span>
          <div class="header-controls">
            <el-select v-model="sortBy" placeholder="排序方式" size="small" style="width: 120px; margin-right: 10px;">
              <el-option label="按名称" value="name" />
              <el-option label="按价格" value="price" />
              <el-option label="按涨跌幅" value="change" />
            </el-select>
            <el-switch
              v-model="showDetailed"
              active-text="详细"
              inactive-text="简洁"
              size="small"
            />
          </div>
        </div>
      </template>
      
      <div class="market-list">
        <el-row :gutter="20">
          <el-col :span="8" v-for="(item, index) in sortedMarketData" :key="item.name">
            <div class="market-item-wrapper" @click="showItemDetail(item)">
              <el-card 
                class="market-item-enhanced" 
                :class="{ 
                  'up': item.change > 0, 
                  'down': item.change < 0,
                  'flat': item.change === 0 
                }"
                shadow="hover"
              >
                <div class="market-header">
                  <div class="market-name">{{ item.name }}</div>
                  <div class="market-trend-icon">
                    <el-icon v-if="item.change > 0" class="trend-up"><CaretTop /></el-icon>
                    <el-icon v-else-if="item.change < 0" class="trend-down"><CaretBottom /></el-icon>
                    <el-icon v-else class="trend-flat"><Minus /></el-icon>
                  </div>
                </div>
                
                <div class="market-price-section">
                  <div class="market-price-main" :class="{ 'up': item.change > 0, 'down': item.change < 0 }">
                    {{ item.price }}
                  </div>
                  <div class="market-change" :class="{ 'up': item.change > 0, 'down': item.change < 0 }">
                    {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
                  </div>
                </div>
                
                <div class="market-info-section" v-if="showDetailed">
                  <div class="info-row">
                    <span class="info-label">最高</span>
                    <span class="info-value high">{{ item.high }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">最低</span>
                    <span class="info-value low">{{ item.low }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">成交量</span>
                    <span class="info-value volume">{{ item.volume }}</span>
                  </div>
                </div>
                
                <div class="market-progress" v-if="showDetailed">
                  <el-progress 
                    :percentage="getProgressPercentage(item)" 
                    :color="item.change > 0 ? '#67c23a' : '#f56c6c'"
                    :show-text="false"
                    :stroke-width="4"
                  />
                  <div class="progress-labels">
                    <span class="low-label">{{ item.low }}</span>
                    <span class="high-label">{{ item.high }}</span>
                  </div>
                </div>
              </el-card>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="dialogVisible" :title="selectedItem?.name" width="600px">
      <div v-if="selectedItem" class="item-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="当前价格">
            <span :class="{ 'up': selectedItem.change > 0, 'down': selectedItem.change < 0 }" style="font-weight: bold; font-size: 18px;">
              {{ selectedItem.price }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="涨跌幅">
            <el-tag :type="selectedItem.change > 0 ? 'success' : 'danger'" size="large">
              {{ selectedItem.change > 0 ? '+' : '' }}{{ selectedItem.change }}%
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最高价">{{ selectedItem.high }}</el-descriptions-item>
          <el-descriptions-item label="最低价">{{ selectedItem.low }}</el-descriptions-item>
          <el-descriptions-item label="成交量" :span="2">{{ selectedItem.volume }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 页面宽度占位符 - 不可见但确保页面宽度一致 -->
    <div class="width-placeholder" aria-hidden="true"></div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
  TrendCharts, 
  Refresh, 
  ArrowUp, 
  Bottom, 
  DataAnalysis,
  CaretTop,
  CaretBottom,
  Minus
} from '@element-plus/icons-vue'

// 响应式数据
const refreshing = ref(false)
const updateTime = ref('')
const sortBy = ref('name')
const showDetailed = ref(true)
const dialogVisible = ref(false)
const selectedItem = ref(null)

const marketData = ref([
  {
    name: '管道天然气(PNG)',
    price: '3.85元/立方米',
    change: 2.5,
    high: '3.92元/立方米',
    low: '3.75元/立方米',
    volume: '1.2亿立方米'
  },
  {
    name: '液化天然气(LNG)',
    price: '4.25元/立方米',
    change: -1.2,
    high: '4.35元/立方米',
    low: '4.15元/立方米',
    volume: '0.8亿立方米'
  },
  {
    name: '原油',
    price: '78.5美元/桶',
    change: 0.8,
    high: '79.2美元/桶',
    low: '77.8美元/桶',
    volume: '150万桶'
  },
  {
    name: '液化石油气(LPG)',
    price: '5.2元/千克',
    change: 1.5,
    high: '5.3元/千克',
    low: '5.1元/千克',
    volume: '50万吨'
  },
  {
    name: '汽油',
    price: '7.85元/升',
    change: -0.5,
    high: '7.95元/升',
    low: '7.75元/升',
    volume: '200万吨'
  },
  {
    name: '柴油',
    price: '7.45元/升',
    change: 0.3,
    high: '7.55元/升',
    low: '7.35元/升',
    volume: '180万吨'
  }
])

// 计算属性
const sortedMarketData = computed(() => {
  const data = [...marketData.value]
  switch (sortBy.value) {
    case 'price':
      return data.sort((a, b) => parseFloat(a.price) - parseFloat(b.price))
    case 'change':
      return data.sort((a, b) => b.change - a.change)
    default:
      return data.sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'))
  }
})

const upCount = computed(() => 
  marketData.value.filter(item => item.change > 0).length
)

const downCount = computed(() => 
  marketData.value.filter(item => item.change < 0).length
)

const avgChange = computed(() => {
  const total = marketData.value.reduce((sum, item) => sum + item.change, 0)
  return total / marketData.value.length
})

const maxChangeItem = computed(() => {
  return marketData.value.reduce((max, item) => 
    Math.abs(item.change) > Math.abs(max.change) ? item : max
  )
})

// 方法
const refreshData = async () => {
  refreshing.value = true
  try {
    // 模拟数据刷新
    await new Promise(resolve => setTimeout(resolve, 1000))
    updateTime.value = new Date().toLocaleTimeString('zh-CN')
    console.log('🔄 市场数据已刷新')
  } finally {
    refreshing.value = false
  }
}

const getProgressPercentage = (item: any) => {
  const current = parseFloat(item.price)
  const low = parseFloat(item.low)
  const high = parseFloat(item.high)
  return ((current - low) / (high - low)) * 100
}

const showItemDetail = (item: any) => {
  selectedItem.value = item
  dialogVisible.value = true
}

const updateTimeStamp = () => {
  updateTime.value = new Date().toLocaleTimeString('zh-CN')
}

// 生命周期
onMounted(() => {
  updateTimeStamp()
  // 每30秒更新一次时间戳（模拟实时更新）
  setInterval(updateTimeStamp, 30000)
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
  margin-bottom: 16px;
}

.refresh-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 16px;
}

.update-time {
  font-size: 14px;
  color: #909399;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-radius: 12px;
  transition: all 0.3s ease;
  border: none;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

.stat-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.market-list {
  min-height: 600px;
}

.market-list-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  min-height: 500px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.market-item-wrapper {
  margin-bottom: 20px;
  cursor: pointer;
}

.market-item-enhanced {
  height: auto;
  min-height: 160px;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  background: white;
  overflow: hidden;
  margin-bottom: 16px;
}

.market-item-enhanced:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(24,144,255,0.15);
  border-color: #1890ff;
}

.market-item-enhanced.up {
  background: linear-gradient(135deg, #fff 0%, #f0f9eb 100%);
  border-color: #67c23a;
}

.market-item-enhanced.down {
  background: linear-gradient(135deg, #fff 0%, #fef0f0 100%);
  border-color: #f56c6c;
}

.market-item-enhanced.flat {
  background: linear-gradient(135deg, #fff 0%, #f5f7fa 100%);
  border-color: #909399;
}

.market-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.market-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.market-trend-icon {
  font-size: 20px;
}

.trend-up { color: #67c23a; }
.trend-down { color: #f56c6c; }
.trend-flat { color: #909399; }

.market-price-section {
  text-align: center;
  margin-bottom: 16px;
}

.market-price-main {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 6px;
  color: #333;
}

.market-price-main.up { color: #67c23a; }
.market-price-main.down { color: #f56c6c; }

.market-change {
  font-size: 14px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 16px;
  display: inline-block;
}

.market-change.up {
  color: #67c23a;
  background: rgba(103, 194, 58, 0.1);
}

.market-change.down {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

.market-info-section {
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-size: 13px;
}

.info-label {
  color: #666;
  font-weight: 500;
}

.info-value {
  font-weight: 600;
}

.info-value.high { color: #67c23a; }
.info-value.low { color: #f56c6c; }
.info-value.volume { color: #1890ff; }

.market-progress {
  margin-top: 12px;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 11px;
  color: #909399;
}

.item-detail {
  padding: 20px 0;
}

.up { color: #67c23a; }
.down { color: #f56c6c; }

/* 动画效果 */
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

.market-item-enhanced {
  animation: fadeInUp 0.6s ease;
}

.stat-card {
  animation: fadeInUp 0.4s ease;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-section {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .market-item-enhanced {
    margin-bottom: 16px;
  }
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