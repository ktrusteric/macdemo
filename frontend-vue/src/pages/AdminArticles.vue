<template>
  <div class="dashboard-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1>📝 文章管理</h1>
        <p>管理系统中的所有文章内容</p>
      </div>
      <div class="header-right">
        <button @click="showCreateModal = true" class="create-btn">
          ➕ 新建文章
        </button>
      </div>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="filter-bar">
      <div class="search-section">
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索文章标题或内容..."
            @input="handleSearch"
          />
          <span class="search-icon">🔍</span>
        </div>
      </div>
      
      <div class="filter-section">
        <div class="filter-group">
          <label>文章类型:</label>
          <select v-model="selectedType" @change="handleFilter" class="filter-select">
            <option value="">全部类型</option>
            <option value="policy">政策法规</option>
            <option value="news">行业资讯</option>
            <option value="price">调价公告</option>
            <option value="announcement">交易公告</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>能源类型:</label>
          <select v-model="selectedEnergyType" @change="handleFilter" class="filter-select">
            <option value="">全部能源</option>
            <option value="天然气">天然气</option>
            <option value="原油">原油</option>
            <option value="液化天然气(LNG)">液化天然气(LNG)</option>
            <option value="管道天然气(PNG)">管道天然气(PNG)</option>
            <option value="电力">电力</option>
            <option value="煤炭">煤炭</option>
            <option value="汽油">汽油</option>
            <option value="柴油">柴油</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>标签搜索:</label>
          <select v-model="tagSearch" @change="handleFilter" class="filter-select">
            <option value="">全部标签</option>
            <optgroup label="地区标签" v-if="tagOptions.region_tags">
              <optgroup label="主要城市">
                <option 
                  v-for="city in tagOptions.region_tags.cities.slice(0, 50)" 
                  :key="city" 
                  :value="city"
                >
                  {{ city }}
                </option>
              </optgroup>
              <optgroup label="省份">
                <option 
                  v-for="province in tagOptions.region_tags.provinces" 
                  :key="province" 
                  :value="province"
                >
                  {{ province }}
                </option>
              </optgroup>
              <optgroup label="地区">
                <option 
                  v-for="region in tagOptions.region_tags.regions" 
                  :key="region" 
                  :value="region"
                >
                  {{ region }}
                </option>
              </optgroup>
            </optgroup>
            <optgroup label="能源类型" v-if="tagOptions.energy_type_tags">
              <option 
                v-for="energy in tagOptions.energy_type_tags" 
                :key="energy" 
                :value="energy"
              >
                {{ energy }}
              </option>
            </optgroup>
            <optgroup label="基础信息" v-if="tagOptions.basic_info_tags">
              <option 
                v-for="basic in tagOptions.basic_info_tags" 
                :key="basic" 
                :value="basic"
              >
                {{ basic }}
              </option>
            </optgroup>
            <optgroup label="业务领域" v-if="tagOptions.business_field_tags">
              <option 
                v-for="business in tagOptions.business_field_tags" 
                :key="business" 
                :value="business"
              >
                {{ business }}
              </option>
            </optgroup>
            <optgroup label="政策措施" v-if="tagOptions.policy_measure_tags">
              <option 
                v-for="policy in tagOptions.policy_measure_tags" 
                :key="policy" 
                :value="policy"
              >
                {{ policy }}
              </option>
            </optgroup>
            <optgroup label="重要性" v-if="tagOptions.importance_tags">
              <option 
                v-for="importance in tagOptions.importance_tags" 
                :key="importance" 
                :value="importance"
              >
                {{ importance }}
              </option>
            </optgroup>
          </select>
        </div>
        
        <div class="filter-actions">
          <button @click="resetFilters" class="reset-btn">🔄 重置</button>
          <button @click="loadArticles" class="search-btn">🔍 搜索</button>
        </div>
      </div>
    </div>

    <!-- 文章列表 -->
    <div class="articles-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner">🔄</div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="articles.length === 0" class="empty-state">
        <div class="empty-icon">📄</div>
        <h3>暂无文章</h3>
        <p>点击"新建文章"开始添加内容</p>
      </div>
      
      <div v-else class="articles-grid">
        <div 
          v-for="article in articles" 
          :key="article._id"
          class="article-card"
        >
          <div class="article-header">
            <div class="article-type">
              <span class="type-badge" :class="article.type">
                {{ contentTypeMap[article.type] || article.type }}
              </span>
            </div>
            <div class="article-actions">
              <button @click="editArticle(article)" class="edit-btn">✏️</button>
              <button @click="deleteArticle(article)" class="delete-btn">🗑️</button>
            </div>
          </div>
          
          <div class="article-content">
            <h3 class="article-title">{{ article.title }}</h3>
            <p class="article-summary">{{ truncateText(article.content, 100) }}</p>
            
            <div class="article-meta">
              <span class="meta-item">📅 {{ formatDate(article.publish_date) }}</span>
              <span class="meta-item">👁️ {{ article.view_count || 0 }} 次浏览</span>
            </div>
            
            <!-- 标签显示 -->
            <div class="article-tags" v-if="hasAnyTags(article)">
              <div v-if="article.basic_info_tags?.length" class="tag-group">
                <span class="tag-label">基础:</span>
                <span 
                  v-for="tag in article.basic_info_tags.slice(0, 2)" 
                  :key="tag"
                  class="tag basic-tag"
                >
                  {{ tag }}
                </span>
                <span v-if="article.basic_info_tags.length > 2" class="tag-more">
                  +{{ article.basic_info_tags.length - 2 }}
                </span>
              </div>
              
              <div v-if="article.energy_type_tags?.length" class="tag-group">
                <span class="tag-label">能源:</span>
                <span 
                  v-for="tag in article.energy_type_tags.slice(0, 2)" 
                  :key="tag"
                  class="tag energy-tag"
                >
                  {{ tag }}
                </span>
                <span v-if="article.energy_type_tags.length > 2" class="tag-more">
                  +{{ article.energy_type_tags.length - 2 }}
                </span>
              </div>
              
              <div v-if="article.region_tags?.length" class="tag-group">
                <span class="tag-label">地区:</span>
                <span 
                  v-for="tag in article.region_tags.slice(0, 2)" 
                  :key="tag"
                  class="tag region-tag"
                >
                  {{ tag }}
                </span>
                <span v-if="article.region_tags.length > 2" class="tag-more">
                  +{{ article.region_tags.length - 2 }}
                </span>
              </div>
              
              <div v-if="article.business_field_tags?.length" class="tag-group">
                <span class="tag-label">业务:</span>
                <span 
                  v-for="tag in article.business_field_tags.slice(0, 1)" 
                  :key="tag"
                  class="tag business-tag"
                >
                  {{ tag }}
                </span>
                <span v-if="article.business_field_tags.length > 1" class="tag-more">
                  +{{ article.business_field_tags.length - 1 }}
                </span>
              </div>
              
              <div v-if="article.importance_tags?.length" class="tag-group">
                <span class="tag-label">重要性:</span>
                <span 
                  v-for="tag in article.importance_tags.slice(0, 1)" 
                  :key="tag"
                  class="tag importance-tag"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页控件 -->
    <div class="pagination" v-if="totalPages > 1">
      <button 
        @click="changePage(currentPage - 1)" 
        :disabled="currentPage <= 1"
        class="page-btn"
      >
        ⬅️ 上一页
      </button>
      
      <span class="page-info">
        第 {{ currentPage }} 页，共 {{ totalPages }} 页
      </span>
      
      <button 
        @click="changePage(currentPage + 1)" 
        :disabled="currentPage >= totalPages"
        class="page-btn"
      >
        下一页 ➡️
      </button>
    </div>

    <!-- 创建/编辑文章模态框 -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal-content large-modal">
        <div class="modal-header">
          <h3>{{ showEditModal ? '✏️ 编辑文章' : '➕ 新建文章' }}</h3>
          <button @click="closeModals" class="close-btn">✕</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveArticle" class="article-form">
            <div class="form-row">
              <div class="form-group">
                <label>文章标题 *</label>
                <input 
                  v-model="articleForm.title" 
                  type="text" 
                  placeholder="请输入文章标题"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>文章类型 * <span class="type-hint">(选择后自动生成基础信息标签)</span></label>
                <select v-model="articleForm.type" required @change="onDocumentTypeChange">
                  <option value="">请选择类型</option>
                  <option value="policy">政策法规</option>
                  <option value="news">行业资讯</option>
                  <option value="price">调价公告</option>
                  <option value="announcement">交易公告</option>
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label>文章内容 *</label>
              <div class="content-input-group">
                <textarea 
                  v-model="articleForm.content" 
                  placeholder="请输入文章内容"
                  rows="8"
                  required
                ></textarea>
                <div class="ai-tag-actions">
                  <button 
                    type="button" 
                    @click="generateTagsWithAI" 
                    :disabled="!articleForm.content.trim() || generatingTags"
                    class="ai-tag-btn"
                  >
                    <span v-if="generatingTags">🤖 AI标签生成中...</span>
                    <span v-else>🤖 AI标签化</span>
                  </button>
                  <small class="ai-hint">输入文章内容后，点击此按钮自动生成标签</small>
                </div>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>发布日期</label>
                <input 
                  v-model="articleForm.publish_date" 
                  type="date"
                />
              </div>
              
              <div class="form-group">
                <label>来源</label>
                <input 
                  v-model="articleForm.source" 
                  type="text" 
                  placeholder="文章来源"
                />
              </div>
            </div>
            
            <div class="form-group">
              <label>文章链接 <span class="optional-hint">(可选)</span></label>
              <input 
                v-model="articleForm.link" 
                type="url" 
                placeholder="https://example.com/article"
              />
              <small class="link-hint">添加原文链接，用户可点击标题跳转</small>
            </div>
            
            <!-- 标签编辑区域 -->
            <div class="tags-section">
              <h4>🏷️ 文章标签</h4>
              
              <!-- 基础信息标签 -->
              <div class="tag-category">
                <label>基础信息标签</label>
                <div class="tag-input-row">
                  <div class="tag-input-group">
                    <input 
                      v-model="newBasicTag" 
                      type="text" 
                      placeholder="添加基础信息标签"
                      @keyup.enter="addBasicTag"
                    />
                    <button type="button" @click="addBasicTag" class="add-tag-btn">➕</button>
                  </div>
                  <div class="preset-tags">
                    <span 
                      v-for="tag in presetTags.basic_info" 
                      :key="tag"
                      @click="addPresetTag('basic_info_tags', tag)"
                      class="preset-tag"
                    >
                      {{ tag }}
                    </span>
                  </div>
                </div>
                <div class="tags-display">
                  <span 
                    v-for="(tag, index) in articleForm.basic_info_tags" 
                    :key="index"
                    class="tag basic-tag"
                  >
                    {{ tag }}
                    <button type="button" @click="removeBasicTag(index)" class="remove-tag">✕</button>
                  </span>
                </div>
              </div>
              
              <!-- 能源类型标签 -->
              <div class="tag-category">
                <label>能源类型标签</label>
                <div class="tag-input-row">
                  <div class="tag-input-group">
                    <input 
                      v-model="newEnergyTag" 
                      type="text" 
                      placeholder="添加能源类型标签"
                      @keyup.enter="addEnergyTag"
                    />
                    <button type="button" @click="addEnergyTag" class="add-tag-btn">➕</button>
                  </div>
                  <div class="preset-tags">
                    <span 
                      v-for="tag in presetTags.energy_types" 
                      :key="tag"
                      @click="addPresetTag('energy_type_tags', tag)"
                      class="preset-tag energy-preset"
                    >
                      {{ tag }}
                    </span>
                  </div>
                </div>
                <div class="tags-display">
                  <span 
                    v-for="(tag, index) in articleForm.energy_type_tags" 
                    :key="index"
                    class="tag energy-tag"
                  >
                    {{ tag }}
                    <button type="button" @click="removeEnergyTag(index)" class="remove-tag">✕</button>
                  </span>
                </div>
              </div>
              
              <!-- 地区标签 -->
              <div class="tag-category">
                <label>地区标签</label>
                <div class="tag-input-row">
                  <div class="tag-input-group">
                    <input 
                      v-model="newRegionTag" 
                      type="text" 
                      placeholder="添加地区标签"
                      @keyup.enter="addRegionTag"
                    />
                    <button type="button" @click="addRegionTag" class="add-tag-btn">➕</button>
                  </div>
                  <div class="preset-tags">
                    <span 
                      v-for="tag in presetTags.regions" 
                      :key="tag"
                      @click="addPresetTag('region_tags', tag)"
                      class="preset-tag region-preset"
                    >
                      {{ tag }}
                    </span>
                  </div>
                </div>
                <div class="tags-display">
                  <span 
                    v-for="(tag, index) in articleForm.region_tags" 
                    :key="index"
                    class="tag region-tag"
                  >
                    {{ tag }}
                    <button type="button" @click="removeRegionTag(index)" class="remove-tag">✕</button>
                  </span>
                </div>
              </div>
              
              <!-- 业务领域标签 -->
              <div class="tag-category">
                <label>业务领域标签</label>
                <div class="tag-input-row">
                  <div class="tag-input-group">
                    <input 
                      v-model="newBusinessTag" 
                      type="text" 
                      placeholder="添加业务领域标签"
                      @keyup.enter="addBusinessTag"
                    />
                    <button type="button" @click="addBusinessTag" class="add-tag-btn">➕</button>
                  </div>
                  <div class="preset-tags">
                    <span 
                      v-for="tag in presetTags.business_fields" 
                      :key="tag"
                      @click="addPresetTag('business_field_tags', tag)"
                      class="preset-tag business-preset"
                    >
                      {{ tag }}
                    </span>
                  </div>
                </div>
                <div class="tags-display">
                  <span 
                    v-for="(tag, index) in articleForm.business_field_tags" 
                    :key="index"
                    class="tag business-tag"
                  >
                    {{ tag }}
                    <button type="button" @click="removeBusinessTag(index)" class="remove-tag">✕</button>
                  </span>
                </div>
              </div>
              
              <!-- 受益主体标签 -->
              <div class="tag-category">
                <label>受益主体标签</label>
                <div class="tag-input-row">
                  <div class="tag-input-group">
                    <input 
                      v-model="newBeneficiaryTag" 
                      type="text" 
                      placeholder="添加受益主体标签"
                      @keyup.enter="addBeneficiaryTag"
                    />
                    <button type="button" @click="addBeneficiaryTag" class="add-tag-btn">➕</button>
                  </div>
                  <div class="preset-tags">
                    <span 
                      v-for="tag in presetTags.beneficiaries" 
                      :key="tag"
                      @click="addPresetTag('beneficiary_tags', tag)"
                      class="preset-tag beneficiary-preset"
                    >
                      {{ tag }}
                    </span>
                  </div>
                </div>
                <div class="tags-display">
                  <span 
                    v-for="(tag, index) in articleForm.beneficiary_tags" 
                    :key="index"
                    class="tag beneficiary-tag"
                  >
                    {{ tag }}
                    <button type="button" @click="removeBeneficiaryTag(index)" class="remove-tag">✕</button>
                  </span>
                </div>
              </div>
              
              <!-- 政策措施标签 -->
              <div class="tag-category">
                <label>政策措施标签</label>
                <div class="tag-input-row">
                  <div class="tag-input-group">
                    <input 
                      v-model="newPolicyTag" 
                      type="text" 
                      placeholder="添加政策措施标签"
                      @keyup.enter="addPolicyTag"
                    />
                    <button type="button" @click="addPolicyTag" class="add-tag-btn">➕</button>
                  </div>
                  <div class="preset-tags">
                    <span 
                      v-for="tag in presetTags.policy_measures" 
                      :key="tag"
                      @click="addPresetTag('policy_measure_tags', tag)"
                      class="preset-tag policy-preset"
                    >
                      {{ tag }}
                    </span>
                  </div>
                </div>
                <div class="tags-display">
                  <span 
                    v-for="(tag, index) in articleForm.policy_measure_tags" 
                    :key="index"
                    class="tag policy-tag"
                  >
                    {{ tag }}
                    <button type="button" @click="removePolicyTag(index)" class="remove-tag">✕</button>
                  </span>
                </div>
              </div>
              
              <!-- 重要性标签 -->
              <div class="tag-category">
                <label>重要性标签</label>
                <div class="tag-input-row">
                  <div class="tag-input-group">
                    <input 
                      v-model="newImportanceTag" 
                      type="text" 
                      placeholder="添加重要性标签"
                      @keyup.enter="addImportanceTag"
                    />
                    <button type="button" @click="addImportanceTag" class="add-tag-btn">➕</button>
                  </div>
                  <div class="preset-tags">
                    <span 
                      v-for="tag in presetTags.importance" 
                      :key="tag"
                      @click="addPresetTag('importance_tags', tag)"
                      class="preset-tag importance-preset"
                    >
                      {{ tag }}
                    </span>
                  </div>
                </div>
                <div class="tags-display">
                  <span 
                    v-for="(tag, index) in articleForm.importance_tags" 
                    :key="index"
                    class="tag importance-tag"
                  >
                    {{ tag }}
                    <button type="button" @click="removeImportanceTag(index)" class="remove-tag">✕</button>
                  </span>
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeModals" class="cancel-btn">
                取消
              </button>
              <button type="submit" :disabled="saving" class="save-btn">
                <span v-if="saving">💾 保存中...</span>
                <span v-else>💾 保存</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 页面宽度占位符 - 不可见但确保页面宽度一致 -->
    <div class="width-placeholder" aria-hidden="true"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useAdminStore } from '@/store/admin'
