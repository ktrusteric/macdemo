<template>
  <div class="admin-users-container">
    <!-- 页面头部 -->
    <div class="header-section">
      <h1 class="page-title">
        <el-icon class="title-icon"><User /></el-icon>
        用户标签管理
      </h1>
      <p class="page-subtitle">管理用户标签，优化推荐效果</p>
    </div>

    <!-- 用户选择区域 -->
    <el-card class="user-selector-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>选择用户</span>
          <el-button 
            type="primary" 
            @click="loadUsers" 
            :loading="loadingUsers"
            icon="Refresh"
            size="small"
          >
            刷新用户列表
          </el-button>
        </div>
      </template>
      
      <div class="user-list">
        <el-row :gutter="20">
          <el-col 
            :span="6" 
            v-for="user in users" 
            :key="user.id"
            class="user-card-col"
          >
            <el-card 
              :class="['user-card', { 'selected': selectedUser?.id === user.id }]"
              @click="selectUser(user)"
              shadow="hover"
            >
              <div class="user-info">
                <div class="user-avatar">
                  <el-avatar :size="50">{{ user.username.charAt(0) }}</el-avatar>
                </div>
                <div class="user-details">
                  <h4 class="user-name">{{ user.username }}</h4>
                  <p class="user-email">{{ user.email }}</p>
                  <p class="user-city">{{ user.register_city }}</p>
                </div>
              </div>
              <div class="user-stats">
                <el-tag size="small">{{ getUserTagCount(user.id) }}个标签</el-tag>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 用户标签管理区域 -->
    <el-card v-if="selectedUser" class="tags-management-card">
      <template #header>
        <div class="card-header">
          <span>{{ selectedUser.username }} 的标签管理</span>
          <div class="header-actions">
            <el-button 
              type="info" 
              @click="loadUserTags" 
              :loading="loadingTags"
              icon="Refresh"
              size="small"
            >
              刷新标签
            </el-button>
            <el-button 
              type="success" 
              @click="saveUserTags" 
              :loading="savingTags"
              icon="Check"
              :disabled="!hasChanges"
            >
              保存更改
            </el-button>
            <el-button 
              type="warning"
              @click="resetUserTags"
              icon="RefreshLeft"
            >
              重置标签
            </el-button>
          </div>
        </div>
      </template>

      <!-- 标签统计 -->
      <div class="tags-stats">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="标签总数" :value="userTags.length" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="地域标签" :value="getTagsByCategory('region').length" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="能源标签" :value="getTagsByCategory('energy_type').length" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="总权重" :value="totalWeight" :precision="1" />
          </el-col>
        </el-row>
      </div>

      <!-- 标签预览 -->
      <div class="tags-preview" v-if="userTags.length">
        <h4>当前标签预览</h4>
        <div class="tags-cloud">
          <el-tag
            v-for="tag in sortedTags"
            :key="`preview-${tag.category}-${tag.name}`"
            :type="getTagTypeByCategory(tag.category)"
            :size="getTagSizeByWeight(tag.weight)"
            :effect="tag.source === 'preset' ? 'dark' : 'plain'"
            class="preview-tag"
          >
            {{ tag.name }}
          </el-tag>
        </div>
      </div>

      <!-- 标签分类管理 -->
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
                <div
                  v-for="tag in getTagsByCategory(category.key)"
                  :key="`${tag.category}-${tag.name}`"
                  class="tag-item-wrapper"
                >
                  <!-- 标签显示 -->
                  <el-tag
                    v-if="!tag.isEditing"
                    :type="getTagTypeByCategory(category.key)"
                    :effect="tag.source === 'preset' ? 'dark' : 'plain'"
                    closable
                    @close="removeTag(tag)"
                    @click="startEditWeight(tag)"
                    class="tag-item editable-tag"
                  >
                    <div class="tag-content">
                      <span class="tag-name">{{ tag.name }}</span>
                      <span class="tag-weight">{{ tag.weight }}x</span>
                    </div>
                    <el-icon class="edit-hint-icon"><Edit /></el-icon>
                  </el-tag>
                  
                  <!-- 权重编辑器 -->
                  <div v-else class="tag-weight-editor">
                    <div class="editor-content">
                      <span class="editing-tag-name">{{ tag.name }}</span>
                      <el-input-number
                        v-model="tag.editingWeight"
                        :min="0.1"
                        :max="5.0"
                        :step="0.1"
                        :precision="1"
                        size="small"
                        class="weight-editor-input"
                        @keyup.enter="confirmEditWeight(tag)"
                        @keyup.esc="cancelEditWeight(tag)"
                      />
                      <div class="weight-editor-actions">
                        <el-button 
                          type="success" 
                          size="small" 
                          @click="confirmEditWeight(tag)"
                          icon="Check"
                        />
                        <el-button 
                          type="info" 
                          size="small" 
                          @click="cancelEditWeight(tag)"
                          icon="Close"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-tags">
                <el-empty description="暂无此类标签" :image-size="80" />
              </div>
            </div>

            <!-- 添加标签区域 -->
            <div class="add-tags-section" v-if="category.key !== 'region'">
              <h4 class="section-title">添加{{ category.name }}标签</h4>
              <div class="preset-tags-container">
                <el-tag
                  v-for="tag in getAvailablePresetTags(category.key)"
                  :key="tag"
                  :type="getTagTypeByCategory(category.key)"
                  effect="plain"
                  @click="addPresetTag(category.key, tag)"
                  class="preset-tag clickable-tag"
                >
                  <el-icon class="add-icon"><Plus /></el-icon>
                  {{ tag }}
                </el-tag>
              </div>
              
              <!-- 自定义标签输入 -->
              <div class="custom-tag-input">
                <el-input
                  v-model="customTagInputs[category.key]"
                  placeholder="输入自定义标签名称"
                  @keyup.enter="addCustomTag(category.key)"
                  size="small"
                  style="width: 200px; margin-right: 10px;"
                />
                <el-button 
                  type="primary" 
                  @click="addCustomTag(category.key)"
                  icon="Plus"
                  size="small"
                  :disabled="!customTagInputs[category.key]?.trim()"
                >
                  添加
                </el-button>
              </div>
            </div>

            <!-- 地域标签特殊处理 -->
            <div v-if="category.key === 'region'" class="region-selector-section">
              <h4 class="section-title">添加地域标签</h4>
              <div class="region-selector">
                <el-select
                  v-model="regionSelector.selectedProvince"
                  placeholder="选择省份"
                  @change="handleProvinceChange"
                  style="width: 200px; margin-right: 10px;"
                >
                  <el-option
                    v-for="province in regionProvinces"
                    :key="province.code"
                    :label="province.name"
                    :value="province.code"
                  />
                </el-select>
                
                <el-select
                  v-model="regionSelector.selectedCity"
                  placeholder="选择城市"
                  :disabled="!regionSelector.selectedProvince"
                  style="width: 200px; margin-right: 10px;"
                >
                  <el-option
                    v-for="city in regionSelector.availableCities"
                    :key="city.code"
                    :label="city.name"
                    :value="city.name"
                  />
                </el-select>
                
                <el-button 
                  type="primary" 
                  @click="addRegionTag"
                  icon="Plus"
                  :disabled="!regionSelector.selectedCity"
                >
                  添加地域标签
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 空状态 -->
    <el-card v-else class="empty-state-card">
      <el-empty description="请先选择一个用户来管理其标签" :image-size="120" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, 
  Plus, 
  Edit, 
  Check, 
  Close, 
  Refresh, 
  RefreshLeft, 
  InfoFilled 
} from '@element-plus/icons-vue'
import { useAdminStore } from '@/store/admin'
import { tagService } from '@/services/tagService'

