#!/bin/bash

echo "=== OpenResty 负载均衡管理平台 - 完整启动（含数据初始化）==="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 错误处理
set -e
error_exit() {
    log_error "启动失败: $1"
    cleanup_on_error
    exit 1
}

# 清理相关进程（保留MongoDB）
cleanup_processes() {
    log_info "清理现有相关进程..."
    
    # 停止uvicorn后端进程
    log_info "查找并停止uvicorn进程..."
    UVICORN_PIDS=$(pgrep -f "uvicorn.*main:app" 2>/dev/null || true)
    if [ ! -z "$UVICORN_PIDS" ]; then
        echo "$UVICORN_PIDS" | xargs kill -9 2>/dev/null || true
        log_success "已停止uvicorn进程: $UVICORN_PIDS"
    else
        log_info "未发现uvicorn进程"
    fi
    
    # 停止npm/node前端进程（排除MongoDB相关）
    log_info "查找并停止前端进程..."
    NODE_PIDS=$(pgrep -f "node.*vite" 2>/dev/null || true)
    if [ ! -z "$NODE_PIDS" ]; then
        echo "$NODE_PIDS" | xargs kill -9 2>/dev/null || true
        log_success "已停止前端Node进程: $NODE_PIDS"
    else
        log_info "未发现前端Node进程"
    fi
    
    # 停止特定端口的进程
    log_info "检查并清理端口占用..."
    for port in 8001 5173; do
        PID=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$PID" ]; then
            # 确保不是MongoDB进程（通常在27017端口）
            PROCESS_NAME=$(ps -p $PID -o comm= 2>/dev/null || true)
            if [[ "$PROCESS_NAME" != *"mongod"* ]]; then
                kill -9 $PID 2>/dev/null || true
                log_success "已停止端口 $port 上的进程: $PID ($PROCESS_NAME)"
            else
                log_info "跳过MongoDB进程: $PID"
            fi
        fi
    done
    
    # 等待进程完全结束
    sleep 2
    log_success "进程清理完成"
}

# 检查环境
check_environment() {
    log_info "检查运行环境..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        error_exit "Python3 未安装"
    fi
    log_success "Python3: $(python3 --version)"
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        error_exit "Node.js 未安装"
    fi
    log_success "Node.js: $(node --version)"
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        error_exit "npm 未安装"
    fi
    log_success "npm: $(npm --version)"
    
    # 检查MongoDB
    if ! pgrep mongod > /dev/null; then
        log_warning "MongoDB 未运行，尝试启动..."
        if command -v brew &> /dev/null; then
            brew services start mongodb-community 2>/dev/null || true
            sleep 3
        fi
        
        if ! pgrep mongod > /dev/null; then
            error_exit "MongoDB 启动失败，请手动启动MongoDB服务"
        fi
    fi
    log_success "MongoDB 服务正在运行"
}

# 清除并重新导入数据
reset_and_import_data() {
    log_info "清除历史数据并重新导入..."
    
    cd backend
    
    # 激活虚拟环境
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    source venv/bin/activate
    
    # 安装依赖
    log_info "安装Python依赖..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    # 清除数据库
    log_info "清除数据库..."
    python3 -c "
import pymongo
import sys

try:
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['energy_info_db']
    
    # 清除所有集合
    collections = db.list_collection_names()
    for collection in collections:
        db[collection].drop()
        print(f'已清除集合: {collection}')
    
    print('数据库清除完成')
    client.close()
except Exception as e:
    print(f'清除数据库失败: {e}')
    sys.exit(1)
"
    
    # 重新导入数据
    log_info "重新导入v3版本数据..."
    log_info "数据来源: 统一v3版本 (45篇文章，简化维护)"
    cd scripts
    python3 integrated_import_v3.py
    
    if [ $? -eq 0 ]; then
        log_success "整合数据导入完成"
    else
        error_exit "数据导入失败"
    fi
    
    cd ../..
}

