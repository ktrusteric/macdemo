# 🔐 管理员功能完整使用指南

## 📋 功能概述

能源信息服务系统已成功实现完整的管理员登录和文章管理功能，包括：

### ✅ 已实现功能
- 🔐 **管理员登录认证** - JWT Token + 权限验证
- 📝 **文章CRUD操作** - 创建、读取、更新、删除文章
- 🏷️ **智能标签管理** - 自动解析和分类标签
- 📊 **批量数据导入** - JSON格式文章批量导入
- 📈 **统计数据查看** - 文章和用户统计信息
- 🔍 **文章搜索筛选** - 按类型、关键词搜索

## 🚀 快速启动

### 1. 启动系统服务

```bash
# 启动后端和前端服务（推荐）
./start_all_with_data.sh

# 或分别启动
./start_backend_with_data.sh  # 后端服务
cd frontend-vue && npm run dev  # 前端服务
```

### 2. 创建管理员账户

```bash
# 创建默认管理员用户
cd backend
python3 scripts/create_admin_user.py
```

**默认管理员账户：**
- 用户名：`admin`
- 密码：`admin123456`
- 邮箱：`admin@energy-system.com`

### 3. 访问管理后台

- **前端管理页面**：http://localhost:5173/admin/login
- **后端API文档**：http://localhost:8001/docs
- **健康检查**：http://localhost:8001/health

## 🔧 API接口详解

### 管理员认证

#### POST `/api/v1/admin/login` - 管理员登录

**请求体：**
```json
{
  "username": "admin",
  "password": "admin123456"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "admin": {
    "id": "683adb77ebb83cbca0f3247f",
    "username": "admin",
    "email": "admin@energy-system.com",
    "role": "admin",
    "access_features": [
      "manage_articles",
      "manage_users", 
      "manage_tags",
      "view_analytics",
      "system_config"
    ]
  },
  "permissions": ["manage_articles", "manage_users", ...]
}
```

### 文章管理

#### GET `/api/v1/admin/articles` - 获取文章列表

**查询参数：**
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）
- `content_type`: 内容类型筛选
- `search_keyword`: 搜索关键词

**响应：**
```json
{
  "items": [
    {
      "id": "article_id",
      "title": "文章标题",
      "content": "文章内容",
      "type": "news",
      "source": "来源机构",
      "publish_time": "2025-05-31T10:00:00",
      "energy_type_tags": ["天然气", "原油"],
      "region_tags": ["上海", "华东"],
      "view_count": 156
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "has_next": true
}
```

#### POST `/api/v1/admin/articles` - 创建文章

**请求体：**
```json
{
  "title": "新文章标题",
  "content": "文章内容...",
  "type": "news",
  "source": "来源机构",
  "publish_time": "2025-05-31T10:00:00",
  "link": "https://example.com/article",
  "basic_info_tags": ["政策解读"],
  "region_tags": ["上海", "华东"],
  "energy_type_tags": ["天然气"],
  "business_field_tags": ["贸易"],
  "beneficiary_tags": ["企业"],
  "policy_measure_tags": ["价格调整"],
  "importance_tags": ["重要"]
}
```

#### PUT `/api/v1/admin/articles/{article_id}` - 更新文章

**请求体：** 同创建文章，但所有字段都是可选的

#### DELETE `/api/v1/admin/articles/{article_id}` - 删除文章

**响应：**
```json
{
  "success": true,
  "message": "文章删除成功"
}
```

### 批量导入

#### POST `/api/v1/admin/articles/batch-import` - 批量导入文章

**请求体：**
```json
{
  "articles": [
    {
      "发布日期": "2025-05-31",
      "文档类型": "政策法规",
      "来源机构": "国家发改委",
      "标题": "关于天然气价格调整的通知",
      "文章内容": "...",
      "链接": "https://example.com",
      "基础信息标签": ["政策解读"],
      "地域标签": ["全国"],
      "能源品种标签": ["天然气"],
      "业务领域标签": ["价格管理"],
      "受益主体标签": ["消费者"],
      "关键措施标签": ["价格调整"],
      "重要性标签": ["重要"]
    }
  ],
  "auto_parse_tags": true,
  "overwrite_existing": false
}
```

