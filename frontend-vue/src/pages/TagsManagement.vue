<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="header-section">
      <h1 class="page-title">
        <el-icon class="title-icon"><PriceTag /></el-icon>
        个人标签管理
      </h1>
      <p class="page-subtitle">管理您的兴趣标签，获得更精准的内容推荐</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && !tags.length" class="loading-container">
      <el-skeleton animated>
        <template #template>
          <el-skeleton-item variant="h1" />
          <el-skeleton-item variant="text" />
          <el-skeleton-item variant="text" />
        </template>
      </el-skeleton>
    </div>

    <!-- 错误提示 -->
    <el-alert 
      v-if="error" 
      :title="error" 
      type="error" 
      show-icon 
      class="error-alert"
      @close="error = ''"
    />

    <!-- 统计概览 -->
    <el-row :gutter="20" class="stats-section" v-if="!loading">
      <el-col :span="6">
        <el-card class="stat-card total-stat">
          <el-statistic title="标签总数" :value="totalTagsCount" />
          <div class="stat-icon">🏷️</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card categories-stat">
          <el-statistic title="启用分类" :value="activeCategoriesCount" />
          <div class="stat-icon">📂</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card weight-stat">
          <el-statistic title="总权重" :value="totalWeight" :precision="1" />
          <div class="stat-icon">⚖️</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card sync-stat">
          <el-statistic title="最后更新" :value="lastUpdateTime" />
          <div class="stat-icon">🔄</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 标签预览 -->
    <el-card class="preview-card" v-if="tags.length">
      <template #header>
        <span class="preview-title">我的标签</span>
      </template>
      <div class="preview-content">
        <div class="all-tags-cloud">
          <el-tag
            v-for="tag in sortedTagsForPreview"
            :key="`preview-${tag.category}-${tag.name}`"
            :type="getTagTypeByCategory(tag.category)"
            :size="getTagSizeByWeight(tag.weight)"
            :effect="tag.source === 'preset' ? 'dark' : 'plain'"
            class="preview-tag"
          >
            {{ tag.name }}
            <el-icon class="tag-weight-icon" v-if="tag.weight > 1.0"><Star /></el-icon>
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 快捷操作 -->
    <el-card class="action-card">
      <div class="action-header">
        <span class="action-title">快捷操作</span>
        <div class="action-buttons">
          <el-tooltip content="从服务器重新加载您的标签数据" placement="top">
            <el-button 
              type="primary" 
              @click="fetchTags" 
              :loading="loading"
              icon="Refresh"
            >
              刷新标签
            </el-button>
          </el-tooltip>
          <el-tooltip content="将当前修改保存到服务器" placement="top">
            <el-button 
              type="success" 
              @click="saveUserTags" 
              :loading="saving"
              icon="Check"
              :disabled="!hasChanges"
            >
              保存更改
            </el-button>
          </el-tooltip>
          <el-tooltip content="保留注册地、省份、区域和能源产品标签，清理其他标签" placement="top">
            <el-button 
              type="warning"
              @click="resetToDefaults"
              icon="RefreshLeft"
            >
              重置基础
            </el-button>
          </el-tooltip>
          <el-tooltip content="移除重复的标签，保持数据整洁" placement="top">
            <el-button 
              type="info"
              @click="cleanDuplicates"
              icon="Delete"
            >
              清理重复
            </el-button>
          </el-tooltip>
        </div>
      </div>
    </el-card>

    <!-- 标签分类管理 -->
    <el-card class="tags-card">
      <template #header>
        <div class="tags-header">
          <span class="tags-title">标签分类管理</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card" class="tags-tabs">
        <el-tab-pane 
          v-for="category in tagCategories" 
          :key="category.key" 
          :name="category.key"
        >
          <template #label>
            <div class="tab-label">
              <span>{{ category.name }}</span>
              <el-badge 
                :value="getTagsByCategory(category.key).length" 
                :type="getBadgeType(category.key)"
                :hidden="getTagsByCategory(category.key).length === 0"
              />
            </div>
          </template>

          <div class="tab-content">
            <!-- 分类描述 -->
            <div class="category-description">
              <el-icon class="desc-icon"><InfoFilled /></el-icon>
              <span>{{ category.description }}</span>
            </div>

            <!-- 当前标签 -->
            <div class="current-tags-section">
              <h4 class="section-title">当前标签</h4>
              <div class="tags-container" v-if="getTagsByCategory(category.key).length">
                <el-tag
                  v-for="tag in getTagsByCategory(category.key)"
                  :key="`${tag.category}-${tag.name}`"
                  :type="getTagTypeByCategory(category.key)"
                  :effect="tag.source === 'preset' ? 'dark' : 'plain'"
                  closable
                  @close="removeTag(tag)"
                  class="tag-item"
                >
                  <div class="tag-content">
                    <span class="tag-name">{{ tag.name }}</span>
                    <span class="tag-weight">{{ tag.weight }}x</span>
                    <span class="tag-source">{{ getSourceLabel(tag.source) }}</span>
                  </div>
                </el-tag>
              </div>
              <el-empty 
                v-else 
                description="暂无标签，请从预设标签中选择或手动添加"
                :image-size="100"
              />
            </div>

            <!-- 预设标签 -->
            <div class="preset-tags-section">
              <h4 class="section-title">
                预设标签
                <div class="preset-actions">
                  <span class="preset-hint">点击选择 →</span>
                  <el-button 
                    type="primary" 
                    link 
                    @click="addAllPresetTags(category)"
                    size="small"
                  >
                    全部添加
                  </el-button>
                </div>
              </h4>
              <div class="preset-tags-container">
                <el-tag
                  v-for="presetTag in getAvailablePresetTags(category.key)"
                  :key="presetTag"
                  :type="getTagTypeByCategory(category.key)"
                  effect="plain"
                  @click="selectPresetTag(category.key, presetTag)"
                  class="preset-tag-item"
                >
                  <el-icon><Plus /></el-icon>
                  {{ presetTag }}
                </el-tag>
              </div>
            </div>

            <!-- 自定义权重 -->
            <div class="custom-tag-section">
              <h4 class="section-title">自定义权重</h4>
              <div class="custom-tag-input">
                <el-input
                  v-model="newTagInputs[category.key]"
                  :placeholder="`标签名称...`"
                  class="tag-input"
                  @keyup.enter="addCustomTag(category.key)"
                >
                  <template #prepend>
                    <el-icon><PriceTag /></el-icon>
                  </template>
                </el-input>
                <el-input-number
                  v-model="newTagWeight"
                  :min="0.1"
                  :max="5.0"
                  :step="0.1"
                  :precision="1"
                  placeholder="权重"
                  class="weight-input"
                />
                <el-button 
                  type="success" 
                  @click="addCustomTag(category.key)"
                  :disabled="!newTagInputs[category.key] || !newTagInputs[category.key].trim()"
                >
                  添加
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { 
  PriceTag, 
  InfoFilled, 
  Plus, 
  Star,
  Refresh,
  Check,
  RefreshLeft,
  Delete
} from '@element-plus/icons-vue'
import api from '@/api/request'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'

