#!/bin/bash

echo "=== OpenResty 负载均衡管理平台 - 环境检查 ==="

# 检查基础环境
echo "📋 基础环境检查"
echo "Python版本: $(python3 --version)"
echo "Node.js版本: $(node --version)"
echo "npm版本: $(npm --version)"
echo ""

# 检查端口占用
echo "🔌 端口状态检查"
echo "检查8001端口（后端）:"
lsof -i:8001 && echo "✅ 后端服务运行中" || echo "❌ 后端服务未运行"

echo "检查5173端口（前端）:"
lsof -i:5173 && echo "✅ 前端服务运行中" || echo "❌ 前端服务未运行"
echo ""

# 检查后端API
echo "🚀 API连接测试"
echo "测试后端根接口:"
curl -s http://localhost:8001/ | jq . 2>/dev/null && echo "✅ 根API正常" || echo "❌ 根API无响应"

echo "测试健康检查接口:"
curl -s http://localhost:8001/health | jq . 2>/dev/null && echo "✅ 健康检查正常" || echo "❌ 健康检查失败"
echo ""

# 检查项目结构
echo "📁 项目结构检查"
echo "后端目录: $([ -d backend ] && echo "✅ 存在" || echo "❌ 缺失")"
echo "前端目录: $([ -d frontend-vue ] && echo "✅ 存在" || echo "❌ 缺失")"
echo "后端虚拟环境: $([ -d backend/venv ] && echo "✅ 存在" || echo "❌ 缺失")"
echo "前端依赖: $([ -d frontend-vue/node_modules ] && echo "✅ 已安装" || echo "❌ 未安装")"
echo ""

# 访问地址提示
echo "🌐 访问地址"
echo "后端API: http://localhost:8001"
echo "API文档: http://localhost:8001/docs"
echo "前端应用: http://localhost:5173"
echo ""

echo "=== 检查完成 ===" 