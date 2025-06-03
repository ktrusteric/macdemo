<template>
  <div class="dashboard-container">
    <!-- 统计卡片 -->
    <div class="stats-grid" v-if="stats">
      <div class="stat-card">
        <div class="stat-icon">📄</div>
        <div class="stat-content">
          <h3>{{ totalArticles }}</h3>
          <p>总文章数</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <h3>{{ stats.users.total }}</h3>
          <p>总用户数</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🔧</div>
        <div class="stat-content">
          <h3>{{ stats.users.admins }}</h3>
          <p>管理员数</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <h3>{{ stats.users.regular }}</h3>
          <p>普通用户</p>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2>🚀 快速操作</h2>
      <div class="actions-grid">
        <router-link to="/admin/articles" class="action-card">
          <div class="action-icon">📝</div>
          <h3>文章管理</h3>
          <p>管理系统中的所有文章内容</p>
        </router-link>
        
        <router-link to="/admin/users" class="action-card">
          <div class="action-icon">👥</div>
          <h3>用户管理</h3>
          <p>管理系统用户和权限</p>
        </router-link>
        
        <div @click="showImportModal = true" class="action-card clickable">
          <div class="action-icon">📦</div>
          <h3>批量导入</h3>
          <p>批量导入文章数据</p>
        </div>
        
        <div @click="refreshStats" class="action-card clickable">
          <div class="action-icon">🔄</div>
          <h3>刷新统计</h3>
          <p>更新系统统计数据</p>
        </div>
      </div>
    </div>

    <!-- 文章类型统计 -->
    <div class="article-stats" v-if="stats?.articles.by_type">
      <h2>📊 文章类型分布</h2>
      <div class="type-stats-grid">
        <div 
          v-for="(count, type) in stats.articles.by_type" 
          :key="type"
          class="type-stat-card"
        >
          <div class="type-name">{{ contentTypeMap[String(type)] || type }}</div>
          <div class="type-count">{{ count }}</div>
          <div class="type-percentage">
            {{ ((count / totalArticles) * 100).toFixed(1) }}%
          </div>
        </div>
      </div>
    </div>

    <!-- 批量导入模态框 -->
    <div v-if="showImportModal" class="modal-overlay" @click="showImportModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>📦 批量导入文章</h3>
          <button @click="showImportModal = false" class="close-btn">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="import-section">
            <h4>选择导入文件</h4>
            <input 
              type="file" 
              accept=".json"
              @change="handleFileSelect"
              class="file-input"
            />
            <p class="file-hint">请选择JSON格式的文章数据文件</p>
          </div>
          
          <div class="import-options">
            <h4>导入选项</h4>
            <label class="option-item">
              <input 
                type="checkbox" 
                v-model="importOptions.overwrite_existing"
              />
              覆盖已存在的文章
            </label>
            <label class="option-item">
              <input 
                type="checkbox" 
                v-model="importOptions.validate_tags"
              />
              验证标签格式
            </label>
          </div>
          
          <div class="modal-actions">
            <button @click="showImportModal = false" class="cancel-btn">
              取消
            </button>
            <button 
              @click="handleImport" 
              :disabled="!selectedFile || importing"
              class="import-btn"
            >
              <span v-if="importing">📦 导入中...</span>
              <span v-else>📦 开始导入</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 页面宽度占位符 - 不可见但确保页面宽度一致 -->
    <div class="width-placeholder" aria-hidden="true"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAdminStore } from '@/store/admin'
import tagService from '@/services/tagService'

const adminStore = useAdminStore()

// 响应式数据
const loading = ref(false)
const stats = ref<any>(null)
const showImportModal = ref(false)
const selectedFile = ref<File | null>(null)
const importing = ref(false)
const isDragOver = ref(false)
const recentArticles = ref<any[]>([])
const contentTypeMap = ref<Record<string, string>>({})