interface UserTag {
  category: string;
  name: string;
  weight: number;
  source: string;
  created_at: string;
}

const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const activeTab = ref('basic_info')
const newTagWeight = ref(1.0)
const hasChanges = ref(false)

// 标签数据
const tags = ref<UserTag[]>([])
const originalTags = ref<UserTag[]>([])
const newTagInputs = reactive<Record<string, string>>({})

// 7大类标签配置 - 与后端完全对应
const tagCategories = ref([
  {
    key: 'basic_info',
    name: '📄 基础信息',
    description: '内容类型和基础属性标签',
    color: 'primary',
    presetTags: ['政策法规', '行业资讯', '交易公告', '调价公告', '研报分析', '价格变动', '科技创新']
  },
  {
    key: 'region',
    name: '🗺️ 地域标签',
    description: '地理区域相关标签（地区、省份、城市）',
    color: 'success',
    presetTags: ['华东地区', '华南地区', '华北地区', '华中地区', '西南地区', '西北地区', '东北地区', '全国', '国际', '中国', '上海市', '北京市', '广东省', '浙江省', '四川省', '湖南省', '湖北省', '江苏省', '天津市', '重庆市', '上海', '北京', '深圳', '广州', '杭州', '成都', '长沙', '武汉', '南京', '苏州', '天津', '重庆', '西安', '郑州', '沈阳', '大连', '青岛', '济南']
  },
  {
    key: 'energy_type',
    name: '⚡ 能源品种',
    description: '能源类型和细分品种标签',
    color: 'warning',
    presetTags: ['原油', '管道天然气(PNG)', '天然气', '液化天然气(LNG)', '液化石油气(LPG)', '汽油', '柴油', '沥青', '石油焦', '生物柴油', '电力', '煤炭', '核能', '可再生能源', '生物质能', '氢能']
  },
  {
    key: 'business_field',
    name: '🏢 业务领域',
    description: '业务类型和关注主题标签',
    color: 'info',
    presetTags: ['市场动态', '价格变化', '交易信息', '科技创新', '政策解读', '国际合作', '投资支持', '民营经济发展', '市场准入优化', '公平竞争']
  },
  {
    key: 'beneficiary',
    name: '👥 受益主体',
    description: '涉及的主体类型标签',
    color: 'danger',
    presetTags: ['能源企业', '政府机构', '交易方', '民营企业', '国有企业', '外资企业', 'LNG交易方', '华东区域用户']
  },
  {
    key: 'policy_measure',
    name: '📋 政策措施',
    description: '政策措施和关键举措标签',
    color: 'success',
    presetTags: ['市场监管', '技术合作', '竞价规则', '投资支持', '市场准入', '创新投融资', '风险管控', '市场准入措施', '价格调整', '区域价格调整']
  },
  {
    key: 'importance',
    name: '⭐ 重要性',
    description: '内容重要程度和影响范围标签',
    color: 'warning',
    presetTags: ['国家级', '权威发布', '重要政策', '行业影响', '常规公告', '国际影响']
  }
])

