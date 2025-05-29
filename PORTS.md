# 能源信息服务系统 - 端口配置清单

## 🔧 核心服务端口分配

| 服务名称 | 端口 | 协议 | 用途 | 访问地址 |
|---------|------|------|------|----------|
| **MongoDB数据库** | `27017` | TCP | 数据存储 | `mongodb://localhost:27017/energy_info` |
| **Python后端API** | `8001` | HTTP | FastAPI服务 | `http://localhost:8001` |
| **React前端应用** | `5173` | HTTP | Vite开发服务器 | `http://localhost:5173` |
| **React前端(备用)** | `3000` | HTTP | 生产环境备用 | `http://localhost:3000` |

## 🌐 外部AI助手服务

| 助手名称 | 服务地址 | Bot ID | Token | 功能描述 |
|---------|----------|--------|-------|----------|
| **客服助手** | `https://ai.wiseocean.cn` | `9714d9bc-31ca-40b5-a720-4329f5fc4af7` | `e0dc8833077b48669a04ad4a70a7ebe2` | 账户问题、功能咨询、技术支持、操作指导 |
| **资讯助手** | `https://ai.wiseocean.cn` | `158ab70e-2996-4cce-9822-6f8195a7cfa5` | `9bc6008decb94efeaee65dd076aab5e8` | 市场快讯、政策解读、行业分析、趋势预测 |
| **交易助手** | `https://ai.wiseocean.cn` | `1e72acc1-43a8-4cda-8d54-f409c9c5d5ed` | `18703d14357040c88f32ae5e4122c2d6` | 策略建议、风险评估、交易分析、市场机会 |

## 📊 服务状态检查端点

| 检查项目 | 检查地址 | 预期响应 | 说明 |
|---------|----------|----------|------|
| **后端健康检查** | `http://localhost:8001/api/v1/content/` | `{"message": "Energy Info System API"}` | 后端服务基本状态 |
| **API文档** | `http://localhost:8001/docs` | Swagger UI页面 | FastAPI自动生成的API文档 |
| **前端应用** | `http://localhost:5173/` | React应用页面 | 前端应用主页 |
| **MongoDB连接** | `mongodb://localhost:27017/energy_info` | 数据库连接成功 | 数据库连接状态 |

## 🔍 端口检查命令

### 检查端口占用
```bash
# 检查所有核心端口
lsof -i:27017,8001,5173

# 检查单个端口
lsof -i:8001
netstat -tlnp | grep 8001
ss -tlnp | grep 8001
```

### 检查进程状态
```bash
# 检查MongoDB进程
pgrep -x mongod
ps aux | grep mongod

# 检查Python后端进程
pgrep -f "uvicorn.*app.main:app"
ps aux | grep uvicorn

# 检查前端进程
pgrep -f "vite.*dev"
ps aux | grep vite
```

### 服务健康检查
```bash
# 后端API健康检查
curl -s http://localhost:8001/api/v1/content/ | jq .

# 前端应用检查
curl -s -I http://localhost:5173/

# MongoDB连接检查
mongo --eval "db.runCommand('ping')"
```

## 🛠️ 常见端口问题解决

### 端口被占用
```bash
# 查找占用进程
lsof -i:8001

# 强制终止进程
kill -9 <PID>

# 批量终止相关进程
pkill -f "uvicorn.*app.main:app"
pkill -f "vite.*dev"
```

### 服务启动失败
```bash
# 检查日志
tail -f backend.log
tail -f frontend.log

# 手动启动服务进行调试
cd backend && python3 -m uvicorn app.main:app --reload --port 8001
cd frontend && npm run dev
```

## 📋 环境变量配置

### 后端环境变量 (.env)
```bash
PROJECT_NAME="Energy Info System"
VERSION="1.0.0"
API_V1_STR="/api/v1"
MONGODB_URL="mongodb://localhost:27017"
DATABASE_NAME="energy_info"
AI_BACKEND_URL="https://ai.wiseocean.cn"
AI_API_TIMEOUT=30
SECRET_KEY="your-secret-key-here"
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

### 前端环境变量 (.env)
```bash
VITE_API_BASE_URL=http://localhost:8001/api/v1
VITE_AI_BACKEND_URL=https://ai.wiseocean.cn
```

## 🚀 快速启动检查清单

- [ ] MongoDB服务运行 (端口27017)
- [ ] 后端API服务运行 (端口8001)
- [ ] 前端应用服务运行 (端口5173)
- [ ] 后端健康检查通过
- [ ] 前端页面可访问
- [ ] API文档可访问
- [ ] 数据库连接正常

## 📞 故障排查联系

如遇到端口冲突或服务启动问题，请：

1. 运行 `./start-all.sh` 选择 "8) 查看端口占用"
2. 运行 `./start-all.sh` 选择 "7) 查看服务状态"
3. 查看相关日志文件
4. 检查环境变量配置

---

**更新时间**: 2024年12月
**维护者**: 能源信息服务系统开发团队 