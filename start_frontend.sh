#!/bin/bash

echo "=== 启动 OpenResty 负载均衡管理平台前端 ==="

# 进入前端目录
cd frontend-vue

# 检查Node.js环境
echo "检查Node.js环境..."
node --version
npm --version

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 启动前端开发服务器
echo "启动前端开发服务器..."
npm run dev

echo "前端服务已启动" 