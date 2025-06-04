<template>
  <div class="energy-hierarchy-selector">
    <div class="selector-header">
      <h3>⚡ 能源产品分层选择</h3>
      <p class="weight-info">
        🔥 权重体系：<strong>大类产品权重 3.0</strong> | <strong>具体产品权重 5.0</strong>
      </p>
    </div>

    <!-- 权重说明卡片 -->
    <el-card class="weight-explanation" shadow="hover">
      <template #header>
        <span>🎯 权重分层说明</span>
      </template>
      <div class="weight-rules">
        <div class="rule-item">
          <el-tag type="warning" size="large">大类产品 (权重 3.0)</el-tag>
          <span>如：天然气、原油、电力、煤炭等</span>
        </div>
        <div class="rule-item">
          <el-tag type="danger" size="large">具体产品 (权重 5.0)</el-tag>
          <span>如：LNG、汽油、风力发电等</span>
        </div>
        <div class="rule-note">
          💡 选择具体产品时会自动添加对应的大类标签
        </div>
      </div>
    </el-card>

    <!-- 能源层级选择器 -->
    <div class="hierarchy-container">
      <div 
        v-for="(categoryInfo, categoryName) in energyHierarchy" 
        :key="categoryName"
        class="category-section"
      >
        <!-- 大类选择 -->
        <div class="category-header">
          <el-checkbox
            v-model="selectedCategories[categoryName]"
            @change="handleCategoryChange(categoryName, $event)"
            class="category-checkbox"
            size="large"
          >
            <div class="category-info">
              <span class="category-name">📁 {{ categoryName }}</span>
              <el-tag type="warning" size="small">权重 3.0</el-tag>
            </div>
          </el-checkbox>
        </div>

        <!-- 具体产品选择 -->
        <div class="products-container" v-if="categoryInfo.products">
          <el-checkbox-group 
            v-model="selectedProducts[categoryName]"
            @change="handleProductsChange(categoryName, $event)"
            class="products-group"
          >
            <div class="products-grid">
              <el-checkbox
                v-for="(productInfo, productName) in categoryInfo.products"
                :key="productName"
                :label="productName"
                class="product-checkbox"
                size="default"
              >
                <div class="product-info">
                  <span class="product-name">🔧 {{ productName }}</span>
                  <el-tag type="danger" size="small">权重 5.0</el-tag>
                </div>
              </el-checkbox>
            </div>
          </el-checkbox-group>
        </div>
      </div>
    </div>

    <!-- 选择结果统计 -->
    <el-card class="selection-summary" shadow="hover" v-if="totalSelected > 0">
      <template #header>
        <span>📊 选择统计</span>
      </template>
      <div class="summary-stats">
        <div class="stat-item">
          <span class="stat-label">📁 大类产品:</span>
          <span class="stat-value">{{ selectedCategoriesCount }} 个</span>
          <span class="stat-weight">(权重 {{ (selectedCategoriesCount * 3.0).toString() }})</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">🔧 具体产品:</span>
          <span class="stat-value">{{ selectedProductsCount }} 个</span>
          <span class="stat-weight">(权重 {{ (selectedProductsCount * 5.0).toString() }})</span>
        </div>
        <div class="stat-item total">
          <span class="stat-label">📈 总权重:</span>
          <span class="stat-value">{{ totalWeight.toFixed(1) }}</span>
        </div>
      </div>
    </el-card>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button @click="clearAll" icon="Delete">清空选择</el-button>
      <el-button @click="selectRecommended" type="primary" icon="Star">推荐配置</el-button>
      <el-button 
        @click="applySelection" 
        type="success" 
        icon="Check"
        :disabled="totalSelected === 0"
      >
        应用选择 ({{ totalSelected }})
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { tagService } from '@/services/tagService'

// Props
interface Props {
  modelValue?: string[]
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  disabled: false
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string[]]
  'change': [value: string[], weightInfo: any]
}>()

// 响应式数据
const energyHierarchy = ref<any>({})
const selectedCategories = ref<Record<string, boolean>>({})
const selectedProducts = ref<Record<string, string[]>>({})
const loading = ref(false)

// 计算属性
const selectedCategoriesCount = computed(() => {
  return Object.values(selectedCategories.value).filter(Boolean).length
})

const selectedProductsCount = computed(() => {
  return Object.values(selectedProducts.value).reduce((total, products) => {
    return total + (products?.length || 0)
  }, 0)
})

const totalSelected = computed(() => {
  return selectedCategoriesCount.value + selectedProductsCount.value
})

const totalWeight = computed(() => {
  return selectedCategoriesCount.value * 3.0 + selectedProductsCount.value * 5.0
})

const allSelectedEnergies = computed(() => {
  const selected: string[] = []
  
  // 添加选中的大类
  Object.entries(selectedCategories.value).forEach(([category, isSelected]) => {
    if (isSelected) {
      selected.push(category)
    }
  })
  
  // 添加选中的具体产品
  Object.entries(selectedProducts.value).forEach(([category, products]) => {
    if (products && products.length > 0) {
      selected.push(...products)
    }
  })
  
  return selected
})