// 使用管理员Store
const adminStore = useAdminStore()

// 接口定义
interface AdminUser {
  id: string
  username: string
  email: string
  register_city: string
  created_at?: string
  tags_count?: number
}

interface UserTag {
  category: string
  name: string
  weight: number
  source: string
  created_at?: string
  isEditing?: boolean
  editingWeight?: number
}

interface TagCategory {
  key: string
  name: string
  description: string
  color: string
  presetTags: string[]
}

// 响应式数据
const users = ref<AdminUser[]>([])
const selectedUser = ref<AdminUser | null>(null)
const userTags = ref<UserTag[]>([])
const tagCategories = ref<TagCategory[]>([])
const activeTab = ref('region')

// 加载状态
const loadingUsers = ref(false)
const loadingTags = ref(false)
const savingTags = ref(false)
const hasChanges = ref(false)

// 自定义标签输入
const customTagInputs = reactive<Record<string, string>>({})

// 地域选择器
const regionProvinces = ref([])
const regionSelector = reactive({
  selectedProvince: '',
  selectedCity: '',
  availableCities: []
})

// 计算属性
const totalWeight = computed(() => {
  return userTags.value.reduce((sum, tag) => sum + (tag.weight || 1.0), 0)
})

const sortedTags = computed(() => {
  return [...userTags.value].sort((a, b) => {
    if (a.category !== b.category) {
      return a.category.localeCompare(b.category)
    }
    return (b.weight || 1.0) - (a.weight || 1.0)
  })
})

