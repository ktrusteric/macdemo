#!/bin/bash

echo "=== 前端页面内容测试 ==="

echo "1. 测试登录页面访问"
response=$(curl -s http://localhost:5173/login)
if [[ $response == *"div id=\"app\""* ]]; then
    echo "✅ 登录页面HTML结构正常"
else
    echo "❌ 登录页面HTML结构异常"
fi

echo ""
echo "2. 测试主页重定向到登录页面"
response=$(curl -s http://localhost:5173/)
if [[ $response == *"div id=\"app\""* ]]; then
    echo "✅ 主页HTML结构正常"
else
    echo "❌ 主页HTML结构异常"
fi

echo ""
echo "3. 测试Vue.js是否正常加载"
response=$(curl -s http://localhost:5173/src/main.ts)
if [[ $response == *"createApp"* ]] || [[ $response == *"mount"* ]]; then
    echo "✅ Vue.js主文件正常"
else
    echo "❌ Vue.js主文件异常"
fi

echo ""
echo "4. 测试路由配置"
response=$(curl -s http://localhost:5173/src/router/index.ts)
if [[ $response == *"router"* ]] || [[ $response == *"routes"* ]]; then
    echo "✅ 路由配置正常"
else
    echo "❌ 路由配置异常"
fi

echo ""
echo "5. 测试Store配置"
response=$(curl -s http://localhost:5173/src/store/user.ts)
if [[ $response == *"defineStore"* ]] || [[ $response == *"pinia"* ]]; then
    echo "✅ Store配置正常"
else
    echo "❌ Store配置异常"
fi

echo ""
echo "=== 内容测试完成 ==="
echo ""
echo "🌐 现在可以访问以下地址测试前端："
echo "- 主页: http://localhost:5173"
echo "- 登录页: http://localhost:5173/login"
echo "- 后端API: http://localhost:8001/docs"
echo ""
echo "📝 注意: 如果页面显示空白，请在浏览器中按F12打开开发者工具查看控制台错误" 