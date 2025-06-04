# 上海石油天然气交易中心信息门户系统 - 配置说明

## 🚀 快速启动

### 完整启动（推荐）

```bash
# 启动前后端服务并自动初始化规范化数据
./start_all_with_data.sh
```

**功能特点：**
- ✅ 自动检查依赖环境（Python3、Node.js、MongoDB）
- ✅ 自动创建Python虚拟环境和安装依赖
- ✅ 自动导入规范化测试数据（45篇文章，优化标签）
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

## 📋 系统概述

上海石油天然气交易中心信息门户系统是一个基于个性化标签的能源资讯推荐平台，支持多种能源类型的信息聚合与智能推荐。

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


## 🗺️ 地区标签系统

### 三层地区标签结构

1. **城市级** (权重: 2.5) - 用户明确选择
2. **省份级** (权重: 2.0) - 系统自动生成
3. **区域级** (权重: 1.5) - 系统自动生成

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