// 获取分类标签
const getTagsByCategory = (category: string) => {
  return userTags.value.filter(tag => tag.category === category)
}

// 获取用户标签数量
const getUserTagCount = (userId: string) => {
  const user = users.value.find(u => u.id === userId)
  return user?.tags_count || 0
}

// 获取可用的预设标签
const getAvailablePresetTags = (category: string) => {
  const categoryConfig = tagCategories.value.find(cat => cat.key === category)
  if (!categoryConfig) return []
  
  const currentTags = getTagsByCategory(category).map(tag => tag.name)
  return categoryConfig.presetTags.filter(tag => !currentTags.includes(tag))
}

// 样式相关方法
const getTagTypeByCategory = (category: string) => {
  const typeMap: Record<string, string> = {
    'region': 'success',
    'energy_type': 'warning', 
    'business_field': 'info',
    'beneficiary': 'danger',
    'policy_measure': 'success',
    'importance': 'warning'
  }
  return typeMap[category] || 'primary'
}

const getTagSizeByWeight = (weight: number) => {
  if (weight >= 3.0) return 'large'
  if (weight >= 2.0) return 'default'
  return 'small'
}

const getBadgeType = (category: string) => {
  const typeMap: Record<string, string> = {
    'region': 'success',
    'energy_type': 'warning',
    'business_field': 'info', 
    'beneficiary': 'danger',
    'policy_measure': 'success',
    'importance': 'warning'
  }
  return typeMap[category] || 'primary'
}

// 标签编辑方法
const startEditWeight = (tag: UserTag) => {
  tag.isEditing = true
  tag.editingWeight = tag.weight
}

const confirmEditWeight = (tag: UserTag) => {
  if (tag.editingWeight && tag.editingWeight >= 0.1 && tag.editingWeight <= 5.0) {
    tag.weight = tag.editingWeight
    tag.isEditing = false
    hasChanges.value = true
    ElMessage.success(`已更新标签权重：${tag.name} -> ${tag.weight}x`)
  } else {
    ElMessage.error('权重必须在0.1-5.0之间')
  }
}

const cancelEditWeight = (tag: UserTag) => {
  tag.isEditing = false
  tag.editingWeight = tag.weight
}

const removeTag = (tag: UserTag) => {
  const index = userTags.value.findIndex(t => 
    t.category === tag.category && t.name === tag.name
  )
  if (index !== -1) {
    userTags.value.splice(index, 1)
    hasChanges.value = true
    ElMessage.success(`已删除标签：${tag.name}`)
  }
}

const addPresetTag = (category: string, tagName: string) => {
  const existingTag = userTags.value.find(tag => 
    tag.category === category && tag.name === tagName
  )
  
  if (existingTag) {
    ElMessage.warning('该标签已存在')
    return
  }
  
  userTags.value.push({
    category,
    name: tagName,
    weight: 1.0,
    source: 'preset',
    created_at: new Date().toISOString()
  })
  
  hasChanges.value = true
  ElMessage.success(`已添加标签：${tagName}`)
}

const addCustomTag = (category: string) => {
  const tagName = customTagInputs[category]?.trim()
  if (!tagName) return
  
  const existingTag = userTags.value.find(tag => 
    tag.category === category && tag.name === tagName
  )
  
  if (existingTag) {
    ElMessage.warning('该标签已存在')
    return
  }
  
  userTags.value.push({
    category,
    name: tagName,
    weight: 1.0,
    source: 'manual',
    created_at: new Date().toISOString()
  })
  
  customTagInputs[category] = ''
  hasChanges.value = true
  ElMessage.success(`已添加自定义标签：${tagName}`)
}