import api from '@/api/request'
import tagService from '@/services/tagService'

const adminStore = useAdminStore()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const generatingTags = ref(false)
const articles = ref<any[]>([])
const searchQuery = ref('')
const selectedType = ref('')
const selectedEnergyType = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 12
const tagOptions = ref<any>({})

// 内容类型映射 - 从统一服务获取，不再硬编码
const contentTypeMap = ref<Record<string, string>>({})

// 模态框状态
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingArticle = ref<any>(null)

// 标签输入
const newEnergyTag = ref('')
const newRegionTag = ref('')
const newBasicTag = ref('')
const newBusinessTag = ref('')
const newBeneficiaryTag = ref('')
const newPolicyTag = ref('')
const newImportanceTag = ref('')
const tagSearch = ref('')

// 预设标签数据 - 从统一的标签服务获取，不再硬编码
const presetTags = ref({
  energy_types: [] as string[],
  regions: [] as string[],
  basic_info: [] as string[],
  business_fields: [] as string[],
  beneficiaries: [] as string[],
  policy_measures: [] as string[],
  importance: [] as string[]
})

// 文章表单
const articleForm = reactive({
  title: '',
  content: '',
  type: '',
  publish_date: '',
  source: '',
  link: '',
  basic_info_tags: [] as string[],
  region_tags: [] as string[],
  energy_type_tags: [] as string[],
  business_field_tags: [] as string[],
  beneficiary_tags: [] as string[],
  policy_measure_tags: [] as string[],
  importance_tags: [] as string[]
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

// 截断文本
const truncateText = (text: string, maxLength: number) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '未知日期'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 检查是否有标签
const hasAnyTags = (article: any) => {
  return (article.basic_info_tags?.length > 0) || 
         (article.energy_type_tags?.length > 0) || 
         (article.region_tags?.length > 0) ||
         (article.business_field_tags?.length > 0) ||
         (article.beneficiary_tags?.length > 0) ||
         (article.policy_measure_tags?.length > 0) ||
         (article.importance_tags?.length > 0)
}

// 加载文章列表
const loadArticles = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize,
      search: searchQuery.value || undefined,
      type: selectedType.value || undefined,
      energy_type: selectedEnergyType.value || undefined,
      tag_search: tagSearch.value || undefined
    }
    
    const response = await adminStore.getArticles(params)
    articles.value = response.articles
    totalPages.value = response.total_pages
    
  } catch (error: any) {
    console.error('加载文章失败:', error)
    alert('加载文章失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  loadArticles()
}

// 筛选处理
const handleFilter = () => {
  currentPage.value = 1
  loadArticles()
}

// 重置筛选
const resetFilters = () => {
  searchQuery.value = ''
  selectedType.value = ''
  selectedEnergyType.value = ''
  tagSearch.value = ''
  currentPage.value = 1
  loadArticles()
}

// 分页处理
const changePage = (page: number) => {
  currentPage.value = page
  loadArticles()
}

// 重置表单
const resetForm = () => {
  articleForm.title = ''
  articleForm.content = ''
  articleForm.type = ''
  articleForm.publish_date = ''
  articleForm.source = ''
  articleForm.link = ''
  articleForm.basic_info_tags = []
  articleForm.region_tags = []
  articleForm.energy_type_tags = []
  articleForm.business_field_tags = []
  articleForm.beneficiary_tags = []
  articleForm.policy_measure_tags = []
  articleForm.importance_tags = []
  newEnergyTag.value = ''
  newRegionTag.value = ''
  newBasicTag.value = ''
  newBusinessTag.value = ''
  newBeneficiaryTag.value = ''
  newPolicyTag.value = ''
  newImportanceTag.value = ''
}

// 关闭模态框
const closeModals = () => {
  showCreateModal.value = false
  showEditModal.value = false
  editingArticle.value = null
  resetForm()
}

// 编辑文章
const editArticle = (article: any) => {
  editingArticle.value = article
  articleForm.title = article.title
  articleForm.content = article.content
  articleForm.type = article.type
  if (article.publish_date) {
    articleForm.publish_date = article.publish_date
  } else if (article.publish_time) {
    articleForm.publish_date = article.publish_time.split('T')[0]
  } else {
    articleForm.publish_date = ''
  }
  articleForm.source = article.source || ''
  articleForm.link = article.link || ''
  articleForm.basic_info_tags = [...(article.basic_info_tags || [])]
  articleForm.region_tags = [...(article.region_tags || [])]
  articleForm.energy_type_tags = [...(article.energy_type_tags || [])]
  articleForm.business_field_tags = [...(article.business_field_tags || [])]
  articleForm.beneficiary_tags = [...(article.beneficiary_tags || [])]
  articleForm.policy_measure_tags = [...(article.policy_measure_tags || [])]
  articleForm.importance_tags = [...(article.importance_tags || [])]
  showEditModal.value = true
}

// 删除文章
const deleteArticle = async (article: any) => {
  if (!confirm(`确定要删除文章"${article.title}"吗？此操作不可恢复。`)) {
    return
  }
  
  try {
    await adminStore.deleteArticle(article.id)
    alert('✅ 文章删除成功')
    loadArticles()
  } catch (error: any) {
    console.error('删除文章失败:', error)
    alert('❌ 删除文章失败: ' + error.message)
  }
}

// 保存文章
const saveArticle = async () => {
  try {
    saving.value = true
    
    const articleData = {
      title: articleForm.title,
      content: articleForm.content,
      type: articleForm.type,
      publish_time: articleForm.publish_date ? new Date(articleForm.publish_date).toISOString() : new Date().toISOString(),
      source: articleForm.source || '官方发布',
      link: articleForm.link || '',
      basic_info_tags: articleForm.basic_info_tags,
      region_tags: articleForm.region_tags,
      energy_type_tags: articleForm.energy_type_tags,
      business_field_tags: articleForm.business_field_tags,
      beneficiary_tags: articleForm.beneficiary_tags,
      policy_measure_tags: articleForm.policy_measure_tags,
      importance_tags: articleForm.importance_tags
    }
    
    if (showEditModal.value && editingArticle.value) {
      // 更新文章
      await adminStore.updateArticle(editingArticle.value.id, articleData)
      alert('✅ 文章更新成功')
    } else {
      // 创建文章
      await adminStore.createArticle(articleData)
      alert('✅ 文章创建成功')
    }
    
    closeModals()
    loadArticles()
    
  } catch (error: any) {
    console.error('保存文章失败:', error)
    alert('❌ 保存文章失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

// AI标签生成
const generateTagsWithAI = async () => {
  try {
    if (!articleForm.content.trim()) {
      alert('请先输入文章内容')
      return
    }
    
    generatingTags.value = true
    
    const response = await api.post('/admin/articles/generate-tags', {
      content: articleForm.content
    })
    
    if (response.data?.success && response.data?.data) {
      const tags = response.data.data
      
      // 合并AI生成的标签到现有标签（去重）
      const mergeUniqueTags = (existing: string[], generated: string[]) => {
        const combined = [...existing, ...generated]
        return [...new Set(combined)]
      }
      
      articleForm.region_tags = mergeUniqueTags(articleForm.region_tags, tags.region_tags || [])
      articleForm.energy_type_tags = mergeUniqueTags(articleForm.energy_type_tags, tags.energy_type_tags || [])
      articleForm.business_field_tags = mergeUniqueTags(articleForm.business_field_tags, tags.business_field_tags || [])
      articleForm.beneficiary_tags = mergeUniqueTags(articleForm.beneficiary_tags, tags.beneficiary_tags || [])
      articleForm.policy_measure_tags = mergeUniqueTags(articleForm.policy_measure_tags, tags.policy_measure_tags || [])
      articleForm.importance_tags = mergeUniqueTags(articleForm.importance_tags, tags.importance_tags || [])
      
      alert('🎉 AI标签生成成功！已自动添加到相应标签类别中')
    } else {
      alert('❌ AI标签生成失败，请稍后重试')
    }
    
  } catch (error: any) {
    console.error('AI标签生成失败:', error)
    alert('❌ AI标签生成失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    generatingTags.value = false
  }
}

// 添加能源标签
const addEnergyTag = () => {
  const tag = newEnergyTag.value.trim()
  if (tag && !articleForm.energy_type_tags.includes(tag)) {
    articleForm.energy_type_tags.push(tag)
    newEnergyTag.value = ''
  }
}

// 移除能源标签
const removeEnergyTag = (index: number) => {
  articleForm.energy_type_tags.splice(index, 1)
}

// 添加地区标签
const addRegionTag = () => {
  const tag = newRegionTag.value.trim()
  if (tag && !articleForm.region_tags.includes(tag)) {
    articleForm.region_tags.push(tag)
    newRegionTag.value = ''
  }
}

// 移除地区标签
const removeRegionTag = (index: number) => {
  articleForm.region_tags.splice(index, 1)
}

// 添加基础信息标签
const addBasicTag = () => {
  const tag = newBasicTag.value.trim()
  if (tag && !articleForm.basic_info_tags.includes(tag)) {
    articleForm.basic_info_tags.push(tag)
    newBasicTag.value = ''
  }
}

// 移除基础信息标签
const removeBasicTag = (index: number) => {
  articleForm.basic_info_tags.splice(index, 1)
}

// 添加业务领域标签
const addBusinessTag = () => {
  const tag = newBusinessTag.value.trim()
  if (tag && !articleForm.business_field_tags.includes(tag)) {
    articleForm.business_field_tags.push(tag)
    newBusinessTag.value = ''
  }
}

// 移除业务领域标签
const removeBusinessTag = (index: number) => {
  articleForm.business_field_tags.splice(index, 1)
}

// 添加受益主体标签
const addBeneficiaryTag = () => {
  const tag = newBeneficiaryTag.value.trim()
  if (tag && !articleForm.beneficiary_tags.includes(tag)) {
    articleForm.beneficiary_tags.push(tag)
    newBeneficiaryTag.value = ''
  }
}

// 移除受益主体标签
const removeBeneficiaryTag = (index: number) => {
  articleForm.beneficiary_tags.splice(index, 1)
}

// 添加政策措施标签
const addPolicyTag = () => {
  const tag = newPolicyTag.value.trim()
  if (tag && !articleForm.policy_measure_tags.includes(tag)) {
    articleForm.policy_measure_tags.push(tag)
    newPolicyTag.value = ''
  }
}

// 移除政策措施标签
const removePolicyTag = (index: number) => {
  articleForm.policy_measure_tags.splice(index, 1)
}

// 添加重要性标签
const addImportanceTag = () => {
  const tag = newImportanceTag.value.trim()
  if (tag && !articleForm.importance_tags.includes(tag)) {
    articleForm.importance_tags.push(tag)
    newImportanceTag.value = ''
  }
}

// 移除重要性标签
const removeImportanceTag = (index: number) => {
  articleForm.importance_tags.splice(index, 1)
}

// 🔥 处理文档类型变更，自动生成basic_info_tags
const onDocumentTypeChange = () => {
  // 文档类型到基础信息标签的映射
  const typeToBasicTag = {
    'policy': '政策法规',
    'news': '行业资讯', 
    'price': '调价公告',
    'announcement': '交易公告'
  }
  
  // 清空现有的基础信息标签
  articleForm.basic_info_tags = []
  
  // 根据选择的类型自动添加对应的基础信息标签
  if (articleForm.type && typeToBasicTag[articleForm.type]) {
    articleForm.basic_info_tags.push(typeToBasicTag[articleForm.type])
    console.log('🏷️ 自动生成基础信息标签:', typeToBasicTag[articleForm.type])
  }
}

// 添加预制标签
const addPresetTag = (tagType: string, tag: string) => {
  if (!articleForm[tagType].includes(tag)) {
    articleForm[tagType].push(tag)
  }
}

// 统一的标签配置加载方法
const loadTagOptions = async () => {
  try {
    console.log('🏷️ 开始加载标签配置...')
    
    // 使用统一的标签服务获取预设标签
    const adminPresetTags = await tagService.getAdminPresetTags()
    presetTags.value = adminPresetTags
    
    // 获取完整的标签选项（用于筛选下拉框）
    const fullTagOptions = await tagService.getTagOptions()
    tagOptions.value = fullTagOptions
    
    // 获取内容类型映射
    contentTypeMap.value = await tagService.getContentTypeMap()
    
    console.log('✅ 标签配置加载成功:', {
      energy_types: presetTags.value.energy_types.length,
      regions: presetTags.value.regions.length,
      basic_info: presetTags.value.basic_info.length,
      business_fields: presetTags.value.business_fields.length,
      beneficiaries: presetTags.value.beneficiaries.length,
      policy_measures: presetTags.value.policy_measures.length,
      importance: presetTags.value.importance.length,
      content_types: Object.keys(contentTypeMap.value).length
    })
    
  } catch (error) {
    console.error('❌ 加载标签配置失败:', error)
    alert('❌ 无法加载标签配置，请检查：\n1. 后端服务是否正常运行\n2. 网络连接是否正常\n\n页面可能无法正常工作，请联系管理员')
    
    // 设置空的标签配置，避免页面崩溃
    presetTags.value = {
      energy_types: [],
      regions: [],
      basic_info: [],
      business_fields: [],
      beneficiaries: [],
      policy_measures: [],
      importance: []
    }
    
    contentTypeMap.value = {}
  }
}

// 在页面加载时初始化
onMounted(async () => {
  try {
    // 1. 先加载标签配置
    await loadTagOptions()
    
    // 2. 再加载文章列表
    await loadArticles()
  } catch (error) {
    console.error('❌ 页面初始化失败:', error)
    alert('页面初始化失败，请刷新重试')
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

.page-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.create-btn {
  background: #48bb78;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.create-btn:hover {
  background: #38a169;
}

.filter-bar {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-section {
  margin-bottom: 20px;
}

.search-box {
  position: relative;
  max-width: 500px;
}

.search-box input {
  width: 100%;
  padding: 12px 40px 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.search-box input:focus {
  outline: none;
  border-color: #4299e1;
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #a0aec0;
}

.filter-section {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
}

.filter-select {
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  min-width: 150px;
  transition: border-color 0.2s;
}

.filter-select:focus {
  outline: none;
  border-color: #4299e1;
}

.filter-input {
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  min-width: 200px;
  transition: border-color 0.2s;
}

.filter-input:focus {
  outline: none;
  border-color: #4299e1;
}

.filter-actions {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.reset-btn, .search-btn {
  background: #718096;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.reset-btn:hover {
  background: #4a5568;
}

.search-btn {
  background: #4299e1;
}

.search-btn:hover {
  background: #3182ce;
}

.articles-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-height: 400px;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  font-size: 48px;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  color: #4a5568;
}

.empty-state p {
  margin: 0;
  color: #718096;
}

.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.article-card {
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s;
  background: #f7fafc;
}

.article-card:hover {
  border-color: #4299e1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.15);
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.type-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.type-badge.policy { background: #9f7aea; }
.type-badge.news { background: #4299e1; }
.type-badge.price { background: #f56565; }
.type-badge.announcement { background: #48bb78; }

.article-actions {
  display: flex;
  gap: 8px;
}

.edit-btn, .delete-btn {
  background: none;
  border: none;
  padding: 6px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s;
}

.edit-btn:hover {
  background: #e2e8f0;
}

.delete-btn:hover {
  background: #fed7d7;
}

.article-title {
  margin: 0 0 12px 0;
  color: #2d3748;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
}

.article-summary {
  margin: 0 0 12px 0;
  color: #4a5568;
  font-size: 14px;
  line-height: 1.5;
}

.article-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.meta-item {
  font-size: 12px;
  color: #718096;
}

.article-tags {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tag-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-label {
  font-size: 12px;
  color: #718096;
  font-weight: 500;
  min-width: 40px;
}

.tag {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  color: white;
}

.energy-tag { background: #ed8936; }
.region-tag { background: #38b2ac; }

.tag-more {
  font-size: 11px;
  color: #718096;
  font-style: italic;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-btn {
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #3182ce;
}

.page-btn:disabled {
  background: #a0aec0;
  cursor: not-allowed;
}

.page-info {
  color: #4a5568;
  font-size: 14px;
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
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.large-modal {
  max-width: 900px;
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

.article-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #2d3748;
  font-size: 14px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4299e1;
}

.tags-section {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  background: #f7fafc;
}

.tags-section h4 {
  margin: 0 0 16px 0;
  color: #2d3748;
}

.tag-category {
  margin-bottom: 20px;
}

.tag-category:last-child {
  margin-bottom: 0;
}

.tag-category label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #4a5568;
  font-size: 14px;
}

.tag-input-row {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.tag-input-group {
  display: flex;
  gap: 8px;
}

.tag-input-group input {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
}

.preset-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-height: 120px;
  overflow-y: auto;
  padding: 8px;
  background: #f7fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.preset-tag {
  background: #e2e8f0;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.preset-tag:hover {
  background: #cbd5e0;
  transform: translateY(-1px);
}

.energy-preset { background: #fed7aa; }
.energy-preset:hover { background: #fdba74; }

.region-preset { background: #bfdbfe; }
.region-preset:hover { background: #93c5fd; }

.business-preset { background: #d1fae5; }
.business-preset:hover { background: #a7f3d0; }

.beneficiary-preset { background: #fce7f3; }
.beneficiary-preset:hover { background: #fbcfe8; }

.policy-preset { background: #e0e7ff; }
.policy-preset:hover { background: #c7d2fe; }

.importance-preset { background: #fef3c7; }
.importance-preset:hover { background: #fde68a; }

.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 32px;
  padding: 8px;
  border: 1px dashed #e2e8f0;
  border-radius: 6px;
  background: #fafafa;
}

.tags-display .tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 16px;
  color: white;
  font-weight: 500;
}

.basic-tag { background: #6b7280; }
.energy-tag { background: #f59e0b; }
.region-tag { background: #3b82f6; }
.business-tag { background: #10b981; }
.beneficiary-tag { background: #ec4899; }
.policy-tag { background: #8b5cf6; }
.importance-tag { background: #f59e0b; }

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.cancel-btn {
  background: #718096;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.cancel-btn:hover {
  background: #4a5568;
}

.save-btn {
  background: #48bb78;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.save-btn:hover:not(:disabled) {
  background: #38a169;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .filter-bar {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .articles-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
}

.add-tag-btn {
  background: #48bb78;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.add-tag-btn:hover {
  background: #38a169;
}

.remove-tag {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 10px;
  opacity: 0.8;
  margin-left: 4px;
  padding: 2px;
  border-radius: 50%;
  transition: opacity 0.2s;
}

.remove-tag:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.2);
}

/* 新增功能样式 */
.content-input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.content-input-group textarea {
  width: 100%;
  min-height: 200px;
  resize: vertical;
}

.ai-tag-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-start;
}

.ai-tag-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.ai-tag-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.ai-tag-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.ai-tag-btn:active {
  transform: translateY(0);
}

.ai-hint {
  color: #718096;
  font-size: 12px;
  font-style: italic;
}

.link-hint {
  display: block;
  margin-top: 4px;
  color: #718096;
  font-size: 12px;
  font-style: italic;
}

.optional-hint {
  color: #a0aec0;
  font-size: 12px;
  font-weight: normal;
}

.type-hint {
  color: #a0aec0;
  font-size: 12px;
  font-weight: normal;
}
</style> 