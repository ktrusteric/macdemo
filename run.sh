#!/bin/bash

# 能源信息服务系统启动脚本

echo "=== 能源信息服务系统启动脚本 ==="
echo ""

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3 未安装"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "错误: npm 未安装"
    exit 1
fi

# 选择操作
echo "请选择要执行的操作:"
echo "1) 安装依赖"
echo "2) 启动后端服务"
echo "3) 启动前端服务"
echo "4) 导入示例数据"
echo "5) 安装并启动所有服务"
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo "=== 安装后端依赖 ==="
        cd backend
        python3 -m pip install -r requirements.txt
        cd ..
        
        echo ""
        echo "=== 安装前端依赖 ==="
        cd frontend
        npm install
        cd ..
        ;;
        
    2)
        echo "=== 启动后端服务 ==="
        cd backend
        python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        ;;
        
    3)
        echo "=== 启动前端服务 ==="
        cd frontend
        npm run dev
        ;;
        
    4)
        echo "=== 导入示例数据 ==="
        cd backend/scripts
        python3 import_sample_data.py
        ;;
        
    5)
        echo "=== 安装所有依赖 ==="
        cd backend
        python3 -m pip install -r requirements.txt
        cd ../frontend
        npm install
        cd ..
        
        echo ""
        echo "=== 依赖安装完成 ==="
        echo "请在不同的终端窗口中运行以下命令:"
        echo ""
        echo "终端1 - 启动后端:"
        echo "  cd backend && python3 -m uvicorn app.main:app --reload"
        echo ""
        echo "终端2 - 启动前端:"
        echo "  cd frontend && npm run dev"
        echo ""
        echo "可选 - 导入数据:"
        echo "  cd backend/scripts && python3 import_sample_data.py"
        ;;
        
    *)
        echo "无效选项"
        exit 1
        ;;
esac 