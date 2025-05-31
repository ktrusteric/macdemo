<template>
  <div class="register-page">
    <div class="register-background">
      <div class="background-shape shape-1"></div>
      <div class="background-shape shape-2"></div>
      <div class="background-shape shape-3"></div>
    </div>
    
    <div class="register-container">
      <div class="register-content">
        <!-- 顶部标题区域 -->
        <div class="register-header">
          <div class="platform-logo">
            <el-icon class="platform-icon"><Plus /></el-icon>
          </div>
          <h1 class="platform-title">用户注册</h1>
          <p class="platform-subtitle">创建您的账户，开始个性化的能源资讯体验</p>
        </div>

        <!-- 注册表单卡片 -->
        <el-card class="register-form-card" shadow="always">
          <el-form :model="form" :rules="rules" ref="registerForm" @submit.prevent="onSubmit" label-position="top">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="邮箱地址" prop="email">
                  <el-input 
                    v-model="form.email" 
                    autocomplete="off"
                    placeholder="请输入邮箱地址"
                  >
                    <template #prefix>
                      <el-icon><Message /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="用户名" prop="username">
                  <el-input 
                    v-model="form.username" 
                    autocomplete="off"
                    placeholder="请输入用户名"
                  >
                    <template #prefix>
                      <el-icon><User /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="登录密码" prop="password">
              <el-input 
                v-model="form.password" 
                type="password" 
                autocomplete="off"
                placeholder="请输入登录密码"
                show-password
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-divider content-position="left">
              <span class="divider-text">地区信息</span>
            </el-divider>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="注册省份" prop="register_province">
                  <el-select 
                    v-model="form.register_province" 
                    placeholder="请选择省份" 
                    filterable 
                    @change="handleProvinceChange"
                    style="width: 100%"
                  >
                    <template #prefix>
                      <el-icon><Location /></el-icon>
                    </template>
                    <el-option 
                      v-for="province in provinces" 
                      :key="province.code" 
                      :label="province.name" 
                      :value="province.code"
                    >
                      <div class="province-option">
                        <span class="province-name">{{ province.name }}</span>
                        <el-tag size="small" type="info">{{ province.city_count }}个城市</el-tag>
                      </div>
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="注册城市" prop="register_city">
                  <el-select 
                    v-model="form.register_city" 
                    placeholder="请先选择省份" 
                    filterable 
                    @change="handleCityChange"
                    style="width: 100%"
                    :disabled="!availableCities.length"
                  >
                    <template #prefix>
                      <el-icon><OfficeBuilding /></el-icon>
                    </template>
                    <el-option 
                      v-for="city in availableCities" 
                      :key="city" 
                      :label="city" 
                      :value="city" 
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="关注能源品种" prop="energy_types">
              <el-select 
                v-model="form.energy_types" 
                multiple 
                placeholder="请选择您关注的能源类型" 
                style="width: 100%"
                collapse-tags
                collapse-tags-tooltip
              >
                <template #prefix>
                  <el-icon><Lightning /></el-icon>
                </template>
                <el-option v-for="et in energyTypeOptions" :key="et" :label="et" :value="et">
                  <span class="energy-option">⚡ {{ et }}</span>
                </el-option>
              </el-select>
            </el-form-item>
            
            <el-divider content-position="left">
              <span class="divider-text">自动生成标签预览</span>
            </el-divider>
            
            <div class="auto-tags-preview-section">
              <div class="auto-tags-preview" v-if="form.register_city || form.energy_types.length">
                <div class="tag-group" v-if="regionInfo.region || regionInfo.province || form.register_city">
                  <span class="tag-group-title">地域标签</span>
                  <div class="tag-group-content">
                    <el-tag type="success" v-if="form.register_city" class="preview-tag">
                      🏙️ {{ form.register_city }}
                    </el-tag>
                    <el-tag type="info" v-if="regionInfo.province" class="preview-tag">
                      📍 {{ regionInfo.province }}
                    </el-tag>
                    <el-tag type="warning" v-if="regionInfo.region" class="preview-tag">
                      🗺️ {{ regionInfo.region }}
                    </el-tag>
                  </div>
                </div>
                
                <div class="tag-group" v-if="form.energy_types.length">
                  <span class="tag-group-title">能源标签</span>
                  <div class="tag-group-content">
                    <el-tag 
                      type="primary" 
                      v-for="energy in form.energy_types" 
                      :key="energy"
                      class="preview-tag"
                    >
                      ⚡ {{ energy }}
                    </el-tag>
                  </div>
                </div>
              </div>
              
              <el-empty 
                v-else 
                description="请选择城市和能源类型，系统将自动生成标签"
                :image-size="80"
              />
            </div>
            
            <el-form-item style="margin-top: 32px;">
              <el-button 
                type="primary" 
                @click="onSubmit" 
                :loading="loading"
                size="large"
                class="register-button"
              >
                <el-icon><Check /></el-icon>
                立即注册
              </el-button>
            </el-form-item>
            
            <div class="login-link">
              <span>已有账户？</span>
              <el-link type="primary" @click="router.push('/login')" class="login-nav-link">立即登录</el-link>
            </div>
            
            <el-alert v-if="error" :title="error" type="error" show-icon style="margin-top: 16px;" />
          </el-form>
        </el-card>

        <!-- 页面宽度占位符 - 不可见但确保页面宽度一致 -->
        <div class="width-placeholder" aria-hidden="true"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  User, 
  Message, 
  Lock, 
  Location, 
  OfficeBuilding, 
  Lightning, 
  Check,
  Plus
} from '@element-plus/icons-vue'
import api from '@/api/request'

