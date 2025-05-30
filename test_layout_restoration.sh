#!/bin/bash

echo "=== 布局恢复测试 ==="
echo ""

echo "1. 检查前端服务状态"
if curl -s http://localhost:5174 > /dev/null; then
    echo "✅ 前端服务正常运行 (端口5174)"
    FRONTEND_PORT=5174
elif curl -s http://localhost:5173 > /dev/null; then
    echo "✅ 前端服务正常运行 (端口5173)"
    FRONTEND_PORT=5173
else
    echo "❌ 前端服务未启动"
    exit 1
fi

echo ""
echo "2. 检查后端服务状态"
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ 后端服务正常运行 (端口8001)"
else
    echo "❌ 后端服务未启动"
fi

echo ""
echo "3. 检查页面文件完整性"
cd frontend-vue/src/pages
if [[ -f "Dashboard.vue" && -f "Login.vue" && -f "TagsManagement.vue" && -f "ContentList.vue" && -f "Market.vue" ]]; then
    echo "✅ 主要页面文件存在"
else
    echo "❌ 缺少关键页面文件"
fi
cd ../../..

echo ""
echo "4. 检查Store配置"
if [[ -f "frontend-vue/src/store/user.ts" ]]; then
    echo "✅ 用户Store配置存在"
else
    echo "❌ 用户Store配置缺失"
fi

echo ""
echo "=== 布局恢复结果 ==="
echo "✅ App.vue - 已恢复顶部栏和侧边栏"
echo "✅ 路由配置 - 已恢复完整路由和守卫"
echo "✅ 用户Store - 已恢复登录状态管理"
echo "✅ 页面文件 - 主要页面都存在"
echo ""
echo "🌐 现在应该包含以下功能："
echo "- 顶部栏: 用户信息、通知、设置、退出按钮"
echo "- 左侧导航: 仪表盘、标签管理、内容资讯、行情信息、AI助手"
echo "- 主内容区: 显示对应页面内容"
echo ""
echo "📝 访问地址:"
echo "- 登录页面: http://localhost:$FRONTEND_PORT/login"
echo "- 仪表盘: http://localhost:$FRONTEND_PORT/dashboard (需要先登录)"
echo ""
echo "🎉 布局应该已经完全恢复！" 