<template>
  <div class="dashboard-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>🏷️ 标签管理</h1>
        <p>管理文章标签和分类系统</p>
      </div>
    </div>

    <!-- 标签统计 -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon">🔥</div>
        <div class="stat-content">
          <h3>{{ tagStats.energy_types || 0 }}</h3>
          <p>能源类型标签</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🌍</div>
        <div class="stat-content">
          <h3>{{ tagStats.regions || 0 }}</h3>
          <p>地区标签</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <h3>{{ tagStats.total_articles || 0 }}</h3>
          <p>已标记文章</p>
        </div>
      </div>
    </div>

    <!-- 标签分类展示 -->
    <div class="tags-container">
      <!-- 能源类型标签 -->
      <div class="tag-section">
        <h2>🔥 能源类型标签</h2>
        <div class="tags-grid">
          <div 
            v-for="tag in energyTags" 
            :key="tag.name"
            class="tag-item energy-tag"
          >
            <span class="tag-name">{{ tag.name }}</span>
            <span class="tag-count">{{ tag.count }} 篇文章</span>
          </div>
        </div>
      </div>

      <!-- 地区标签 -->
      <div class="tag-section">
        <h2>🌍 地区标签</h2>
        <div class="tags-grid">
          <div 
            v-for="tag in regionTags" 
            :key="tag.name"
            class="tag-item region-tag"
          >
            <span class="tag-name">{{ tag.name }}</span>
            <span class="tag-count">{{ tag.count }} 篇文章</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">🔄</div>
      <p>加载中...</p>
    </div>

    <!-- 页面宽度占位符 - 不可见但确保页面宽度一致 -->
    <div class="width-placeholder" aria-hidden="true"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAdminStore } from '@/store/admin'

const adminStore = useAdminStore()

// 响应式数据
const loading = ref(false)
const tagStats = ref({
  energy_types: 0,
  regions: 0,
  total_articles: 0
})
const energyTags = ref<Array<{name: string, count: number}>>([])
const regionTags = ref<Array<{name: string, count: number}>>([])

// 加载标签数据
const loadTagsData = async () => {
  try {
    loading.value = true
    
    // 获取文章数据来统计标签
    const response = await adminStore.getArticles({ page: 1, page_size: 1000 })
    const articles = response.articles
    
    // 统计能源类型标签
    const energyTagMap = new Map<string, number>()
    const regionTagMap = new Map<string, number>()
    
    articles.forEach((article: any) => {
      // 统计能源类型标签
      if (article.energy_type_tags) {
        article.energy_type_tags.forEach((tag: string) => {
          energyTagMap.set(tag, (energyTagMap.get(tag) || 0) + 1)
        })
      }
      
      // 统计地区标签
      if (article.region_tags) {
        article.region_tags.forEach((tag: string) => {
          regionTagMap.set(tag, (regionTagMap.get(tag) || 0) + 1)
        })
      }
    })
    
    // 转换为数组并排序
    energyTags.value = Array.from(energyTagMap.entries())
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
    
    regionTags.value = Array.from(regionTagMap.entries())
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
    
    // 更新统计数据
    tagStats.value = {
      energy_types: energyTags.value.length,
      regions: regionTags.value.length,
      total_articles: articles.length
    }
    
  } catch (error: any) {
    console.error('加载标签数据失败:', error)
    alert('加载标签数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadTagsData()
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  max-width: 1280px;
  margin: 0 auto;
  background: #f5f7fa;
}

.page-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left h1 {
  margin: 0 0 8px 0;
  color: #2d3748;
  font-size: 24px;
  font-weight: 600;
}

.header-left p {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #edf2f7;
  border-radius: 12px;
}

.stat-content h3 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 600;
  color: #2d3748;
}

.stat-content p {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

.tags-container {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.tag-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tag-section h2 {
  margin: 0 0 20px 0;
  color: #2d3748;
  font-size: 20px;
  font-weight: 600;
}

.tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.tag-item {
  background: #f7fafc;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  transition: all 0.2s;
}

.tag-item:hover {
  border-color: #4299e1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.15);
}

.tag-item.energy-tag:hover {
  border-color: #ed8936;
  box-shadow: 0 4px 12px rgba(237, 137, 54, 0.15);
}

.tag-item.region-tag:hover {
  border-color: #38b2ac;
  box-shadow: 0 4px 12px rgba(56, 178, 172, 0.15);
}

.tag-name {
  display: block;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 8px;
  font-size: 16px;
}

.tag-count {
  display: block;
  color: #718096;
  font-size: 14px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.loading-spinner {
  font-size: 48px;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }
  
  .stats-section {
    grid-template-columns: 1fr;
  }
  
  .tags-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style> 