const router = useRouter()
const registerForm = ref()
const form = reactive({ 
  email: '', 
  username: '', 
  password: '', 
  register_province: '',
  register_city: '', 
  energy_types: [] as string[] 
})
const loading = ref(false)
const error = ref('')
const regionInfo = reactive({ province: '', region: '' })

// 省份和城市数据
const provinces = ref([])
const provincesWithCities = ref({})
const availableCities = computed(() => {
  if (!form.register_province || !provincesWithCities.value[form.register_province]) {
    return []
  }
  return provincesWithCities.value[form.register_province]
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  register_province: [
    { required: true, message: '请选择注册省份', trigger: 'change' }
  ],
  register_city: [
    { required: true, message: '请选择注册城市', trigger: 'change' }
  ],
  energy_types: [
    { required: true, message: '请至少选择一种能源类型', trigger: 'change' }
  ]
}

const energyTypeOptions = [
  '原油', '管道天然气(PNG)', '天然气', '液化天然气(LNG)', '液化石油气(LPG)',
  '汽油', '柴油', '沥青', '石油焦', '生物柴油', '电力', '煤炭', '重烃'
]

// 加载省份城市数据
const loadProvincesWithCities = async () => {
  try {
    const response = await api.get('/users/provinces-with-cities')
    const data = response.data
    
    provinces.value = data.provinces
    
    // 构建省份代码到城市列表的映射
    provincesWithCities.value = {}
    data.provinces.forEach(province => {
      provincesWithCities.value[province.code] = province.cities
    })
    
    console.log('✅ 省份城市数据加载成功', {
      provinces: data.total_provinces,
      cities: data.total_cities
    })
  } catch (error) {
    console.error('❌ 加载省份城市数据失败:', error)
  }
}

const handleProvinceChange = (provinceCode: string) => {
  // 清空城市选择
  form.register_city = ''
  regionInfo.province = ''
  regionInfo.region = ''
  
  console.log('🏛️ 省份选择:', provinceCode, availableCities.value.length, '个城市')
}

const handleCityChange = async (cityValue: string) => {
  if (!cityValue) {
    regionInfo.province = ''
    regionInfo.region = ''
    return
  }
  
  try {
    // 调用后端API获取城市的完整区域信息
    const response = await api.get(`/users/cities-details`)
    const citiesDetails = response.data.cities
    
    const cityDetail = citiesDetails.find(c => c.city === cityValue)
    if (cityDetail) {
      regionInfo.province = cityDetail.province
      regionInfo.region = cityDetail.region
      
      console.log('🏙️ 城市详情:', cityDetail)
    }
  } catch (error) {
    console.error('❌ 获取城市详情失败:', error)
  }
}

const onSubmit = async () => {
  await registerForm.value.validate()
  loading.value = true
  error.value = ''
  try {
    // 调用注册API
    const response = await api.post('/users/register', {
      email: form.email,
      username: form.username,
      password: form.password,
      register_city: form.register_city,
      energy_types: form.energy_types
    })
    
    console.log('✅ 注册成功:', response.data)
    router.push('/login')
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.response?.data?.message || '注册失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadProvincesWithCities()
})
</script>

<style scoped>
.register-page {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  z-index: 9999;
}

.register-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  overflow: hidden;
}