// 计算属性
const totalTagsCount = computed(() => tags.value.length)
const activeCategoriesCount = computed(() => {
  const categories = new Set(tags.value.map(tag => tag.category))
  return categories.size
})
const totalWeight = computed(() => {
  return tags.value.reduce((sum, tag) => sum + tag.weight, 0)
})
const lastUpdateTime = computed(() => {
  if (!tags.value.length) return '无'
  const dates = tags.value.map(tag => new Date(tag.created_at))
  const latest = new Date(Math.max(...dates.map(d => d.getTime())))
  return latest.toLocaleDateString('zh-CN')
})

const sortedTagsForPreview = computed(() => {
  return [...tags.value].sort((a, b) => b.weight - a.weight)
})

// 工具函数
const getTagsByCategory = (category: string) => {
  return tags.value.filter(tag => tag.category === category)
}

const getAvailablePresetTags = (category: string) => {
  const categoryConfig = tagCategories.value.find(cat => cat.key === category)
  if (!categoryConfig) return []
  
  const existingTagNames = getTagsByCategory(category).map(tag => tag.name)
  return categoryConfig.presetTags.filter(preset => !existingTagNames.includes(preset))
}

const getTagTypeByCategory = (category: string) => {
  const categoryConfig = tagCategories.value.find(cat => cat.key === category)
  return categoryConfig?.color || 'info'
}

const getBadgeType = (category: string) => {
  const count = getTagsByCategory(category).length
  if (count === 0) return 'info'
  if (count <= 2) return 'warning'
  return 'success'
}

const getSourceLabel = (source: string) => {
  switch (source) {
    case 'preset': return '预设'
    case 'manual': return '自定义'
    case 'region_auto': return '自动'
    default: return source
  }
}

const getTagSizeByWeight = (weight: number) => {
  if (weight >= 2.0) return 'large'
  if (weight >= 1.5) return 'default'
  return 'small'
}

// 标签操作方法
const selectPresetTag = (category: string, tagName: string) => {
  // 检查是否已存在
  if (tags.value.find(tag => tag.category === category && tag.name === tagName)) {
    ElMessage.warning('该标签已存在')
    return
  }
  
  // 将标签名称填入输入框
  newTagInputs[category] = tagName
  
  // 给出提示
  ElMessage.success(`已选择"${tagName}"，请调整权重后点击添加`)
}

const addPresetTag = (category: string, tagName: string) => {
  if (tags.value.find(tag => tag.category === category && tag.name === tagName)) {
    ElMessage.warning('该标签已存在')
    return
  }
  
  tags.value.push({
    category,
    name: tagName,
    weight: 1.0,
    source: 'preset',
    created_at: new Date().toISOString()
  })
  
  hasChanges.value = true
  ElMessage.success(`已添加${tagName}`)
}

