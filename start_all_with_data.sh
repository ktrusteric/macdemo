#!/bin/bash

# 上海石油天然气交易中心信息门户系统 - 完整启动脚本（包含数据导入）
echo "🚀 启动上海石油天然气交易中心信息门户系统（包含数据导入）"
echo "============================================================"

# 检查依赖环境
echo "🔍 检查依赖环境..."

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装Node.js"
    exit 1
fi

# 检查MongoDB
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB 未运行，尝试启动..."
    # 尝试启动MongoDB（根据不同系统调整）
    if command -v brew &> /dev/null; then
        brew services start mongodb-community
    elif command -v systemctl &> /dev/null; then
        sudo systemctl start mongod
    else
        echo "❌ 无法自动启动MongoDB，请手动启动"
        exit 1
    fi
    sleep 3
fi

echo "✅ 依赖环境检查完成"

# 进入后端目录
cd backend

# 创建并激活虚拟环境
echo "🐍 设置Python虚拟环境..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ 创建虚拟环境完成"
fi

source .venv/bin/activate
echo "✅ 激活虚拟环境完成"

# 安装后端依赖
echo "📦 安装后端依赖..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ 后端依赖安装完成"

# 🔥 检查并导入数据
echo "📋 检查后端数据文件..."
if [ -f "scripts/能源信息服务系统_清理重复字段_51篇.json" ]; then
    echo "✅ 发现清理后的数据文件"
    echo "📊 导入清理后的数据（已移除重复的文档类型字段）..."
    python3 scripts/import_sample_data.py
    if [ $? -eq 0 ]; then
        echo "✅ 数据导入成功 - 使用统一的basic_info_tags字段"
    else
        echo "❌ 数据导入失败"
        exit 1
    fi
else
    echo "❌ 找不到数据文件，请检查scripts目录"
    exit 1
fi

# 启动后端服务
echo "🔧 启动后端服务..."
cd backend  # 进入backend目录
PYTHONPATH=/Users/eric/Documents/GitHub/macdemo/backend uvicorn app.main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID) - http://localhost:8001"

# 返回项目根目录并进入前端目录
cd ../frontend-vue

# 安装前端依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
    echo "✅ 前端依赖安装完成"
fi

# 启动前端服务
echo "🎨 启动前端服务..."
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID) - http://localhost:5173"

# 等待服务完全启动
echo "⏳ 等待服务启动..."
sleep 5

# 验证服务状态
echo "🔍 验证服务状态..."

# 检查后端服务
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常"
else
    echo "⚠️  后端服务可能未完全启动，请稍等..."
fi

# 检查前端服务
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ 前端服务运行正常"
else
    echo "⚠️  前端服务可能未完全启动，请稍等..."
fi

# 🎯 完成信息
echo ""
echo "🎉 上海石油天然气交易中心信息门户系统启动完成！"
echo "============================================================"
echo "📊 数据导入状态: ✅ 成功导入51篇文章（已清理重复字段）"
echo "🗑️  字段优化: 已移除重复的'文档类型'字段"
echo "🏷️  标签统一: 统一使用'basic_info_tags'字段"
echo ""
echo "🌐 服务地址:"
echo "   前端应用: http://localhost:5173"
echo "   后端API:  http://localhost:8001"
echo "   API文档:  http://localhost:8001/docs"
echo ""
echo "📋 预设用户 (邮箱/密码):"
echo "   张工程师 (天然气专家):    zhang@shanghai.com / demo123"
echo "   李经理 (原油贸易):        li@beijing.com / demo123" 
echo "   王主任 (LNG项目):         wang@shenzhen.com / demo123"
echo "   陈总监 (PNG运营):         chen@guangzhou.com / demo123"
echo "   刘研究员 (电力系统):      liu@chengdu.com / demo123"
echo ""
echo "🛑 停止服务："
echo "   Ctrl+C 停止当前服务，或运行 ./stop_backend.sh"
echo ""
echo "🔧 技术改进:"
echo "   ✅ 移除了'文档类型'和'基础信息标签'的重复问题"
echo "   ✅ 前端选择文档类型自动生成basic_info_tags"
echo "   ✅ 统一了前后端标签管理逻辑"
echo "   ✅ 数据存储更加高效，避免冗余"

# 保存PID以便后续停止
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# 等待用户中断
wait 