.background-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 20s ease-in-out infinite;
}

.shape-1 {
  width: 350px;
  height: 350px;
  background: white;
  top: 15%;
  left: 5%;
  animation-delay: 0s;
}

.shape-2 {
  width: 250px;
  height: 250px;
  background: white;
  top: 50%;
  right: 10%;
  animation-delay: 7s;
}

.shape-3 {
  width: 180px;
  height: 180px;
  background: white;
  bottom: 15%;
  left: 75%;
  animation-delay: 14s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  33% { transform: translateY(-40px) rotate(120deg); }
  66% { transform: translateY(40px) rotate(240deg); }
}

.register-container {
  position: relative;
  z-index: 10;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.register-content {
  width: 100%;
  max-width: 1280px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

.register-header {
  text-align: center;
  color: white;
  margin-bottom: 16px;
}

.platform-logo {
  margin-bottom: 16px;
}

.platform-icon {
  font-size: 64px;
  color: #FFD700;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
}

.platform-title {
  font-size: 36px;
  font-weight: 700;
  margin: 16px 0 8px 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
  letter-spacing: 1px;
}

.platform-subtitle {
  font-size: 18px;
  opacity: 0.9;
  margin: 0;
  font-weight: 300;
}

.register-form-card {
  width: 100%;
  max-width: 800px;
  border-radius: 20px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.divider-text {
  font-weight: 600;
  color: #606266;
  font-size: 16px;
}

.province-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.province-name {
  flex: 1;
}

.energy-option {
  display: flex;
  align-items: center;
  gap: 6px;
}

.auto-tags-preview-section {
  background: linear-gradient(135deg, #f8f9fa, #ffffff);
  border-radius: 12px;
  padding: 20px;
  border: 2px solid #e4e7ed;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
}

.auto-tags-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.tag-group {
  margin-bottom: 16px;
  width: 100%;
}

.tag-group-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-group-title::before {
  content: '';
  width: 4px;
  height: 16px;
  background: linear-gradient(45deg, #409EFF, #67C23A);
  border-radius: 2px;
}

.tag-group-content {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.preview-tag {
  margin: 0;
  padding: 6px 12px;
  border-radius: 16px;
  font-weight: 500;
}

.register-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(45deg, #409EFF, #67C23A);
  border: none;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

.login-link {
  text-align: center;
  margin-top: 20px;
  font-size: 15px;
}

.login-nav-link {
  font-weight: 500;
  margin-left: 8px;
}

:deep(.el-card__body) {
  padding: 32px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 0 16px;
  height: 44px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 12px;
}

:deep(.el-divider__text) {
  background-color: transparent;
}

:deep(.el-empty) {
  padding: 20px;
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
  .register-container {
    padding: 20px 10px;
  }
  
  .platform-title {
    font-size: 28px;
  }
  
  .platform-subtitle {
    font-size: 16px;
  }
  
  .register-form-card {
    max-width: 100%;
  }
  
  :deep(.el-card__body) {
    padding: 24px;
  }
  
  .tag-group {
    margin-bottom: 12px;
  }
}
</style> 