// 地域标签方法
const handleProvinceChange = (provinceCode: string) => {
  regionSelector.selectedCity = ''
  const province = regionProvinces.value.find((p: any) => p.code === provinceCode)
  regionSelector.availableCities = province?.cities || []
}

const addRegionTag = () => {
  const cityName = regionSelector.selectedCity
  if (!cityName) return
  
  const existingTag = userTags.value.find(tag => 
    tag.category === 'region' && tag.name === cityName
  )
  
  if (existingTag) {
    ElMessage.warning('该地域标签已存在')
    return
  }
  
  // 添加城市标签
  userTags.value.push({
    category: 'region',
    name: cityName,
    weight: 2.5,
    source: 'preset',
    created_at: new Date().toISOString()
  })
  
  // 自动添加省份标签
  const province = regionProvinces.value.find((p: any) => p.code === regionSelector.selectedProvince)
  if (province) {
    const provinceName = province.name
    const existingProvinceTag = userTags.value.find(tag => 
      tag.category === 'region' && tag.name === provinceName
    )
    
    if (!existingProvinceTag) {
      userTags.value.push({
        category: 'region',
        name: provinceName,
        weight: 2.0,
        source: 'region_auto',
        created_at: new Date().toISOString()
      })
    }
  }
  
  hasChanges.value = true
  ElMessage.success(`已添加地域标签：${cityName}`)
  
  // 清空选择
  regionSelector.selectedProvince = ''
  regionSelector.selectedCity = ''
  regionSelector.availableCities = []
}

// API方法
const loadUsers = async () => {
  loadingUsers.value = true
  try {
    const response = await adminStore.getUsers()
    users.value = response.data || []
    ElMessage.success(`加载了 ${users.value.length} 个用户`)
  } catch (error: any) {
    console.error('❌ 加载用户失败:', error)
    ElMessage.error('加载用户失败：' + error.message)
  } finally {
    loadingUsers.value = false
  }
}

const selectUser = async (user: AdminUser) => {
  selectedUser.value = user
  await loadUserTags()
}

const loadUserTags = async () => {
  if (!selectedUser.value) return
  
  loadingTags.value = true
  try {
    const response = await adminStore.getUserTags(selectedUser.value.id)
    
    if (response?.data?.tags) {
      userTags.value = response.data.tags.map((tag: any) => ({
        ...tag,
        isEditing: false,
        editingWeight: tag.weight
      }))
      hasChanges.value = false
      ElMessage.success(`加载了 ${userTags.value.length} 个标签`)
    } else {
      userTags.value = []
      ElMessage.info('该用户暂无标签')
    }
  } catch (error: any) {
    console.error('❌ 加载用户标签失败:', error)
    ElMessage.error('加载用户标签失败：' + error.message)
  } finally {
    loadingTags.value = false
  }
}

const saveUserTags = async () => {
  if (!selectedUser.value || !hasChanges.value) {
    ElMessage.info('没有更改需要保存')
    return
  }
  
  savingTags.value = true
  try {
    const tagsData = {
      tags: userTags.value.map(tag => ({
        category: tag.category,
        name: tag.name,
        weight: tag.weight || 1.0,
        source: tag.source || 'manual',
        created_at: tag.created_at || new Date().toISOString()
      }))
    }
    
    await adminStore.updateUserTags(selectedUser.value.id, tagsData)
    hasChanges.value = false
    ElMessage.success(`成功保存 ${userTags.value.length} 个标签`)
  } catch (error: any) {
    console.error('❌ 保存用户标签失败:', error)
    ElMessage.error('保存失败：' + error.message)
  } finally {
    savingTags.value = false
  }
}

