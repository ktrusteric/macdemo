# OpenResty 负载均衡管理平台 - 快速启动参考

## 🚀 一键启动（推荐）

```bash
./start_all.sh
```

## 📋 分别启动

### 后端服务（端口8001）
```bash
./start_backend.sh
```

### 前端服务（端口5173）
```bash
./start_frontend.sh
```

## 🌐 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **后端API** | http://localhost:8001 | FastAPI服务 |
| **API文档** | http://localhost:8001/docs | Swagger UI |
| **健康检查** | http://localhost:8001/health | 服务状态 |
| **前端应用** | http://localhost:5173 | Vue.js开发服务器 |

## 🔧 环境确认

根据您的资料，项目已配置为：
- ✅ **后端端口**: 8001（已在所有配置文件中确认）
- ✅ **前端API配置**: 指向 http://localhost:8001/api/v1
- ✅ **无虚拟环境**: 使用系统Python环境
- ✅ **前端Vue项目**: frontend-vue目录

## 🛠️ 端口检查

```bash
# 检查8001端口占用
lsof -i:8001

# 检查5173端口占用  
lsof -i:5173

# 测试后端健康状态
curl http://localhost:8001/health
```

## 📁 项目结构（已清理）

```
macdemo/
├── backend/                 # Python FastAPI 后端（端口8001）
├── frontend-vue/           # Vue.js 前端（端口5173）
├── start_all.sh            # 完整启动脚本
├── start_backend.sh        # 后端启动脚本
├── start_frontend.sh       # 前端启动脚本
└── SIMPLIFIED_SETUP.md     # 详细设置说明
```

## ⚠️ 注意事项

1. **端口8001**: 确保此端口未被其他服务占用
2. **无虚拟环境**: Python依赖安装到系统环境
3. **热重载**: 开发模式支持代码变更自动重启
4. **CORS**: 后端已配置跨域支持前端调用 