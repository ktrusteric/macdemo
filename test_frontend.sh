#!/bin/bash

echo "=== 前端页面测试 ==="

echo "1. 检查服务状态"
lsof -i:5173 > /dev/null && echo "✅ 前端服务运行中" || echo "❌ 前端服务未运行"

echo ""
echo "2. 检查主页HTML结构"
curl -s http://localhost:5173 | grep -q "div id=\"app\"" && echo "✅ 主页HTML结构正常" || echo "❌ 主页HTML结构异常"

echo ""
echo "3. 检查登录页面路由"
curl -s http://localhost:5173/login | grep -q "div id=\"app\"" && echo "✅ 登录页面路由正常" || echo "❌ 登录页面路由异常"

echo ""
echo "4. 检查JavaScript加载"
curl -s http://localhost:5173 | grep -q "script type=\"module\"" && echo "✅ JavaScript模块正常" || echo "❌ JavaScript模块异常"

echo ""
echo "5. 检查API连接"
curl -s http://localhost:8001/health > /dev/null && echo "✅ 后端API正常" || echo "❌ 后端API异常"

echo ""
echo "=== 测试完成 ===" 