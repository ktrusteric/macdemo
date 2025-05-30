<template>
  <el-card class="register-card">
    <h2>用户注册</h2>
    <el-form :model="form" :rules="rules" ref="registerForm" @submit.prevent="onSubmit">
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" autocomplete="off" />
      </el-form-item>
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" autocomplete="off" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" autocomplete="off" />
      </el-form-item>
      <el-form-item label="注册城市" prop="register_city">
        <el-select v-model="form.register_city" placeholder="请选择城市" filterable @change="handleCityChange">
          <el-option v-for="city in cities" :key="city.value" :label="city.label" :value="city.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="关注能源品种" prop="energy_types">
        <el-select v-model="form.energy_types" multiple placeholder="请选择能源类型">
          <el-option v-for="et in energyTypeOptions" :key="et" :label="et" :value="et" />
        </el-select>
      </el-form-item>
      <el-form-item label="自动生成标签">
        <el-tag type="success" v-if="form.register_city">🏙️ 城市: {{ form.register_city }}</el-tag>
        <el-tag type="info" v-if="regionInfo.province">📍 省份: {{ regionInfo.province }}</el-tag>
        <el-tag type="warning" v-if="regionInfo.region">🗺️ 区域: {{ regionInfo.region }}</el-tag>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit" :loading="loading">注册</el-button>
      </el-form-item>
      <el-alert v-if="error" :title="error" type="error" show-icon />
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { register } from '@/api/user'
import { useRouter } from 'vue-router'

const router = useRouter()
const registerForm = ref()
const form = reactive({ email: '', username: '', password: '', register_city: '', energy_types: [] as string[] })
const loading = ref(false)
const error = ref('')
const regionInfo = reactive({ province: '', region: '' })

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
  register_city: [
    { required: true, message: '请选择注册城市', trigger: 'change' }
  ],
  energy_types: [
    { required: true, message: '请至少选择一种能源类型', trigger: 'change' }
  ]
}

const cities = [
  { value: '上海', label: '上海', province: '上海市', region: '华东地区' },
  { value: '北京', label: '北京', province: '北京市', region: '华北地区' },
  { value: '深圳', label: '深圳', province: '广东省', region: '华南地区' },
  { value: '广州', label: '广州', province: '广东省', region: '华南地区' },
  { value: '杭州', label: '杭州', province: '浙江省', region: '华东地区' },
  { value: '成都', label: '成都', province: '四川省', region: '西南地区' },
  { value: '长沙', label: '长沙', province: '湖南省', region: '华中地区' },
  { value: '武汉', label: '武汉', province: '湖北省', region: '华中地区' },
  { value: '南京', label: '南京', province: '江苏省', region: '华东地区' },
  { value: '苏州', label: '苏州', province: '江苏省', region: '华东地区' },
  { value: '天津', label: '天津', province: '天津市', region: '华北地区' },
  { value: '重庆', label: '重庆', province: '重庆市', region: '西南地区' },
]

const energyTypeOptions = [
  '原油', '管道天然气(PNG)', '天然气', '液化天然气(LNG)', '液化石油气(LPG)',
  '汽油', '柴油', '沥青', '石油焦', '生物柴油', '电力', '煤炭'
]

const handleCityChange = (cityValue: string) => {
  const city = cities.find(c => c.value === cityValue)
  if (city) {
    regionInfo.province = city.province
    regionInfo.region = city.region
  } else {
    regionInfo.province = ''
    regionInfo.region = ''
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
    error.value = e.response?.data?.message || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-card { max-width: 480px; margin: 80px auto; }
</style> 