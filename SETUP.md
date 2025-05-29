# 能源信息服务系统 - 设置和运行指南

## 后端设置

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下参数：

```env
# 项目信息
PROJECT_NAME="Energy Info System"
VERSION="1.0.0"
API_V1_STR="/api/v1"

# 数据库配置
MONGODB_URL="mongodb://localhost:27017"
DATABASE_NAME="energy_info"

# AI集成配置
AI_BACKEND_URL="https://ai.wiseocean.cn"
AI_API_TIMEOUT=30

# 安全配置
SECRET_KEY="your-secret-key-here"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS配置
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### 3. 启动MongoDB

使用Docker：
```bash
docker run -d --name mongodb -p 27017:27017 mongo:6
```

或者使用本地安装的MongoDB。

### 4. 导入示例数据

```bash
cd scripts
python import_sample_data.py
```

### 5. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API文档将在 http://localhost:8000/docs 可用。

## 前端设置

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
# API Base URL
VITE_API_BASE_URL=http://localhost:8000/api/v1

# AI Assistant URL
VITE_AI_BACKEND_URL=https://ai.wiseocean.cn
```

### 3. 启动开发服务器

```bash
npm run dev
```

前端应用将在 http://localhost:5173 可用。

## 功能测试

### 1. 用户标签管理
- 访问 http://localhost:5173/tags
- 管理7大类用户标签

### 2. 内容浏览
- 访问 http://localhost:5173/content
- 浏览能源资讯内容

### 3. AI助手
- 访问 http://localhost:5173/ai-assistants
- 使用三个AI助手：客服助手、资讯助手、交易助手

### 4. 仪表盘
- 访问 http://localhost:5173/
- 查看个性化推荐和统计信息

## 常见问题

### MongoDB连接失败
- 确保MongoDB正在运行
- 检查连接URL是否正确

### CORS错误
- 确保后端的CORS配置包含前端URL
- 检查API请求的URL是否正确

### AI助手无法加载
- 检查网络连接
- 确认AI服务URL可访问 