// 方法
const loadEnergyHierarchy = async () => {
  try {
    loading.value = true
    const response = await tagService.getEnergyHierarchy()
    energyHierarchy.value = response.hierarchy
    
    // 初始化选择状态
    Object.keys(energyHierarchy.value).forEach(category => {
      selectedCategories.value[category] = false
      selectedProducts.value[category] = []
    })
    
    // 根据传入的值设置初始选择
    if (props.modelValue && props.modelValue.length > 0) {
      setInitialSelection(props.modelValue)
    }
    
  } catch (error) {
    console.error('❌ 获取能源层级失败:', error)
    ElMessage.error('获取能源产品层级失败')
  } finally {
    loading.value = false
  }
}

const setInitialSelection = (energies: string[]) => {
  energies.forEach(energy => {
    // 检查是否为大类
    if (energyHierarchy.value[energy]) {
      selectedCategories.value[energy] = true
    } else {
      // 查找具体产品属于哪个大类
      Object.entries(energyHierarchy.value).forEach(([category, info]: [string, any]) => {
        if (info.products && info.products[energy]) {
          if (!selectedProducts.value[category]) {
            selectedProducts.value[category] = []
          }
          if (!selectedProducts.value[category].includes(energy)) {
            selectedProducts.value[category].push(energy)
          }
        }
      })
    }
  })
}

const handleCategoryChange = (categoryName: string, isSelected: boolean) => {
  selectedCategories.value[categoryName] = isSelected
  emitChange()
}

const handleProductsChange = (categoryName: string, products: string[]) => {
  selectedProducts.value[categoryName] = products
  
  // 如果选择了具体产品，自动取消对应大类的选择（避免重复权重）
  if (products.length > 0) {
    selectedCategories.value[categoryName] = false
  }
  
  emitChange()
}

const emitChange = () => {
  const selected = allSelectedEnergies.value
  
  // 计算权重信息
  const weightInfo = {
    categories: selectedCategoriesCount.value,
    products: selectedProductsCount.value,
    totalWeight: totalWeight.value,
    breakdown: {
      categoryWeight: selectedCategoriesCount.value * 3.0,
      productWeight: selectedProductsCount.value * 5.0
    }
  }
  
  emit('update:modelValue', selected)
  emit('change', selected, weightInfo)
}

const clearAll = () => {
  Object.keys(selectedCategories.value).forEach(category => {
    selectedCategories.value[category] = false
    selectedProducts.value[category] = []
  })
  emitChange()
}

const selectRecommended = () => {
  clearAll()
  
  // 推荐配置：选择几个主要的具体产品
  const recommended = {
    '天然气': ['液化天然气(LNG)', '管道天然气(PNG)'],
    '原油': ['汽油', '柴油'],
    '电力': ['风力发电', '太阳能发电']
  }
  
  Object.entries(recommended).forEach(([category, products]) => {
    if (selectedProducts.value[category]) {
      selectedProducts.value[category] = products
    }
  })
  
  emitChange()
  ElMessage.success('已应用推荐配置')
}

const applySelection = () => {
  const selected = allSelectedEnergies.value
  ElMessage.success(`已选择 ${selected.length} 种能源产品`)
}

// 监听外部传入值的变化
watch(() => props.modelValue, (newValue) => {
  if (newValue && newValue.length > 0) {
    clearAll()
    setInitialSelection(newValue)
  }
}, { deep: true })

// 生命周期
onMounted(() => {
  loadEnergyHierarchy()
})
</script>

<style scoped>
.energy-hierarchy-selector {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.selector-header {
  text-align: center;
  margin-bottom: 20px;
}

.selector-header h3 {
  margin: 0 0 8px 0;
  color: #1769aa;
  font-size: 24px;
}

.weight-info {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.weight-explanation {
  margin-bottom: 20px;
}

.weight-rules {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rule-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 8px;
}

.rule-note {
  padding: 8px;
  background: #e3f2fd;
  border-radius: 8px;
  color: #1565c0;
  font-size: 14px;
  text-align: center;
}

.hierarchy-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 20px;
}

.category-section {
  background: white;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.category-header {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.category-checkbox {
  width: 100%;
}

.category-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.category-name {
  font-size: 16px;
  font-weight: 600;
  color: #1769aa;
}

.products-container {
  margin-top: 12px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 8px;
}

.product-checkbox {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.product-checkbox:hover {
  background: #e3f2fd;
  border-color: #1769aa;
}

.product-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 8px;
}

.product-name {
  font-size: 14px;
  color: #333;
}

.selection-summary {
  margin-bottom: 20px;
}

.summary-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 6px;
}

.stat-item.total {
  background: #e3f2fd;
  border: 1px solid #1769aa;
  font-weight: 600;
}

.stat-label {
  min-width: 100px;
  color: #666;
}

.stat-value {
  font-weight: 600;
  color: #1769aa;
}

.stat-weight {
  color: #999;
  font-size: 12px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}

@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .stat-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style> 