# 能源信息服务系统 - 配置说明

## 🚀 快速启动

### 完整启动（推荐）

```bash
# 启动前后端服务并自动初始化v3版本数据
./start_all_with_data.sh
```

**功能特点：**
- ✅ 自动检查依赖环境（Python3、Node.js、MongoDB）
- ✅ 自动创建Python虚拟环境和安装依赖
- ✅ 自动导入v3版本统一数据（45篇文章，包含重烃标签）
- ✅ 自动创建5个Demo用户（每用户1个能源标签）
- ✅ 启动后端服务（http://localhost:8001）
- ✅ 启动前端服务（http://localhost:5173）

### 仅启动后端

```bash
# 仅启动后端服务并初始化数据
./start_backend_with_data.sh
```

### 停止服务

```bash
# 停止后端服务
./stop_backend.sh

# 或手动停止（Ctrl+C）
```

### 数据说明

系统使用v3版本统一数据（`backend/scripts/信息发布文章与标签_规范化.json` + v2版本额外文章）：
- **51篇能源政策文章** - 每篇3-5个标签（优化后）
- **13种能源类型** - 包含新增的重烃标签
- **能源标签覆盖率** - 天然气62.7%，原油47.1%，LNG29.4%，PNG19.6%，电力17.6%，重烃2.0%
- **地域标签覆盖率** - 66.7%，支持全国主要城市的省份和地区自动识别
- **5个Demo用户** - 基于覆盖率优化，每用户专注1个能源类型

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
  { value: '重烃', label: '重烃' },
];
```

### 能源类型分组

**传统化石能源**：
- 原油、汽油、柴油、沥青、石油焦

**天然气类**：
- 管道天然气(PNG)、天然气、液化天然气(LNG)、液化石油气(LPG)、重烃

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

## 🎯 推荐算法权重配置

### 标签权重分级系统

推荐算法基于标签类型分配不同权重，确保地域和能源类型标签获得最高优先级：

| 标签类型 | 权重系数 | 优先级 | 说明 |
|---------|---------|--------|------|
| 地域标签 | **×3.0** | 🟢 最高 | 城市、省份、区域标签 |
| 能源类型 | **×2.5** | 🟡 第二 | 13种标准能源类型 |
| 基础信息 | ×1.0 | ⚪ 标准 | 文档类型等基础标签 |
| 业务领域 | ×0.8 | 🔸 较低 | 业务范围、行业领域 |
| 政策措施 | ×0.8 | 🔸 较低 | 政策工具、措施类型 |
| 重要性 | ×0.6 | 🔹 最低 | 影响力、重要程度 |

### 地域标签权重细分

地域标签内部采用分级权重系统：

| 地域级别 | 权重系数 | 覆盖范围 | 示例 |
|---------|---------|---------|------|
| 直辖市 | 3.0 | 4个 | 北京、上海、天津、重庆 |
| 省会城市 | 2.5 | 31个 | 南京、杭州、广州、成都 |
| 重要城市 | 2.0 | 273个 | 苏州、深圳、青岛、大连 |
| 省份 | 1.8 | 34个 | 江苏、浙江、广东、山东 |
| 经济区域 | 1.5 | 7个 | 长三角、珠三角、环渤海 |
| 方向性地区 | 1.2 | 30个 | 华东、华南、中原、关中 |

### 特殊奖励机制

- **地域匹配奖励**：用户地域与文章地域匹配时额外 +30% 加分
- **能源类型匹配奖励**：用户关注能源类型与文章匹配时额外 +20% 加分
- **组合匹配奖励**：地域+能源类型双重匹配时获得额外奖励加分

### 权重计算公式

```python
# 推荐得分计算
final_score = base_score * (
    region_weight * 3.0 +           # 地域权重
    energy_type_weight * 2.5 +      # 能源类型权重
    other_weights * 1.0              # 其他标签权重
) + bonus_points                     # 奖励加分
```

### 完整地域覆盖数据

系统内置完整的中国行政区划数据库：

- **省份/自治区**：68个（包含完整形式和简称）
- **主要城市**：308个（省会、计划单列市、重要地级市）
- **经济区域**：7个（华北、华东、华南、华中、西南、西北、东北）
- **能源区域**：7个（环渤海、长三角、珠三角、成渝、京津冀等）
- **方向性地区**：30个（中原、关中、江南、岭南等传统地理概念）
- **总关键词**：408个地域关键词，实现全面覆盖

### 数据优化成果

通过标签规范化和权重优化，系统实现了：

- **能源标签覆盖率**：91.1% (41/45篇文章)
- **地域标签覆盖率**：66.7% (30/45篇文章)
- **平均标签数**：从15+个优化至3.6个
- **推荐精度提升**：地域权重+200%，能源类型权重+150%

## 👥 演示用户配置

### 5个预设演示用户（基于能源标签覆盖率优化）

根据当前文章库的能源标签分布，每个用户专注1个能源类型，确保测试更具代表性：

```javascript
const demoUsers = [
  {
    demo_user_id: "user001",
    username: "张工程师",
    email: "zhang@shanghai.com", 
    register_city: "上海",
    description: "天然气市场分析师 - 关注天然气价格与政策",
    energy_types: ["天然气"],  // 覆盖率最高：62.7% (32篇文章)
    expected_articles: 32
  },
  {
    demo_user_id: "user002", 
    username: "李经理",
    email: "li@beijing.com",
    register_city: "北京",
    description: "石油贸易专家 - 原油进口与价格分析",
    energy_types: ["原油"],  // 第二高：47.1% (24篇文章)
    expected_articles: 24
  },
  {
    demo_user_id: "user003",
    username: "王主任",
    email: "wang@shenzhen.com", 
    register_city: "深圳",
    description: "LNG项目经理 - 液化天然气接收站运营",
    energy_types: ["液化天然气(LNG)"],  // 第三高：29.4% (15篇文章)
    expected_articles: 15
  },
  {
    demo_user_id: "user004",
    username: "陈总监", 
    email: "chen@guangzhou.com",
    register_city: "广州",
    description: "管道天然气运营专家 - 天然气管网建设",
    energy_types: ["管道天然气(PNG)"],  // 第四高：19.6% (10篇文章)
    expected_articles: 10
  },
  {
    demo_user_id: "user005",
    username: "刘研究员",
    email: "liu@chengdu.com",
    register_city: "成都", 
    description: "电力系统研究员 - 可再生能源发电",
    energy_types: ["电力"],  // 第五高：17.6% (9篇文章)
    expected_articles: 9
  }
];
```

### 能源标签覆盖率分析

| 能源类型 | 覆盖文章数 | 覆盖率 | 对应用户 |
|---------|-----------|--------|---------|
| 天然气 | 32篇 | 62.7% | 张工程师（上海） |
| 原油 | 24篇 | 47.1% | 李经理（北京） |
| 液化天然气(LNG) | 15篇 | 29.4% | 王主任（深圳） |
| 管道天然气(PNG) | 10篇 | 19.6% | 陈总监（广州） |
| 电力 | 9篇 | 17.6% | 刘研究员（成都） |

### 测试推荐效果验证

**高匹配度场景**：
- 上海用户 + 天然气：应优先推荐上海天然气相关文章
- 北京用户 + 原油：应优先推荐北京/国家层面原油政策文章
- 深圳用户 + LNG：应优先推荐LNG接收站、进口相关文章

**权重验证**：
- 地域匹配：上海用户优先看到上海市相关文章（权重×3.0）
- 能源匹配：天然气用户优先看到天然气文章（权重×2.5）
- 双重匹配：上海+天然气用户获得最高推荐得分

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
cd energy-trading-system/frontend-vue
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
- **能源类型数量**: 13 种能源类型（包含重烃）
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
