# OpenResty 负载均衡管理平台 - 简化版设置

## 项目结构（已清理）

```
macdemo/
├── backend/                 # Python FastAPI 后端
│   ├── app/                # FastAPI 应用代码
│   ├── requirements.txt    # Python 依赖
│   └── ...
├── frontend-vue/           # Vue.js 前端
│   ├── src/               # Vue 源代码
│   ├── package.json       # Node.js 依赖
│   └── ...
├── start_backend.sh        # 后端启动脚本
├── start_frontend.sh       # 前端启动脚本
└── docs/                   # 项目文档
```

## 环境清理内容

✅ **已删除的内容：**
- `/venv/` - 根目录Python虚拟环境
- `/backend/venv/` - 后端Python虚拟环境  
- `/frontend.bak/` - 废弃的前端目录
- 根目录下的 `package.json`, `package-lock.json`, `node_modules/`

## 快速启动

### 1. 启动后端服务
```bash
./start_backend.sh
```
- 后端服务地址：http://localhost:8001
- API文档地址：http://localhost:8001/docs

### 2. 启动前端服务  
```bash
./start_frontend.sh
```
- 前端服务地址：http://localhost:3000 (或Vite默认端口)

## 环境要求

### Python 环境（后端）
- Python 3.8+
- 使用系统级Python，不依赖虚拟环境
- 依赖包将安装到系统Python环境

### Node.js 环境（前端）
- Node.js 16+
- npm 或 yarn
- 依赖包安装在 `frontend-vue/node_modules/`

## 开发说明

### 后端开发
```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 前端开发
```bash
cd frontend-vue  
npm run dev
```

## 生产环境部署

### 后端部署
```bash
cd backend
pip3 install -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 前端部署
```bash
cd frontend-vue
npm install
npm run build
# 将 dist/ 目录部署到Web服务器
```

## 注意事项

1. **无虚拟环境**：当前配置不使用Python虚拟环境，所有Python包安装到系统环境
2. **端口配置**：确保8001端口（后端）和前端端口不冲突
3. **依赖管理**：Python依赖使用pip3安装，Node.js依赖使用npm管理
4. **开发模式**：两个启动脚本都支持热重载开发模式

## 端口映射
- **后端API服务**：8001端口
- **前端开发服务器**：5173端口（Vite默认）
- **API接口地址**：http://localhost:8001/api/v1
- **API文档地址**：http://localhost:8001/docs 