const addCustomTag = (category: string) => {
  const tagName = newTagInputs[category]?.trim()
  if (!tagName) {
    ElMessage.warning('请输入标签名称')
    return
  }
  
  if (tags.value.find(tag => tag.category === category && tag.name === tagName)) {
    ElMessage.warning('该标签已存在')
    return
  }
  
  // 检查是否为预设标签
  const categoryConfig = tagCategories.value.find(cat => cat.key === category)
  const isPresetTag = categoryConfig?.presetTags.includes(tagName) || false
  
  tags.value.push({
    category,
    name: tagName,
    weight: newTagWeight.value,
    source: isPresetTag ? 'preset' : 'manual',
    created_at: new Date().toISOString()
  })
  
  newTagInputs[category] = ''
  newTagWeight.value = 1.0
  hasChanges.value = true
  ElMessage.success(`已添加${isPresetTag ? '预设' : '自定义'}标签：${tagName}`)
}

const addAllPresetTags = async (category: any) => {
  const result = await ElMessageBox.confirm(
    `确定要添加所有${category.name}的预设标签吗？`,
    '批量添加确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).catch(() => false)
  
  if (!result) return
  
  const availableTags = getAvailablePresetTags(category.key)
  let addedCount = 0
  availableTags.forEach(tagName => {
    if (!tags.value.find(tag => tag.category === category.key && tag.name === tagName)) {
      tags.value.push({
        category: category.key,
        name: tagName,
        weight: 1.0,
        source: 'preset',
        created_at: new Date().toISOString()
      })
      addedCount++
    }
  })
  
  hasChanges.value = true
  ElMessage.success(`已添加${addedCount}个预设标签`)
}

const removeTag = async (tag: UserTag) => {
  const result = await ElMessageBox.confirm(
    `确定要删除标签"${tag.name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).catch(() => false)
  
  if (!result) return
  
  // 找到第一个匹配的标签进行删除（避免删除重复标签时的问题）
  const index = tags.value.findIndex(t => t.category === tag.category && t.name === tag.name)
  if (index !== -1) {
    tags.value.splice(index, 1)
    hasChanges.value = true
    ElMessage.success(`已删除标签：${tag.name}`)
  }
}

const resetToDefaults = async () => {
  const result = await ElMessageBox.confirm(
    '确定要重置标签吗？将保留您的注册地、省份、区域和能源产品标签，清理其他类型标签。',
    '重置确认',
    {
      confirmButtonText: '重置',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).catch(() => false)
  
  if (!result) return
  
  // 保留地域标签和能源类型标签，删除其他标签
  const preservedCategories = ['region', 'energy_type']
  const originalCount = tags.value.length
  
  tags.value = tags.value.filter(tag => preservedCategories.includes(tag.category))
  
  const removedCount = originalCount - tags.value.length
  
  if (removedCount > 0) {
    hasChanges.value = true
    ElMessage.success(`已重置标签，保留${tags.value.length}个基础标签，清理了${removedCount}个其他标签`)
  } else {
    ElMessage.info('当前只有基础标签，无需重置')
  }
}

const cleanDuplicates = () => {
  const originalCount = tags.value.length
  tags.value = deduplicateTags(tags.value)
  const removedCount = originalCount - tags.value.length
  
  if (removedCount > 0) {
    hasChanges.value = true
    ElMessage.success(`已清理${removedCount}个重复标签`)
  } else {
    ElMessage.info('没有发现重复标签')
  }
}

// 去重处理函数
const deduplicateTags = (tagList: UserTag[]) => {
  const seen = new Set()
  return tagList.filter(tag => {
    const key = `${tag.category}-${tag.name}`
    if (seen.has(key)) {
      return false
    }
    seen.add(key)
    return true
  })
}

// API方法
const fetchTags = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const userId = userStore.userInfo?.id
    if (!userId) {
      throw new Error('请先登录')
    }
    
    console.log('🏷️ 获取用户标签 - userId:', userId)
    const response = await api.get(`/users/${userId}/tags`)
    
    if (response.data?.data?.tags) {
      // 处理标签数据并去重
      let rawTags = response.data.data.tags
      
      // 映射标签分类（处理后端可能返回的城市、省份等标签）
      rawTags = rawTags.map(tag => {
        if (['city', 'province'].includes(tag.category)) {
          return { ...tag, category: 'region' }
        }
        return tag
      })
      
      // 去重处理
      tags.value = deduplicateTags(rawTags)
      originalTags.value = JSON.parse(JSON.stringify(tags.value))
      hasChanges.value = false
      
      console.log('✅ 标签加载成功，数量:', tags.value.length)
      ElMessage.success(`成功加载${tags.value.length}个标签`)
    } else {
      tags.value = []
      originalTags.value = []
      ElMessage.info('暂无标签，请添加您感兴趣的标签')
    }
  } catch (e: any) {
    console.error('❌ 获取标签失败:', e)
    error.value = e.response?.data?.message || e.message || '获取标签失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

const saveUserTags = async () => {
  if (!hasChanges.value) {
    ElMessage.info('没有更改需要保存')
    return
  }
  
  saving.value = true
  
  try {
    const userId = userStore.userInfo?.id
    if (!userId) {
      throw new Error('请先登录')
    }
    
    const tagsData = {
      tags: tags.value.map(tag => ({
        category: tag.category,
        name: tag.name,
        weight: tag.weight || 1.0,
        source: tag.source || 'manual',
        created_at: tag.created_at || new Date().toISOString()
      }))
    }
    
    console.log('💾 保存用户标签:', tagsData)
    await api.put(`/users/${userId}/tags`, tagsData)
    
    originalTags.value = JSON.parse(JSON.stringify(tags.value))
    hasChanges.value = false
    
    ElMessage.success(`成功保存${tags.value.length}个标签`)
  } catch (e: any) {
    console.error('❌ 保存标签失败:', e)
    ElMessage.error(e.response?.data?.message || e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 监听标签变化
watch(tags, () => {
  const currentTagsStr = JSON.stringify(tags.value)
  const originalTagsStr = JSON.stringify(originalTags.value)
  hasChanges.value = currentTagsStr !== originalTagsStr
}, { deep: true })

// 页面挂载
onMounted(() => {
  fetchTags()
  
  // 初始化输入框
  tagCategories.value.forEach(category => {
    newTagInputs[category.key] = ''
  })
})
</script>

<style scoped>
.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.header-section {
  text-align: center;
  margin-bottom: 32px;
  padding: 32px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.page-title {
  font-size: 36px;
  font-weight: bold;
  color: #1769aa;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.title-icon {
  font-size: 40px;
  color: #1890ff;
}

.page-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.loading-container {
  margin-bottom: 24px;
}

.error-alert {
  margin-bottom: 24px;
}

.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.stat-card.total-stat {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card.categories-stat {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-card.weight-stat {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-card.sync-stat {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 32px;
  opacity: 0.3;
}

.action-card {
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.action-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.tags-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  margin-bottom: 24px;
}

.tags-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tags-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.tags-tabs {
  border: none;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-content {
  padding: 20px;
}

.category-description {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
}

.desc-icon {
  color: #1890ff;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin: 24px 0 16px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.preset-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.preset-hint {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

.current-tags-section {
  margin-bottom: 32px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tag-item {
  margin: 0;
  padding: 8px 12px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.tag-item:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.tag-content {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag-name {
  font-weight: bold;
}

.tag-weight {
  font-size: 12px;
  opacity: 0.8;
}

.tag-source {
  font-size: 11px;
  opacity: 0.6;
  padding: 2px 6px;
  background: rgba(255,255,255,0.3);
  border-radius: 10px;
}

.preset-tags-section {
  margin-bottom: 32px;
}

.preset-tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preset-tag-item {
  margin: 0;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px dashed #d9d9d9;
  background: #fafafa;
  position: relative;
}

.preset-tag-item:hover {
  border-color: #1890ff;
  background: #e6f7ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.2);
}

.preset-tag-item:hover::after {
  content: "点击选择";
  position: absolute;
  top: -24px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: #1890ff;
  background: white;
  padding: 2px 6px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  white-space: nowrap;
}

.custom-tag-section {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px dashed #d9d9d9;
}

.custom-tag-input {
  display: flex;
  gap: 12px;
  align-items: center;
}

.tag-input {
  flex: 1;
}

.weight-input {
  width: 120px;
}

.preview-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.preview-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.preview-content {
  padding: 20px;
}

.all-tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.preview-tag {
  margin: 0;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tag-weight-icon {
  color: #faad14;
}

:deep(.el-statistic__head) {
  color: rgba(255,255,255,0.9);
  margin-bottom: 8px;
}

:deep(.el-statistic__content) {
  color: white;
  font-weight: bold;
}

:deep(.el-tabs__header) {
  margin: 0;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.el-empty) {
  padding: 40px 0;
}

:deep(.el-badge__content) {
  border: none;
}
</style> 