const resetUserTags = async () => {
  if (!selectedUser.value) return
  
  const result = await ElMessageBox.confirm(
    `确定要重置用户 ${selectedUser.value.username} 的标签吗？将保留地域和能源类型标签，清理其他标签。`,
    '重置确认',
    {
      confirmButtonText: '重置',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).catch(() => false)
  
  if (!result) return
  
  const preservedCategories = ['region', 'energy_type']
  const originalCount = userTags.value.length
  
  userTags.value = userTags.value.filter(tag => preservedCategories.includes(tag.category))
  
  const removedCount = originalCount - userTags.value.length
  
  if (removedCount > 0) {
    hasChanges.value = true
    ElMessage.success(`已重置标签，保留${userTags.value.length}个基础标签，清理了${removedCount}个其他标签`)
  } else {
    ElMessage.info('当前只有基础标签，无需重置')
  }
}

// 初始化方法
const initTagCategories = async () => {
  try {
    const categories = await tagService.getTagCategories()
    // 过滤掉基础信息标签分类
    tagCategories.value = categories.filter(cat => cat.key !== 'basic_info')
    console.log('✅ 标签分类配置加载成功:', tagCategories.value.length)
  } catch (error) {
    console.error('❌ 加载标签分类配置失败:', error)
    ElMessage.error('加载标签配置失败，请刷新重试')
  }
}

const loadProvincesWithCities = async () => {
  try {
    const data = await tagService.getProvincesWithCities()
    regionProvinces.value = data.provinces
    console.log('✅ 省份城市数据加载成功')
  } catch (error) {
    console.error('❌ 加载省份城市数据失败:', error)
    ElMessage.error('加载省份城市数据失败')
  }
}

// 监听变化
watch(userTags, () => {
  // 这里可以添加更复杂的变化检测逻辑
}, { deep: true })

// 页面挂载
onMounted(async () => {
  try {
    await initTagCategories()
    await loadProvincesWithCities()
    await loadUsers()
  } catch (error) {
    console.error('❌ 页面初始化失败:', error)
    ElMessage.error('页面初始化失败，请刷新重试')
  }
})
</script>

<style scoped>
.admin-users-container {
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header-section {
  text-align: center;
  margin-bottom: 24px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: #1769aa;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.title-icon {
  font-size: 32px;
  color: #1890ff;
}

.page-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.user-selector-card {
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.user-list {
  padding: 20px;
}

.user-card-col {
  margin-bottom: 16px;
}

.user-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.user-card.selected {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.user-details h4 {
  margin: 0 0 4px 0;
  color: #303133;
}

.user-details p {
  margin: 2px 0;
  font-size: 12px;
  color: #909399;
}

.user-stats {
  text-align: center;
}

.tags-management-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.tags-stats {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
}

.tags-preview {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
}

.tags-preview h4 {
  margin-bottom: 16px;
  color: #303133;
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preview-tag {
  margin: 0;
  transition: all 0.3s;
}

.tags-tabs {
  border: none;
  min-height: 500px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-content {
  padding: 20px;
  min-height: 400px;
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
  margin-bottom: 16px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;
}

.tag-item-wrapper {
  position: relative;
}

.editable-tag {
  cursor: pointer;
  position: relative;
  padding-right: 32px;
}

.tag-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-weight {
  font-size: 12px;
  opacity: 0.8;
}

.edit-hint-icon {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  opacity: 0.6;
}

.tag-weight-editor {
  display: inline-block;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 8px;
}

.editor-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.editing-tag-name {
  font-size: 12px;
  color: #606266;
}

.weight-editor-input {
  width: 80px;
}

.weight-editor-actions {
  display: flex;
  gap: 4px;
}

.empty-tags {
  text-align: center;
  padding: 40px;
}

.add-tags-section {
  margin-top: 24px;
}

.preset-tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.preset-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.preset-tag:hover {
  transform: scale(1.05);
}

.clickable-tag {
  display: flex;
  align-items: center;
  gap: 4px;
}

.add-icon {
  font-size: 12px;
}

.custom-tag-input {
  display: flex;
  align-items: center;
  margin-top: 16px;
}

.region-selector-section {
  margin-top: 24px;
}

.region-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.empty-state-card {
  text-align: center;
  padding: 60px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

:deep(.el-statistic__head) {
  color: #606266;
  margin-bottom: 4px;
}

:deep(.el-statistic__content) {
  color: #303133;
  font-weight: bold;
}

:deep(.el-card__header) {
  background: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-tabs__header) {
  margin: 0;
}

:deep(.el-tabs__nav-wrap) {
  background: #fafafa;
}
</style> 