// 计算属性
const totalArticles = computed(() => stats.value?.articles?.total || 0)
const totalViews = computed(() => stats.value?.total_views || 0)
const typeDistribution = computed(() => stats.value?.articles?.by_type || {})
const totalUsers = computed(() => stats.value?.users?.total || 0)
const adminUsers = computed(() => stats.value?.users?.admins || 0)
const regularUsers = computed(() => stats.value?.users?.regular_users || 0)

const importOptions = ref({
  overwrite_existing: false,
  validate_tags: true
})

// 获取类型显示名称
const getTypeDisplayName = (type: string) => {
  const typeMap: Record<string, string> = {
    'policy': '政策法规',
    'news': '行业资讯',
    'price': '调价公告',
    'announcement': '交易公告'
  }
  return typeMap[type] || type
}

// 加载统计数据
const loadStats = async () => {
  try {
    loading.value = true
    stats.value = await adminStore.getStats()
  } catch (error: any) {
    console.error('加载统计数据失败:', error)
    alert('加载统计数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 刷新统计数据
const refreshStats = async () => {
  await loadStats()
  alert('✅ 统计数据已刷新')
}

// 文件选择处理
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
  }
}

// 文件拖拽处理
const handleFileDrop = (event: DragEvent) => {
  isDragOver.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    selectedFile.value = event.dataTransfer.files[0]
  }
}

// 批量导入处理
const handleImport = async () => {
  if (!selectedFile.value) return
  
  try {
    importing.value = true
    const result = await adminStore.importFromJsonFile(selectedFile.value, importOptions.value)
    
    alert(`✅ 导入完成!\n总计: ${result.total_articles}\n成功: ${result.imported_count}\n更新: ${result.updated_count}\n失败: ${result.failed_count}`)
    
    showImportModal.value = false
    selectedFile.value = null
    await loadStats() // 刷新统计数据
    
  } catch (error: any) {
    console.error('批量导入失败:', error)
    alert('❌ 批量导入失败: ' + error.message)
  } finally {
    importing.value = false
  }
}

// 组件挂载时加载数据
onMounted(async () => {
  try {
    // 加载内容类型映射
    contentTypeMap.value = await tagService.getContentTypeMap()
    
    // 加载统计数据
    await loadStats()
  } catch (error) {
    console.error('初始化失败:', error)
    await loadStats() // 确保至少加载统计数据
  }
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  max-width: 1280px;
  margin: 0 auto;
  background: #f5f7fa;
}

.stats-grid {
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

.quick-actions, .article-stats {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.quick-actions h2, .article-stats h2 {
  margin: 0 0 20px 0;
  color: #2d3748;
  font-size: 20px;
  font-weight: 600;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.action-card {
  background: #f7fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
  text-align: center;
}

.action-card:hover {
  border-color: #4299e1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.15);
}

.action-card.clickable {
  cursor: pointer;
}

.action-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.action-card h3 {
  margin: 0 0 8px 0;
  color: #2d3748;
  font-size: 16px;
  font-weight: 600;
}

.action-card p {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

.type-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.type-stat-card {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.type-name {
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 8px;
}

.type-count {
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 4px;
}

.type-percentage {
  font-size: 12px;
  color: #718096;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #2d3748;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #718096;
}

.modal-body {
  padding: 24px;
}

.import-section {
  margin-bottom: 20px;
}

.import-section h4 {
  margin: 0 0 12px 0;
  color: #2d3748;
  font-size: 16px;
  font-weight: 600;
}

.file-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 8px;
}

.file-hint {
  font-size: 12px;
  color: #a0aec0;
  margin: 0;
}

.import-options {
  margin-bottom: 24px;
}

.import-options h4 {
  margin: 0 0 12px 0;
  color: #2d3748;
  font-size: 16px;
  font-weight: 600;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  color: #4a5568;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cancel-btn {
  background: #4a5568;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.cancel-btn:hover {
  background: #2d3748;
}

.import-btn {
  background: #48bb78;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.import-btn:hover:not(:disabled) {
  background: #38a169;
}

.import-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
}
</style> 