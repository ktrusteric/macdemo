# 🚀 OpenResty 负载均衡管理平台 - 启动指南

## 📋 概述

本系统提供了完全自动化的启动脚本，包含数据初始化功能。启动时会自动导入**规范化测试数据**，确保系统开箱即用。

## 🎯 新增启动脚本特点

### ✅ 自动化程度更高
- 自动检查系统依赖（Python3、Node.js、MongoDB）
- 自动创建和配置Python虚拟环境
- 自动安装项目依赖
- 自动启动MongoDB服务（macOS）
- 自动检查和释放端口占用

### ✅ 智能数据初始化
- 使用规范化的`简化测试数据.json`文件
- 自动检测数据库状态，避免重复导入
- 导入45篇优化标签的能源文章
- 创建5个基于覆盖率优化的Demo用户

### ✅ 完善的错误处理
- 详细的彩色日志输出
- 智能错误恢复机制
- 优雅的服务停止功能
- 资源清理和状态检查

## 📁 启动脚本文件

| 脚本文件 | 用途 | 说明 |
|---------|------|------|
| `start_all_with_data.sh` | **完整启动** | 前后端+数据初始化 |
| `start_backend_with_data.sh` | 仅后端启动 | 后端+数据初始化 |
| `stop_backend.sh` | 停止服务 | 优雅停止后端服务 |
| `test_startup_scripts.sh` | 测试脚本 | 验证启动脚本功能 |

## 🚀 快速启动

### 方式一：完整启动（推荐）

```bash
# 一键启动前后端服务并初始化数据
./start_all_with_data.sh
```

**启动流程：**
1. 🔍 检查系统环境（Python3、Node.js、MongoDB）
2. 🐍 设置Python虚拟环境和依赖
3. 🗃️ 检查并初始化MongoDB数据库
4. 📊 导入规范化测试数据（如需要）
5. 🔧 启动后端服务 (http://localhost:8001)
6. 🌐 启动前端服务 (http://localhost:5173)

### 方式二：仅启动后端

```bash
# 仅启动后端服务并初始化数据
./start_backend_with_data.sh
```

适用于：
- 前端调试开发
- API测试
- 数据库管理

## 📊 规范化数据说明

### 数据文件：`backend/scripts/简化测试数据.json`

**数据特点：**
- **文章数量**：45篇能源政策文档
- **标签优化**：每篇文章平均3-5个标签（原15+标签优化后）
- **标签质量**：保留高相关性标签，移除冗余标签

**能源标签覆盖率：**
```
天然气：         42.2% (19篇)
原油：           42.2% (19篇)
液化天然气(LNG)： 24.4% (11篇)
管道天然气(PNG)： 22.2% (10篇)
电力：           8.9% (4篇)
```

**地域标签覆盖率：**
```
总覆盖率：       66.7% (30/45篇)
主要地区：       上海28.9%、新疆8.9%、北京8.9%
支持城市：       68个主要城市
自动识别：       城市→省份→地区三层标签
```

### Demo用户配置（优化后）

每个用户专注1个能源类型，基于覆盖率优化：

| 用户 | 城市 | 能源类型 | 覆盖率 | 预期文章数 |
|------|------|----------|--------|------------|
| 张先生 | 上海 | 天然气 | 42.2% | 19篇 |
| 李女士 | 北京 | 原油 | 42.2% | 19篇 |
| 王先生 | 深圳 | LNG | 24.4% | 11篇 |
| 陈女士 | 广州 | PNG | 22.2% | 10篇 |
| 刘先生 | 成都 | 电力 | 8.9% | 4篇 |

## 🛠️ 服务管理

### 启动状态检查

```bash
# 检查后端服务
curl http://localhost:8001/health

# 检查前端服务
curl http://localhost:5173

# 检查数据库内容
curl http://localhost:8001/content | jq '.total'
```

### 停止服务

```bash
# 优雅停止后端
./stop_backend.sh

# 手动停止（如果脚本不可用）
pkill -f "uvicorn.*8001"
pkill -f "vite.*5173"

# 强制停止
pkill -9 -f "uvicorn.*8001"
```

### 重启服务

```bash
# 停止现有服务
./stop_backend.sh

# 重新启动
./start_all_with_data.sh
```

## 🔧 高级配置

### 环境变量

```bash
# MongoDB连接
export MONGODB_URL="mongodb://localhost:27017"

# 数据库名称
export DATABASE_NAME="energy_info"

# 后端端口
export BACKEND_PORT="8001"

# 前端端口  
export FRONTEND_PORT="5173"
```

### 自定义数据导入

```bash
# 使用完整原始数据（每篇15+标签）
cd backend/scripts
python3 import_sample_data.py --full

# 使用简化数据（默认，每篇3-5标签）
python3 import_sample_data.py --use-simplified-data
```

### 手动数据管理

```bash
# 清空数据库
mongo energy_info --eval "db.dropDatabase()"

# 仅导入文章（不导入用户）
cd backend/scripts  
python3 -c "
import asyncio
from import_sample_data import import_articles
asyncio.run(import_articles(use_simplified=True))
"

# 仅创建用户（不导入文章）
python3 -c "
import asyncio
from import_sample_data import create_sample_users
asyncio.run(create_sample_users())
"
```

## 🧪 测试和验证

### 运行完整测试

```bash
# 测试启动脚本功能
./test_startup_scripts.sh
```

**测试项目：**
- ✅ 规范化数据文件检查
- ✅ 后端启动脚本（含数据初始化）
- ✅ 停止脚本功能
- ✅ 自动数据导入功能
- ✅ Demo用户创建功能

### 验证系统功能

1. **访问前端** - http://localhost:5173
2. **查看API文档** - http://localhost:8001/docs
3. **登录Demo用户** - 任选一个Demo用户测试
4. **检查推荐内容** - 验证个性化推荐
5. **标签管理** - 测试标签修改功能

## 🚨 故障排除

### 常见问题

**1. MongoDB连接失败**
```bash
# 启动MongoDB服务
brew services start mongodb-community

# 检查MongoDB状态
brew services list | grep mongodb
```

**2. 端口被占用**
```bash
# 查看端口占用
lsof -i:8001
lsof -i:5173

# 强制释放端口
pkill -f "uvicorn.*8001"
pkill -f "vite.*5173"
```

**3. Python依赖问题**
```bash
# 删除虚拟环境重新创建
rm -rf backend/venv
cd backend && python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. 前端依赖问题**
```bash
# 重新安装前端依赖
cd frontend-vue
rm -rf node_modules package-lock.json
npm install
```

### 日志查看

```bash
# 后端日志
tail -f backend.log

# 前端日志  
tail -f frontend.log

# 系统日志
tail -f /var/log/system.log | grep -i mongo
```

## 📚 相关文档

- [README.md](README.md) - 系统配置和标签说明
- [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md) - 优化总结
- [backend/scripts/](backend/scripts/) - 数据处理脚本
- API文档 - http://localhost:8001/docs

---

🎉 **现在您可以一键启动完整的能源信息服务系统！** 