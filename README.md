# 能源信息服务系统 - 配置说明

## 📋 系统概述

能源信息服务系统是一个基于个性化标签的能源资讯推荐平台，支持多种能源类型的信息聚合与智能推荐。

## 🏷️ 核心标签系统

### 7大类标签分类

```typescript
// 内容标签字段 (Content Model)
interface Content {
  basic_info_tags: string[];      // 基础信息标签
  region_tags: string[];          // 地区标签
  energy_type_tags: string[];     // 能源类型标签
  business_field_tags: string[];  // 业务领域标签
  beneficiary_tags: string[];     // 受益主体标签
  policy_measure_tags: string[];  // 政策措施标签
  importance_tags: string[];      // 重要性标签
}
```

### 用户标签分类

```typescript
enum TagCategory {
  BASIC_INFO = "basic_info",        // 基础信息
  CITY = "city",                    // 城市
  PROVINCE = "province",            // 省份
  REGION = "region",                // 地区
  ENERGY_TYPE = "energy_type",      // 能源类型
  BUSINESS_FIELD = "business_field", // 业务领域
  BENEFICIARY = "beneficiary",      // 受益主体
  POLICY_MEASURE = "policy_measure", // 政策措施
  IMPORTANCE = "importance"         // 重要性
}

enum TagSource {
  PRESET = "preset",               // 预设标签
  MANUAL = "manual",              // 手动添加
  AI_GENERATED = "ai_generated",  // AI生成
  REGION_AUTO = "region_auto"     // 地区自动生成
}
```

## ⚡ 能源类型配置

### 完整能源类型列表 (energyTypes)

```typescript
const energyTypes = [
  { value: '原油', label: '原油' },
  { value: '管道天然气(PNG)', label: '管道天然气(PNG)' },
  { value: '天然气', label: '天然气' },
  { value: '液化天然气(LNG)', label: '液化天然气(LNG)' },
  { value: '液化石油气(LPG)', label: '液化石油气(LPG)' },
  { value: '汽油', label: '汽油' },
  { value: '柴油', label: '柴油' },
  { value: '沥青', label: '沥青' },
  { value: '石油焦', label: '石油焦' },
  { value: '生物柴油', label: '生物柴油' },
  { value: '电力', label: '电力' },
  { value: '煤炭', label: '煤炭' },
];
```

### 能源类型分组

**传统化石能源**：
- 原油、汽油、柴油、沥青、石油焦

**天然气类**：
- 管道天然气(PNG)、天然气、液化天然气(LNG)、液化石油气(LPG)

**新能源/清洁能源**：
- 生物柴油、电力

**固体燃料**：
- 煤炭

## 📄 内容类型映射

### CONTENT_TYPE_MAP

```python
CONTENT_TYPE_MAP = {
    "政策法规": ContentType.POLICY,       # 政策法规类
    "行业资讯": ContentType.NEWS,         # 行业资讯类
    "调价公告": ContentType.PRICE,        # 价格调整公告
    "交易公告": ContentType.ANNOUNCEMENT  # 交易相关公告
}
```

### ContentType 枚举

```python
class ContentType(str, Enum):
    POLICY = "policy"           # 政策法规
    NEWS = "news"              # 行业资讯  
    PRICE = "price"            # 调价公告
    ANNOUNCEMENT = "announcement" # 交易公告
```

## 🗺️ 地区标签系统

### 三层地区标签结构

1. **城市级** (权重: 2.5) - 用户明确选择
2. **省份级** (权重: 2.0) - 系统自动生成
3. **区域级** (权重: 1.5) - 系统自动生成

### 支持的地区

**华东地区**：上海、杭州、南京、苏州等
**华北地区**：北京、天津等
**华南地区**：深圳、广州等
**西南地区**：成都、重庆等
**华中地区**：长沙、武汉等

## 👥 演示用户配置

### 5个预设演示用户