# 检查端口占用（简化版，主要清理工作在cleanup_processes中完成）
check_ports() {
    log_info "检查端口状态..."
    
    # 显示当前端口占用情况
    for port in 8001 5173; do
        if lsof -i:$port > /dev/null 2>&1; then
            log_info "端口 $port 目前无占用"
        else
            log_info "端口 $port 可用"
        fi
    done
    
    log_success "端口检查完成"
}

# 启动后端服务
start_backend() {
    log_info "启动后端服务..."
    
    cd backend
    
    # 激活虚拟环境（已在reset_and_import_data中创建）
    source venv/bin/activate
    
    # 后台启动后端服务
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # 等待后端启动
    log_info "等待后端服务启动..."
    sleep 5
    
    # 检查后端是否启动成功
    if curl -s http://localhost:8001/health > /dev/null; then
        log_success "后端服务启动成功 (PID: $BACKEND_PID)"
        log_info "后端地址: http://localhost:8001"
        log_info "API文档: http://localhost:8001/docs"
    else
        error_exit "后端服务启动失败"
    fi
}

# 启动前端服务
start_frontend() {
    log_info "启动前端服务..."
    
    cd frontend-vue
    
    # 安装依赖
    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖..."
        npm install
        log_success "前端依赖安装完成"
    fi
    
    # 后台启动前端开发服务器
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # 等待前端启动
    log_info "等待前端服务启动..."
    sleep 8
    
    # 检查前端是否启动成功
    if curl -s http://localhost:5173 > /dev/null; then
        log_success "前端服务启动成功 (PID: $FRONTEND_PID)"
        log_info "前端地址: http://localhost:5173"
    else
        log_warning "前端服务可能还在启动中，请稍后访问 http://localhost:5173"
    fi
}

# 清理函数
cleanup() {
    log_info "正在停止服务..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "vite.*dev" 2>/dev/null || true
    log_success "服务已停止"
    exit 0
}

cleanup_on_error() {
    log_error "发生错误，清理环境..."
    cleanup
}

# 显示启动信息
show_startup_info() {
    echo ""
    echo "=========================================="
    log_success "🎉 OpenResty负载均衡管理平台启动完成!"
    echo "=========================================="
    log_info "🌐 前端地址: http://localhost:5173"
    log_info "🔧 后端API: http://localhost:8001"  
    log_info "📚 API文档: http://localhost:8001/docs"
    log_info "🗃️  数据库: MongoDB (localhost:27017)"
    echo ""
    log_info "📋 系统功能:"
    log_info "   • 用户注册登录（含Demo用户）"
    log_info "   • 智能推荐引擎（地域+能源标签）"
    log_info "   • 标签管理系统（城市→省份→地区自动识别）"
    log_info "   • 内容浏览与搜索"
    echo ""
    log_info "🎭 Demo用户（已优化为单能源标签）:"
    log_info "   • 张先生@上海 - 天然气专家"
    log_info "   • 李女士@北京 - 原油分析师" 
    log_info "   • 王先生@深圳 - LNG项目经理"
    log_info "   • 陈女士@广州 - PNG运营专家"
    log_info "   • 刘先生@成都 - 电力工程师"
    echo ""
    log_info "📊 测试数据:"
    log_info "   • 45篇标准化测试文章"
    log_info "   • 优化的标签分布（3-5个标签/文章）"
    log_info "   • 68个城市地区映射支持"
    echo ""
    log_warning "按 Ctrl+C 停止所有服务"
    echo "=========================================="
}

# 主函数
main() {
    echo "=========================================="
    log_info "OpenResty 负载均衡管理平台完整启动"
    log_info "包含前后端服务和数据重置初始化"
    echo "=========================================="
    
    # 1. 清理现有进程
    cleanup_processes
    
    # 2. 检查运行环境
    check_environment
    
    # 3. 检查端口状态
    check_ports
    
    # 4. 清除并重新导入数据
    reset_and_import_data
    
    # 5. 启动后端服务
    start_backend
    
    # 6. 启动前端服务  
    start_frontend
    
    # 7. 显示启动信息
    show_startup_info
    
    # 8. 保持运行状态
    log_info "服务运行中，按 Ctrl+C 停止..."
    while true; do
        sleep 1
    done
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 执行主函数
main 