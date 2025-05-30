#!/bin/bash

echo "=== 登录页面修复测试 ==="
echo ""

# 等待服务启动
echo "等待前端服务启动..."
sleep 5

echo "1. 测试前端服务是否运行"
if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ 前端服务正常运行在端口5173"
else
    echo "❌ 前端服务未启动"
    exit 1
fi

echo ""
echo "2. 测试后端服务是否运行"
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ 后端服务正常运行在端口8001"
else
    echo "❌ 后端服务未启动"
fi

echo ""
echo "3. 测试登录页面内容"
login_content=$(curl -s http://localhost:5173/login)
if [[ $login_content == *"OpenResty 负载均衡管理平台"* ]]; then
    echo "✅ 登录页面标题正确"
else
    echo "❌ 登录页面标题异常"
fi

echo ""
echo "4. 测试API请求"
api_test=$(curl -s http://localhost:5173/src/api/request.ts)
if [[ $api_test == *"axios"* ]] || [[ $api_test == *"baseURL"* ]]; then
    echo "✅ API配置文件正常"
else
    echo "❌ API配置文件异常"
fi

echo ""
echo "=== 测试完成 ==="
echo ""
echo "🌐 请访问以下地址测试："
echo "- 登录页面: http://localhost:5173/login"
echo "- 后端API: http://localhost:8001/docs"
echo ""
echo "📝 测试账号:"
echo "- zhang@newenergy.com / demo123"
echo "- li@traditional.com / demo123"
echo "- wang@carbon.com / demo123"
echo ""
echo "💡 如果登录按钮仍显示'在开发中'，请清除浏览器缓存后重试" 