#!/bin/bash

# 快速启动脚本 - 使用本地MongoDB

echo "=== 能源信息服务系统快速启动 ==="
echo ""

# 切换到项目目录
cd "$(dirname "$0")"

# 检查MongoDB状态
if systemctl is-active --quiet mongod || pgrep -x "mongod" > /dev/null; then
    echo "✓ MongoDB正在运行"
else
    echo "✗ MongoDB未运行，请先启动MongoDB服务"
    echo "  使用命令: sudo systemctl start mongod"
    exit 1
fi

# 创建后端.env文件
if [ ! -f "backend/.env" ]; then
    echo "创建后端配置文件..."
    cat > backend/.env << 'EOF'
PROJECT_NAME="Energy Info System"
VERSION="1.0.0"
API_V1_STR="/api/v1"
MONGODB_URL="mongodb://localhost:27017"
DATABASE_NAME="energy_info"
AI_BACKEND_URL="https://ai.wiseocean.cn"
AI_API_TIMEOUT=30
SECRET_KEY="your-secret-key-here"
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
EOF
fi

# 创建前端.env文件
if [ ! -f "frontend/.env" ]; then
    echo "创建前端配置文件..."
    cat > frontend/.env << 'EOF'
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_AI_BACKEND_URL=https://ai.wiseocean.cn
EOF
fi

# 检查依赖是否已安装
if [ ! -f "backend/.deps_installed" ]; then
    echo "安装后端依赖..."
    cd backend
    python3 -m pip install -r requirements.txt
    touch .deps_installed
    cd ..
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

# 启动后端
echo ""
echo "启动后端服务..."
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo "等待后端启动..."
sleep 5

# 启动前端
echo "启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "系统已启动!"
echo ""
echo "前端地址: http://localhost:5173"
echo "后端API文档: http://localhost:8000/docs"
echo ""
echo "后端进程ID: $BACKEND_PID"
echo "前端进程ID: $FRONTEND_PID"
echo ""
echo "停止服务请按 Ctrl+C"
echo "========================================"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait 