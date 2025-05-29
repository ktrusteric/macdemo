# 能源交易系统 (Energy Trading System)

🌟 一个全功能的能源交易信息服务系统，集成了用户管理、标签系统、内容推荐和AI助手功能。

## 🚀 项目特性

### 核心功能
- **用户管理系统** - 完整的用户注册、登录、认证功能
- **智能标签系统** - 多维度用户标签管理和分类
- **内容推荐引擎** - 基于用户标签的个性化内容推荐
- **AI助手集成** - 集成多个专业AI助手（客服、资讯、交易）
- **数据可视化** - 丰富的数据展示和分析功能

### 技术栈
- **前端**: React 18 + TypeScript + Vite + TailwindCSS + Redux Toolkit
- **后端**: Python 3.9+ + FastAPI + MongoDB + Pydantic
- **AI集成**: 智海AI平台集成
- **部署**: Docker支持，可快速部署

## 📁 项目结构

```
energy-trading-system/
├── frontend/                 # 前端React应用
│   ├── src/
│   │   ├── components/      # React组件
│   │   ├── pages/           # 页面组件
│   │   ├── services/        # API服务
│   │   ├── store/           # Redux状态管理
│   │   └── types/           # TypeScript类型定义
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # 后端FastAPI应用
│   ├── app/
│   │   ├── api/             # API路由
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据模型
│   │   ├── services/        # 业务逻辑
│   │   └── utils/           # 工具函数
│   ├── scripts/             # 数据库脚本
│   └── requirements.txt
├── docs/                     # 文档
└── README.md
```

## 🏁 快速开始

### 环境要求
- Node.js 18+
- Python 3.9+
- MongoDB 4.4+

### 1. 克隆项目
```bash
git clone https://github.com/ktrusteric/macdemo.git
cd macdemo
```

### 2. 一键启动（推荐）
```bash
chmod +x start-all.sh
./start-all.sh
```

### 3. 手动启动

#### 启动后端
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### 启动前端
```bash
cd frontend
npm install
npm run dev
```

## 🌐 访问地址

- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:8001
- **API文档**: http://localhost:8001/docs

## 📚 主要功能模块

### 1. 用户标签管理
- 支持7大类标签：基础信息、地域、能源类型、业务领域、受益主体、政策措施、重要性
- 标签权重管理和动态调整
- 标签来源追踪（预设、手动、AI生成）

### 2. 内容推荐系统
- 基于用户标签的智能推荐算法
- 支持多种内容类型：政策文件、市场资讯、研究报告等
- 实时推荐评分和排序

### 2. AI助手集成
- **客服助手**: 智能客服支持
- **资讯助手**: 专业资讯解读
- **交易助手**: 交易指导和建议

### 4. 数据管理
- MongoDB数据库支持
- 完整的数据备份和恢复
- 数据迁移和同步工具

## 🔧 配置说明

### 环境变量配置

#### 后端配置 (backend/.env)
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=energy_trading
AI_BACKEND_URL=https://ai.wiseocean.cn
SECRET_KEY=your-secret-key-here
```

#### 前端配置 (frontend/.env)
```env
VITE_API_BASE_URL=http://localhost:8001
VITE_APP_NAME=能源交易系统
```

## 🧪 测试指南

### 运行系统测试
```bash
./test-system.sh
```

### API测试
访问 http://localhost:8001/docs 查看交互式API文档

### 功能测试
1. 用户注册/登录测试
2. 标签管理功能测试
3. 内容推荐准确性测试
4. AI助手响应测试

## 📈 开发指南

### 添加新的API端点
1. 在 `backend/app/api/` 中创建新的路由文件
2. 定义Pydantic模型在 `backend/app/models/`
3. 实现业务逻辑在 `backend/app/services/`

### 添加新的前端页面
1. 在 `frontend/src/pages/` 中创建新页面组件
2. 在 `frontend/src/services/` 中添加API调用
3. 更新路由配置

### 数据库操作
```bash
# 初始化数据库
cd backend && python init_db.py

# 导入测试数据
cd backend && python scripts/import_sample_data.py
```

## 🔄 部署指南

### Docker部署
```bash
# 构建镜像
docker build -t energy-trading-system .

# 运行容器
docker run -p 8001:8001 -p 5173:5173 energy-trading-system
```

### 生产环境部署
1. 配置Nginx反向代理
2. 设置SSL证书
3. 配置MongoDB集群
4. 设置监控和日志

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 联系我们

- 项目维护者: ktrusteric
- 邮箱: your-email@example.com
- 项目地址: https://github.com/ktrusteric/macdemo

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！
