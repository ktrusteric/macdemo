# AI智能助手系统 - 部署检查清单

## 🚀 部署前准备

### 1. 环境依赖检查
- [ ] **Python 3.8+** 已安装
- [ ] **Node.js 16+** 已安装  
- [ ] **MongoDB** 已安装并运行
- [ ] **Git** 已安装（用于克隆代码）

### 2. 网络和端口检查
- [ ] **端口 8001** 可用（后端服务）
- [ ] **端口 5173** 可用（前端开发服务）
- [ ] **端口 27017** 可用（MongoDB默认端口）
- [ ] 网络可访问 `https://ai.wiseocean.cn`（AI服务端点）

## 📦 后端部署

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```
- [ ] 所有Python依赖安装成功
- [ ] 无版本冲突错误

### 2. 配置检查
```bash
# 检查配置文件
cat backend/app/core/config.py
```
- [ ] `MONGODB_URL` 配置正确
- [ ] `AI_BACKEND_URL` 配置正确
- [ ] `DATABASE_NAME` 配置正确

### 3. 数据库连接测试
```bash
# 启动MongoDB
mongod --dbpath /data/db

# 测试连接
mongo --eval "db.version()"
```
- [ ] MongoDB服务正常启动
- [ ] 数据库连接测试成功

### 4. 启动后端服务
```bash
cd backend
python main.py
```
- [ ] 后端服务启动成功
- [ ] 控制台无错误信息
- [ ] 浏览器访问 `http://localhost:8001/health` 返回正常

## 🎨 前端部署

### 1. 安装依赖
```bash
cd frontend-vue
npm install
```
- [ ] Node.js依赖安装成功
- [ ] 无版本冲突警告

### 2. 环境配置检查
```bash
# 检查代理配置
cat frontend-vue/vite.config.ts
```
- [ ] API代理配置指向 `http://localhost:8001`
- [ ] 端口配置正确

### 3. 启动前端服务
```bash
cd frontend-vue
npm run dev
```
- [ ] 前端服务启动成功
- [ ] 浏览器访问 `http://localhost:5173` 正常

## 🧪 功能测试

### 1. 基础API测试
```bash
# 运行测试脚本
python test_ai_assistant.py
```
- [ ] AI助手配置获取成功
- [ ] 消息发送功能正常
- [ ] 会话历史功能正常
- [ ] 搜索功能正常
- [ ] 统计功能正常

### 2. 前端功能测试
- [ ] 悬浮按钮显示正常
- [ ] 助手选择器工作正常
- [ ] 聊天窗口功能完整
- [ ] 最小化/恢复功能正常
- [ ] 快捷键（Ctrl+K, ESC）响应正常

### 3. 管理后台测试
- [ ] 管理员登录功能正常
- [ ] 聊天记录管理页面显示正常
- [ ] 统计卡片数据正确
- [ ] 搜索筛选功能正常
- [ ] 会话详情查看正常

## 🔧 高级配置

### 1. AI服务配置验证
```bash
# 测试AI服务连接
curl -X POST "https://ai.wiseocean.cn/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"bot_id":"9714d9bc-31ca-40b5-a720-4329f5fc4af7","token":"e0dc8833077b48669a04ad4a70a7ebe2","message":"测试"}'
```
- [ ] AI服务响应正常
- [ ] 三个助手ID和Token有效

### 2. 数据库优化
```bash
# MongoDB索引创建
mongo energy_info --eval "
  db.ai_chat_sessions.createIndex({session_id: 1});
  db.ai_chat_sessions.createIndex({user_id: 1});
  db.ai_chat_sessions.createIndex({assistant_type: 1});
  db.ai_chat_sessions.createIndex({created_at: -1});
"
```
- [ ] 数据库索引创建成功
- [ ] 查询性能优化

### 3. 安全配置
- [ ] 生产环境更改 `SECRET_KEY`
- [ ] CORS配置限制为生产域名
- [ ] 管理员账户密码强度检查

## 🎯 生产部署注意事项

### 1. 服务器配置
- [ ] 服务器资源充足（CPU、内存、磁盘）
- [ ] 防火墙配置正确
- [ ] SSL证书配置（HTTPS）
- [ ] 负载均衡配置（如需要）

### 2. 监控和日志
- [ ] 应用日志配置
- [ ] 错误监控设置
- [ ] 性能监控配置
- [ ] 数据库监控设置

### 3. 备份策略
- [ ] 数据库定期备份
- [ ] 应用代码版本控制
- [ ] 配置文件备份
- [ ] 灾难恢复计划

## 🚨 故障排除

### 常见问题及解决方案

#### 1. 后端服务启动失败
```bash
# 检查端口占用
lsof -i :8001

# 检查Python环境
python --version
pip list
```

#### 2. 前端访问失败
```bash
# 检查代理配置
cat frontend-vue/vite.config.ts

# 清理缓存重新安装
rm -rf node_modules package-lock.json
npm install
```

#### 3. AI服务连接失败
- 检查网络连接
- 验证AI服务Token
- 确认服务端点URL

#### 4. 数据库连接失败
```bash
# 检查MongoDB服务
ps aux | grep mongod
netstat -tulpn | grep 27017

# 重启MongoDB
sudo systemctl restart mongod
```

## ✅ 部署完成确认

### 最终检查清单
- [ ] 所有服务正常运行
- [ ] 所有功能测试通过
- [ ] 性能表现满足要求
- [ ] 安全配置已完成
- [ ] 监控系统正常工作
- [ ] 备份策略已执行
- [ ] 文档和运维手册已准备

---

## 📞 技术支持

如遇到问题，请检查：
1. **错误日志**：查看控制台和应用日志
2. **网络连接**：确认AI服务和数据库连接正常
3. **版本兼容性**：确认所有依赖版本匹配
4. **配置文件**：验证所有配置项正确性

**部署成功标志**：
- 前端页面正常显示AI助手悬浮按钮
- 点击可以选择三种助手并正常对话
- 管理后台可以查看聊天记录和统计数据

🎉 **恭喜！AI智能助手系统部署完成！** 