```javascript
const demoUsers = [
  {
    demo_user_id: "user001",
    username: "张先生",
    email: "zhang@newenergy.com", 
    register_city: "上海",
    description: "新能源投资者 - 关注太阳能、风能项目",
    energy_types: ["电力", "生物柴油", "天然气"]
  },
  {
    demo_user_id: "user002", 
    username: "李女士",
    email: "li@traditional.com",
    register_city: "北京",
    description: "传统能源企业主 - 石油、天然气行业专家",
    energy_types: ["原油", "天然气", "液化天然气(LNG)", "煤炭"]
  },
  {
    demo_user_id: "user003",
    username: "王先生",
    email: "wang@carbon.com", 
    register_city: "深圳",
    description: "节能减排顾问 - 专注碳中和、环保政策",
    energy_types: ["电力", "生物柴油", "天然气"]
  },
  {
    demo_user_id: "user004",
    username: "陈女士", 
    email: "chen@power.com",
    register_city: "广州",
    description: "电力系统工程师 - 电网、储能技术专家", 
    energy_types: ["电力", "煤炭", "天然气"]
  },
  {
    demo_user_id: "user005",
    username: "刘先生",
    email: "liu@policy.com",
    register_city: "成都", 
    description: "能源政策研究员 - 政策法规、市场分析",
    energy_types: ["原油", "天然气", "电力", "煤炭"]
  }
];
```

## 🔧 技术配置

### 数据库配置

```python
# MongoDB 配置
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "energy_info"

# 集合名称
- users: 用户基础信息
- user_tags: 用户标签数据
- content: 内容文章数据
```

### API 端点

```bash
# 用户相关
GET  /api/v1/users/demo-users                    # 获取演示用户列表
GET  /api/v1/users/demo-users/{demo_user_id}/tags # 获取演示用户标签
GET  /api/v1/users/{user_id}/tags                # 获取用户标签
PUT  /api/v1/users/{user_id}/tags                # 更新用户标签
POST /api/v1/users/register                      # 用户注册
POST /api/v1/users/login                         # 用户登录

# 内容相关  
GET  /api/v1/users/{user_id}/recommendations     # 获取个性化推荐
POST /api/v1/users/behavior                      # 记录用户行为
GET  /api/v1/users/{user_id}/insights           # 获取用户行为洞察
```

### 前端配置

```typescript
// Vite 代理配置
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8001',
      changeOrigin: true,
      secure: false,
    }
  }
}

// Redux Store 结构
interface RootState {
  auth: AuthState;      // 认证状态
  user: UserState;      // 用户状态
  // ... 其他状态
}
```

## 🚀 部署说明

### 启动顺序

1. **启动数据库** (MongoDB)
```bash
mongod --dbpath /data/db
```

2. **导入初始数据**
```bash
cd energy-trading-system/backend
python3 scripts/import_sample_data.py
```

3. **启动后端服务**
```bash
cd energy-trading-system/backend  
python3 main.py
# 服务地址: http://localhost:8001
```

4. **启动前端应用**
```bash
cd energy-trading-system/frontend
npm run dev
# 应用地址: http://localhost:5173
```

## 🎯 AI助手集成

### 内置AI助手

1. **客服助手**
   - ID: `9714d9bc-31ca-40b5-a720-4329f5fc4af7`
   - Token: `e0dc8833077b48669a04ad4a70a7ebe2`

2. **资讯助手**  
   - ID: `158ab70e-2996-4cce-9822-6f8195a7cfa5`
   - Token: `9bc6008decb94efeaee65dd076aab5e8`

3. **交易助手**
   - ID: `1e72acc1-43a8-4cda-8d54-f409c9c5d5ed` 
   - Token: `18703d14357040c88f32ae5e4122c2d6`

### AI服务配置

```python
AI_BACKEND_URL = "https://ai.wiseocean.cn"
AI_API_TIMEOUT = 30
```

## 📊 数据统计

- **支持城市数量**: 12+ 个主要城市
- **能源类型数量**: 12 种能源类型
- **标签分类数量**: 7 大类标签系统
- **演示用户数量**: 5 个典型用户画像
- **内容类型数量**: 4 种内容分类

## 🔍 注意事项

1. **能源类型一致性**: 前后端必须使用相同的能源类型列表
2. **标签权重设置**: 城市(2.5) > 省份(2.0) > 地区(1.5) > 能源类型(1.0)
3. **API版本控制**: 所有API使用 `/api/v1/` 前缀
4. **数据迁移**: 更新能源类型时需要同步更新现有用户数据
5. **缓存策略**: 推荐内容建议设置适当的缓存时间

---

📝 **最后更新**: 2025-05-28  
🔧 **维护**: 定期更新能源类型和标签分类  
🎯 **目标**: 提供精准的个性化能源资讯服务
