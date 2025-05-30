<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <div class="header-content">
            <h2 class="register-title">
              <el-icon class="title-icon"><UserPlus /></el-icon>
              用户注册
            </h2>
            <p class="register-subtitle">创建您的账户，开始个性化的能源资讯体验</p>
          </div>
        </div>
      </template>
      
      <el-form :model="form" :rules="rules" ref="registerForm" @submit.prevent="onSubmit" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="邮箱地址" prop="email">
              <el-input 
                v-model="form.email" 
                autocomplete="off"
                prefix-icon="Message"
                placeholder="请输入邮箱地址"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input 
                v-model="form.username" 
                autocomplete="off"
                prefix-icon="User"
                placeholder="请输入用户名"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="登录密码" prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            autocomplete="off"
            prefix-icon="Lock"
            placeholder="请输入登录密码"
            show-password
          />
        </el-form-item>
        
        <el-divider content-position="left">
          <span class="divider-text">地区信息</span>
        </el-divider>
        
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="注册省份" prop="register_province">
              <el-select 
                v-model="form.register_province" 
                placeholder="请选择省份" 
                filterable 
                @change="handleProvinceChange"
                style="width: 100%"
                prefix-icon="Location"
              >
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
                prefix-icon="OfficeBuilding"
              >
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
            prefix-icon="Lightning"
            collapse-tags
            collapse-tags-tooltip
          >
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
            style="width: 100%"
            icon="Check"
          >
            立即注册
          </el-button>
        </el-form-item>
        
        <div class="login-link">
          <span>已有账户？</span>
          <el-link type="primary" @click="router.push('/login')">立即登录</el-link>
        </div>
        
        <el-alert v-if="error" :title="error" type="error" show-icon style="margin-top: 16px;" />
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { register } from '@/api/user'
import { useRouter } from 'vue-router'
import { UserPlus } from '@element-plus/icons-vue'
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
  '汽油', '柴油', '沥青', '石油焦', '生物柴油', '电力', '煤炭'
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
    await register(form.email, form.username, form.password, form.register_city, form.energy_types)
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
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card { 
  max-width: 600px; 
  width: 100%;
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  border-radius: 16px;
}

.card-header {
  text-align: center;
  padding: 0;
}

.header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.register-title {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  color: #409eff;
  font-size: 28px;
}

.register-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.divider-text {
  font-weight: bold;
  color: #606266;
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
  gap: 4px;
}

.auto-tags-preview-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e4e7ed;
}

.auto-tags-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.auto-tags-preview .el-tag {
  margin: 0;
}

.tag-group {
  margin-bottom: 16px;
}

.tag-group-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
}

.tag-group-content {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preview-tag {
  margin: 0;
}

.login-link {
  text-align: center;
  margin-top: 16px;
}

:deep(.el-select) {
  width: 100%;
}
</style> 