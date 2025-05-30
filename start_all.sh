#!/bin/bash

echo "=== OpenResty 负载均衡管理平台 - 完整启动 ==="

# 检查环境
echo "检查运行环境..."
python3 --version
node --version
npm --version

# 检查端口占用情况
echo "检查端口占用情况..."
lsof -i:8001 && echo "警告：8001端口已被占用" || echo "8001端口可用"
lsof -i:5173 && echo "警告：5173端口已被占用" || echo "5173端口可用"

echo ""
echo "启动服务..."

# 启动后端服务（后台运行）
echo "启动后端服务（端口8001）..."
cd backend

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并启动
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 5

# 检查后端是否启动成功
curl -s http://localhost:8001/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ 后端服务启动成功"
else
    echo "❌ 后端服务启动失败"
fi

# 启动前端服务（前台运行）
echo "启动前端服务（端口5173）..."
cd frontend-vue

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

npm run dev

# 清理函数
cleanup() {
    echo ""
    echo "正在停止服务..."
    kill $BACKEND_PID 2>/dev/null
    echo "服务已停止"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

wait 