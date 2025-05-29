# 🚨 紧急测试指南 - 解决页面空白问题

## 📍 当前状态
- **前端服务**: http://localhost:5174 ✅ 运行中
- **后端服务**: http://localhost:8001 ✅ 运行中
- **认证**: ✅ 已完全绕过
- **问题**: 页面显示空白

## 🔧 立即测试这些地址

### 1. 基础连接测试
```
http://localhost:5174/test
```
**说明**: 简单测试页面，如果显示红色标题，说明React正常工作

### 2. 主页测试 (使用测试组件)
```
http://localhost:5174/
```
**说明**: 已临时替换为测试组件，应该看到红色标题和时间显示

### 3. 公共页面测试
```
http://localhost:5174/login
http://localhost:5174/register
```
**说明**: 这些页面不需要认证，应该正常显示

## 🔍 诊断步骤

### 步骤1: 检查基础连接
1. 访问 `http://localhost:5174/test`
2. 如果看到红色标题 "测试页面" - React工作正常
3. 如果还是空白 - 前端服务有问题

### 步骤2: 检查控制台
1. 按F12打开开发者工具
2. 查看Console标签页是否有错误
3. 查看Network标签页是否有请求失败

### 步骤3: 强制刷新
1. 按Ctrl + F5 强制刷新
2. 清除浏览器缓存
3. 尝试无痕模式

## 🛠️ 可能的解决方案

### 方案1: 检查前端服务日志
```bash
# 查看前端服务是否有错误
cd /root/energy-trading-system/frontend
ps aux | grep vite
```

### 方案2: 重启前端服务
```bash
# 停止当前服务
pkill -f vite

# 重新启动
cd /root/energy-trading-system/frontend
npm run dev
```

### 方案3: 检查端口占用
```bash
# 确认5174端口状态
netstat -tlnp | grep 5174
```

### 方案4: 检查防火墙和网络
```bash
# 检查本地访问
curl -I http://localhost:5174
```

## 📋 预期结果

### 正常情况应该看到:
- `/test` 页面: 红色标题 "测试页面 - 如果您看到这个，说明React正常工作"
- `/` 页面: 相同的测试内容，但有左侧导航栏
- `/login` 页面: 登录表单

### 如果还是空白:
1. **检查浏览器**: 尝试不同浏览器 (Chrome, Firefox, Edge)
2. **检查网络**: 确认可以访问localhost
3. **检查服务**: 前端服务可能崩溃

## 🔥 紧急恢复步骤

如果上述方法都不行，执行以下恢复操作:

```bash
# 1. 完全重启前端服务
cd /root/energy-trading-system/frontend
pkill -f vite
pkill -f npm
sleep 3
npm run dev

# 2. 清理node_modules重新安装
rm -rf node_modules package-lock.json
npm install
npm run dev

# 3. 检查端口冲突
lsof -i :5174
# 如果有其他进程占用，kill掉再重启
```

## 📞 诊断信息收集

如果问题持续，请提供以下信息:

1. **浏览器信息**: 使用什么浏览器和版本
2. **控制台错误**: F12开发者工具中的错误信息
3. **网络请求**: Network标签页中的请求状态
4. **服务状态**: `ps aux | grep vite` 的输出
5. **端口状态**: `netstat -tlnp | grep 517` 的输出

## ⚡ 快速验证命令

```bash
# 一键检查所有状态
echo "=== 前端服务状态 ==="
ps aux | grep vite | grep -v grep

echo "=== 端口状态 ==="
netstat -tlnp | grep 517

echo "=== 测试HTTP响应 ==="
curl -I http://localhost:5174

echo "=== 检查进程 ==="
lsof -i :5174
```

---

**现在请立即访问: http://localhost:5174/test**

如果能看到红色的测试页面，说明前端正常工作，问题在组件层面。
如果还是空白，说明前端服务有问题，需要重启服务。 