**响应：**
```json
{
  "success": true,
  "total_articles": 1,
  "imported_count": 1,
  "updated_count": 0,
  "failed_count": 0,
  "failed_articles": [],
  "message": "批量导入完成"
}
```

#### POST `/api/v1/admin/articles/import-json-file` - 从JSON文件导入

**请求：** 文件上传（multipart/form-data）
- `file`: JSON文件
- `auto_parse_tags`: 是否自动解析标签（默认true）
- `overwrite_existing`: 是否覆盖已存在文章（默认false）

### 统计数据

#### GET `/api/v1/admin/stats` - 获取统计数据

**响应：**
```json
{
  "articles": {
    "total": 45,
    "by_type": {
      "news": 20,
      "policy": 15,
      "price": 8,
      "announcement": 2
    }
  },
  "users": {
    "total": 6,
    "admins": 1,
    "regular": 5
  }
}
```

## 🏷️ 标签系统详解

### 标签分类（9大类）

1. **基础信息标签** (`basic_info_tags`)
   - 政策解读、行业分析、市场动态等

2. **地域标签** (`region_tags`)
   - 城市：上海、北京、深圳等
   - 省份：江苏、浙江、广东等
   - 区域：华东、华南、华北等

3. **能源类型标签** (`energy_type_tags`)
   - 天然气、原油、液化天然气(LNG)、管道天然气(PNG)
   - 汽油、柴油、电力、煤炭等

4. **业务领域标签** (`business_field_tags`)
   - 贸易、运输、储存、加工等

5. **受益主体标签** (`beneficiary_tags`)
   - 企业、消费者、政府、行业等

6. **政策措施标签** (`policy_measure_tags`)
   - 价格调整、税收优惠、补贴政策等

7. **重要性标签** (`importance_tags`)
   - 重要、一般、紧急等

### 标签权重系统

推荐算法中的标签权重分配：

| 标签类型 | 权重系数 | 优先级 |
|---------|---------|--------|
| 地域标签 | ×3.0 | 🟢 最高 |
| 能源类型 | ×2.5 | 🟡 第二 |
| 基础信息 | ×1.0 | ⚪ 标准 |
| 业务领域 | ×0.8 | 🔸 较低 |
| 政策措施 | ×0.8 | 🔸 较低 |
| 重要性 | ×0.6 | 🔹 最低 |

## 📊 JSON导入格式

### 标准JSON文章格式

```json
{
  "发布日期": "2025-05-31",
  "文档类型": "政策法规",
  "来源机构": "国家发改委",
  "标题": "关于完善天然气价格机制的通知",
  "文章内容": "为进一步完善天然气价格机制...",
  "链接": "https://www.ndrc.gov.cn/xxgk/zcfb/tz/202505/t20250531_1234567.html",
  "基础信息标签": ["政策解读", "价格机制"],
  "地域标签": ["全国", "华东", "上海"],
  "能源品种标签": ["天然气", "管道天然气(PNG)"],
  "业务领域标签": ["价格管理", "市场监管"],
  "受益主体标签": ["天然气企业", "消费者"],
  "关键措施标签": ["价格调整", "市场化改革"],
  "重要性标签": ["重要"],
  "规范化地域标签": ["上海", "江苏", "华东地区"]
}
```

### 文档类型映射

| JSON中的类型 | 系统内部类型 | 说明 |
|-------------|-------------|------|
| 政策法规 | policy | 政策法规类 |
| 行业资讯 | news | 行业资讯类 |
| 调价公告 | price | 价格调整公告 |
| 交易公告 | announcement | 交易相关公告 |

## 🔒 权限管理

### 管理员权限列表

- `manage_articles`: 文章管理权限
- `manage_users`: 用户管理权限
- `manage_tags`: 标签管理权限
- `view_analytics`: 查看分析数据权限
- `system_config`: 系统配置权限

