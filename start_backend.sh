#!/bin/bash

echo "=== 启动 OpenResty 负载均衡管理平台后端 ==="

# 检查Python环境
echo "检查Python环境..."
python3 --version

# 进入后端目录
cd backend

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖（如果需要）
echo "检查Python依赖..."
pip list | grep fastapi > /dev/null
if [ $? -ne 0 ]; then
    echo "安装Python依赖..."
    pip install -r requirements.txt
fi

# 启动后端服务
echo "启动后端服务..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

echo "后端服务已启动在 http://localhost:8001" 