### JWT Token验证

所有管理员API都需要在请求头中包含JWT Token：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Token包含以下信息：
- `sub`: 用户ID
- `role`: 用户角色（admin）
- `exp`: 过期时间

## 🎯 前端管理界面

### 管理员登录页面

访问：http://localhost:5173/admin/login

**功能特点：**
- 🎨 现代化UI设计
- 🔄 加载状态显示
- ❌ 错误信息提示
- 🔒 安全提醒
- 📱 响应式布局

### 管理后台功能（待实现）

计划实现的管理后台页面：
- 📊 **仪表板** - 统计数据概览
- 📝 **文章管理** - 文章列表、编辑、删除
- 📤 **批量导入** - JSON文件上传和导入
- 👥 **用户管理** - 用户列表和权限管理
- 🏷️ **标签管理** - 标签分类和维护
- ⚙️ **系统设置** - 系统配置管理

## 🧪 测试验证

### 1. API测试

```bash
# 测试管理员登录
curl -X POST "http://localhost:8001/api/v1/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123456"}'

# 测试获取文章列表（需要Token）
curl -X GET "http://localhost:8001/api/v1/admin/articles" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 测试创建文章
curl -X POST "http://localhost:8001/api/v1/admin/articles" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "测试文章",
    "content": "这是一篇测试文章",
    "type": "news",
    "source": "测试来源",
    "energy_type_tags": ["天然气"]
  }'
```

### 2. 前端测试

1. 访问管理员登录页面：http://localhost:5173/admin/login
2. 使用默认账户登录：`admin` / `admin123456`
3. 验证登录成功后的跳转和状态管理

### 3. 批量导入测试

准备JSON文件并通过API上传：

```bash
curl -X POST "http://localhost:8001/api/v1/admin/articles/import-json-file" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@test_articles.json" \
  -F "auto_parse_tags=true"
```

## 🔧 故障排除

### 常见问题

1. **登录失败**
   - 检查用户名密码是否正确
   - 确认管理员用户已创建
   - 查看后端日志：`tail -f backend.log`

2. **Token过期**
   - 重新登录获取新Token
   - 检查系统时间是否正确

3. **权限不足**
   - 确认用户角色为`admin`
   - 检查Token中的权限信息

4. **导入失败**
   - 检查JSON格式是否正确
   - 确认文件编码为UTF-8
   - 查看错误详情和失败文章列表

### 日志查看

```bash
# 查看后端日志
tail -f backend.log

# 查看前端日志
tail -f frontend.log

# 查看启动日志
tail -f startup.log
```

## 📈 性能优化

### 数据库索引

系统已为以下字段创建索引：
- `title`: 文章标题搜索
- `type`: 内容类型筛选
- `publish_time`: 发布时间排序
- `energy_type_tags`: 能源类型筛选
- `region_tags`: 地域标签筛选

### 缓存策略

- **文章列表**: 建议缓存5分钟
- **统计数据**: 建议缓存15分钟
- **用户权限**: 建议缓存30分钟

## 🚀 部署建议

### 生产环境配置

1. **安全设置**
   - 修改默认管理员密码
   - 使用强密码策略
   - 启用HTTPS
   - 配置防火墙规则

2. **性能优化**
   - 启用数据库连接池
   - 配置Redis缓存
   - 使用CDN加速静态资源
   - 启用Gzip压缩

3. **监控告警**
   - 配置日志收集
   - 设置性能监控
   - 配置错误告警
   - 定期备份数据

## 📝 更新日志

### v1.0.0 (2025-05-31)
- ✅ 实现管理员登录认证
- ✅ 实现文章CRUD操作
- ✅ 实现批量导入功能
- ✅ 实现标签智能解析
- ✅ 实现权限验证系统
- ✅ 实现前端登录页面
- ✅ 实现状态管理

---

🎯 **系统状态**: 管理员功能已完整实现并测试通过  
🔧 **维护**: 定期更新文档和功能优化  
📞 **支持**: 如有问题请查看日志或联系开发团队 