#!/bin/bash

# 能源信息服务系统 - 完整启动脚本
# 支持MongoDB检查、依赖安装、服务启动

set -e  # 遇到错误立即退出

# ==================== 服务端口配置清单 ====================
# 
# 🔧 核心服务端口分配：
# ├── MongoDB数据库      : 27017 (默认)
# ├── Python后端API     : 8001  (FastAPI + uvicorn)
# ├── React前端开发服务  : 5173  (Vite默认端口)
# └── React前端生产服务  : 3000  (备用端口)
#
# 🌐 AI助手服务 (外部):
# ├── 客服助手: https://ai.wiseocean.cn/bot/#/9714d9bc-31ca-40b5-a720-4329f5fc4af7
# ├── 资讯助手: https://ai.wiseocean.cn/bot/#/158ab70e-2996-4cce-9822-6f8195a7cfa5  
# └── 交易助手: https://ai.wiseocean.cn/bot/#/1e72acc1-43a8-4cda-8d54-f409c9c5d5ed
#
# 📊 服务状态检查端点：
# ├── 后端健康检查: http://localhost:8001/
# ├── 后端API文档 : http://localhost:8001/docs
# ├── 前端应用    : http://localhost:5173
# └── MongoDB连接 : mongodb://localhost:27017/energy_info
#
# =======================================================

# 端口配置
MONGODB_PORT=27017
BACKEND_PORT=8001
FRONTEND_PORT=5173
FRONTEND_ALT_PORT=3000

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_success() {
    echo -e "${CYAN}[SUCCESS]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查端口是否被占用
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        local pid=$(lsof -Pi :$port -sTCP:LISTEN -t)
        local process=$(ps -p $pid -o comm= 2>/dev/null || echo "unknown")
        print_warning "$service_name端口 $port 被占用 (PID: $pid, 进程: $process)"
        return 1
    else
        print_info "$service_name端口 $port 可用"
        return 0
    fi
}

# 检查服务健康状态
check_service_health() {
    local url=$1
    local service_name=$2
    local timeout=${3:-5}
    
    if curl -s --max-time $timeout "$url" >/dev/null 2>&1; then
        print_success "$service_name 健康检查通过"
        return 0
    else
        print_warning "$service_name 健康检查失败"
        return 1
    fi
}

# 检查MongoDB
check_mongodb() {
    print_header "检查MongoDB状态"
    
    # 检查MongoDB进程是否在运行
    if pgrep -x "mongod" > /dev/null; then
        print_info "MongoDB进程已在运行"
        # 尝试连接测试
        if command_exists mongosh; then
            if timeout 3 mongosh --eval "db.runCommand('ping')" >/dev/null 2>&1; then
                print_success "MongoDB运行正常，连接测试通过"
                return 0
            fi
        elif command_exists mongo; then
            if timeout 3 mongo --eval "db.runCommand('ping')" >/dev/null 2>&1; then
                print_success "MongoDB运行正常，连接测试通过"
                return 0
            fi
        fi
        print_success "MongoDB进程运行中"
        return 0
    fi
    
    # 检查端口占用
    if lsof -Pi :$MONGODB_PORT -sTCP:LISTEN >/dev/null 2>&1; then
        local pid=$(lsof -Pi :$MONGODB_PORT -sTCP:LISTEN -t)
        local process=$(ps -p $pid -o comm= 2>/dev/null || echo "unknown")
        print_warning "MongoDB端口 $MONGODB_PORT 被占用 (PID: $pid, 进程: $process)"
        # 如果是MongoDB进程占用，认为是正常的
        if [[ "$process" == *"mongod"* ]]; then
            print_info "确认是MongoDB进程占用端口"
            return 0
        else
            print_error "端口被非MongoDB进程占用"
            return 1
        fi
    fi
    
    # 检查MongoDB服务状态
    if systemctl is-active --quiet mongod 2>/dev/null; then
        print_info "MongoDB服务状态显示为运行中，但进程未找到"
        return 1
    fi
    
    print_warning "MongoDB未运行"
    return 1
}

# 安装Python依赖
install_python_deps() {
    print_header "安装Python依赖"
    cd backend
    
    if [ ! -f ".env" ]; then
        print_info "创建.env文件..."
        cat > .env << EOF
PROJECT_NAME="Energy Info System"
VERSION="1.0.0"
API_V1_STR="/api/v1"
MONGODB_URL="mongodb://localhost:$MONGODB_PORT"
DATABASE_NAME="energy_info"
AI_BACKEND_URL="https://ai.wiseocean.cn"
AI_API_TIMEOUT=30
SECRET_KEY="your-secret-key-here"
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:$FRONTEND_PORT","http://localhost:$FRONTEND_ALT_PORT"]
EOF
    fi
    
    python3 -m pip install -r requirements.txt
    cd ..
    print_success "Python依赖安装完成"
}

# 安装前端依赖
install_frontend_deps() {
    print_header "安装前端依赖"
    cd frontend
    
    if [ ! -f ".env" ]; then
        print_info "创建前端.env文件..."
        cat > .env << EOF
VITE_API_BASE_URL=http://localhost:$BACKEND_PORT/api/v1
VITE_AI_BACKEND_URL=https://ai.wiseocean.cn
EOF
    fi
    
    npm install
    cd ..
    print_success "前端依赖安装完成"
}

# 导入示例数据
import_sample_data() {
    print_header "导入示例数据"
    cd backend/scripts
    
    if [ -f "import_sample_data.py" ]; then
        python3 import_sample_data.py
        print_success "示例数据导入完成"
    else
        print_warning "未找到数据导入脚本"
    fi
    cd ../..
}

# 启动后端服务
start_backend() {
    print_header "启动后端服务"
    
    # 检查端口
    if ! check_port $BACKEND_PORT "后端API"; then
        print_error "后端端口 $BACKEND_PORT 被占用，请先停止相关服务"
        return 1
    fi
    
    cd backend
    nohup python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > ../backend.log 2>&1 &
    echo $! > ../backend.pid
    cd ..
    
    # 等待服务启动
    sleep 3
    
    # 健康检查
    if check_service_health "http://localhost:$BACKEND_PORT/" "后端API"; then
        print_success "后端服务已启动 (PID: $(cat backend.pid))"
        print_info "后端地址: http://localhost:$BACKEND_PORT"
        print_info "API文档: http://localhost:$BACKEND_PORT/docs"
        print_info "后端日志: tail -f backend.log"
    else
        print_error "后端服务启动失败，请检查日志: tail -f backend.log"
        return 1
    fi
}

# 启动前端服务
start_frontend() {
    print_header "启动前端服务"
    
    # 检查端口
    if ! check_port $FRONTEND_PORT "前端应用"; then
        print_error "前端端口 $FRONTEND_PORT 被占用，请先停止相关服务"
        return 1
    fi
    
    cd frontend
    nohup npm run dev > ../frontend.log 2>&1 &
    echo $! > ../frontend.pid
    cd ..
    
    # 等待服务启动
    sleep 5
    
    # 健康检查
    if check_service_health "http://localhost:$FRONTEND_PORT/" "前端应用" 10; then
        print_success "前端服务已启动 (PID: $(cat frontend.pid))"
        print_info "前端地址: http://localhost:$FRONTEND_PORT"
        print_info "前端日志: tail -f frontend.log"
    else
        print_warning "前端服务可能仍在启动中，请稍后访问: http://localhost:$FRONTEND_PORT"
        print_info "前端日志: tail -f frontend.log"
    fi
}

# 停止应用服务（不停止MongoDB）
stop_app_services() {
    print_header "停止应用服务"
    
    # 停止后端
    if [ -f backend.pid ]; then
        local backend_pid=$(cat backend.pid)
        if kill -0 $backend_pid 2>/dev/null; then
            kill $backend_pid 2>/dev/null || true
            print_info "后端服务已停止 (PID: $backend_pid)"
        fi
        rm backend.pid
    fi
    
    # 停止前端
    if [ -f frontend.pid ]; then
        local frontend_pid=$(cat frontend.pid)
        if kill -0 $frontend_pid 2>/dev/null; then
            kill $frontend_pid 2>/dev/null || true
            print_info "前端服务已停止 (PID: $frontend_pid)"
        fi
        rm frontend.pid
    fi
    
    # 强力清理可能残留的应用进程
    print_info "清理残留的应用进程..."
    
    # 清理后端进程
    pkill -f "uvicorn.*app.main:app.*$BACKEND_PORT" 2>/dev/null || true
    pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
    
    # 清理前端进程
    pkill -f "vite.*dev" 2>/dev/null || true
    pkill -f "npm.*run.*dev" 2>/dev/null || true
    
    # 检查并强制终止占用应用端口的进程
    for port in $BACKEND_PORT $FRONTEND_PORT; do
        local pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$pids" ]; then
            print_warning "强制终止占用端口 $port 的进程: $pids"
            echo $pids | xargs kill -9 2>/dev/null || true
        fi
    done
    
    # 等待进程完全退出
    sleep 2
    
    print_success "应用服务已停止"
}

# 启动MongoDB服务
start_mongodb() {
    print_header "启动MongoDB服务"
    
    # 检查MongoDB是否已在运行
    if pgrep -x "mongod" > /dev/null; then
        print_info "MongoDB进程已在运行"
        return 0
    fi
    
    # 检查端口占用
    if lsof -Pi :$MONGODB_PORT -sTCP:LISTEN >/dev/null 2>&1; then
        print_warning "MongoDB端口 $MONGODB_PORT 被占用"
        return 1
    fi
    
    # 尝试启动MongoDB服务
    print_info "启动MongoDB服务..."
    if command_exists systemctl; then
        if sudo systemctl start mongod 2>/dev/null; then
            sleep 3
            print_success "MongoDB服务已启动"
            return 0
        fi
    fi
    
    # 尝试使用service命令
    if command_exists service; then
        if sudo service mongod start 2>/dev/null; then
            sleep 3
            print_success "MongoDB服务已启动"
            return 0
        fi
    fi
    
    print_error "无法启动MongoDB服务"
    return 1
}

# 停止所有服务
stop_all() {
    print_header "停止所有服务"
    
    # 先停止应用服务
    stop_app_services
    
    # 停止MongoDB服务
    print_info "停止MongoDB服务..."
    if command_exists systemctl; then
        if sudo systemctl is-active --quiet mongod 2>/dev/null; then
            sudo systemctl stop mongod 2>/dev/null && print_info "MongoDB服务已停止" || print_warning "MongoDB服务停止失败"
        else
            print_info "MongoDB服务未运行"
        fi
    elif command_exists service; then
        sudo service mongod stop 2>/dev/null && print_info "MongoDB服务已停止" || print_warning "MongoDB服务停止失败"
    else
        print_warning "无法停止MongoDB服务，请手动停止"
    fi
    
    print_success "所有服务已停止"
    
    # 最终检查
    echo ""
    print_info "最终状态检查："
    for port in $MONGODB_PORT $BACKEND_PORT $FRONTEND_PORT; do
        if lsof -Pi :$port -sTCP:LISTEN >/dev/null 2>&1; then
            print_warning "端口 $port 仍被占用"
        else
            print_success "端口 $port 已释放"
        fi
    done
}

# 详细的服务状态检查
check_service_status() {
    print_header "服务状态检查"
    
    echo ""
    print_info "🔍 端口占用情况："
    echo "MongoDB ($MONGODB_PORT):"
    if lsof -Pi :$MONGODB_PORT -sTCP:LISTEN >/dev/null 2>&1; then
        lsof -Pi :$MONGODB_PORT -sTCP:LISTEN | head -2
    else
        echo "  端口未被占用"
    fi
    
    echo ""
    echo "后端API ($BACKEND_PORT):"
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN >/dev/null 2>&1; then
        lsof -Pi :$BACKEND_PORT -sTCP:LISTEN | head -2
    else
        echo "  端口未被占用"
    fi
    
    echo ""
    echo "前端应用 ($FRONTEND_PORT):"
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN >/dev/null 2>&1; then
        lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN | head -2
    else
        echo "  端口未被占用"
    fi
    
    echo ""
    print_info "📊 服务运行状态："
    
    # MongoDB状态
    if pgrep -x "mongod" > /dev/null; then
        print_success "MongoDB: ✅ 运行中"
        # 尝试连接测试
        if command_exists mongo; then
            if timeout 3 mongo --eval "db.runCommand('ping')" >/dev/null 2>&1; then
                print_info "  └─ 数据库连接正常"
            else
                print_warning "  └─ 数据库连接异常"
            fi
        fi
    else
        print_error "MongoDB: ❌ 未运行"
    fi
    
    # 后端状态
    if [ -f backend.pid ] && kill -0 $(cat backend.pid) 2>/dev/null; then
        print_success "后端API: ✅ 运行中 (PID: $(cat backend.pid))"
        # 健康检查
        if check_service_health "http://localhost:$BACKEND_PORT/" "后端API" 3; then
            print_info "  └─ 健康检查通过"
            print_info "  └─ API文档: http://localhost:$BACKEND_PORT/docs"
        else
            print_warning "  └─ 健康检查失败"
        fi
    else
        print_error "后端API: ❌ 未运行"
    fi
    
    # 前端状态
    if [ -f frontend.pid ] && kill -0 $(cat frontend.pid) 2>/dev/null; then
        print_success "前端应用: ✅ 运行中 (PID: $(cat frontend.pid))"
        # 健康检查
        if check_service_health "http://localhost:$FRONTEND_PORT/" "前端应用" 3; then
            print_info "  └─ 应用访问正常"
            print_info "  └─ 前端地址: http://localhost:$FRONTEND_PORT"
        else
            print_warning "  └─ 应用可能仍在启动中"
        fi
    else
        print_error "前端应用: ❌ 未运行"
    fi
    
    echo ""
    print_info "🔗 快速访问链接："
    echo "  • 前端应用: http://localhost:$FRONTEND_PORT"
    echo "  • 后端API: http://localhost:$BACKEND_PORT"
    echo "  • API文档: http://localhost:$BACKEND_PORT/docs"
    echo "  • MongoDB: mongodb://localhost:$MONGODB_PORT/energy_info"
    
    echo ""
    print_info "📋 日志文件："
    echo "  • 后端日志: tail -f backend.log"
    echo "  • 前端日志: tail -f frontend.log"
}

# 主菜单
main_menu() {
    echo ""
    print_header "能源信息服务系统启动脚本"
    echo ""
    echo "1) 🚀 快速启动 (检查MongoDB并启动所有服务)"
    echo "2) 📦 安装依赖"
    echo "3) 🔧 仅启动后端"
    echo "4) 🎨 仅启动前端"
    echo "5) 📊 导入示例数据"
    echo "6) 🛑 停止应用服务 (保持MongoDB运行)"
    echo "7) 🛑 停止所有服务 (包括MongoDB)"
    echo "8) 📋 查看服务状态"
    echo "9) 🔍 查看端口占用"
    echo "10) 📝 查看日志"
    echo "0) 🚪 退出"
    echo ""
    read -p "请选择操作 (0-10): " choice
    
    case $choice in
        1)
            print_header "快速启动所有服务"
            
            # 1. 确保MongoDB运行
            if ! check_mongodb; then
                print_info "MongoDB未运行，尝试启动..."
                if ! start_mongodb; then
                    print_error "MongoDB启动失败，无法继续"
                    exit 1
                fi
            fi
            
            # 2. 安装依赖（如果需要）
            if [ ! -d "backend/venv" ] && [ ! -f "backend/.deps_installed" ]; then
                install_python_deps
                touch backend/.deps_installed
            fi
            
            if [ ! -d "frontend/node_modules" ]; then
                install_frontend_deps
            fi
            
            # 3. 停止现有的应用服务（保持MongoDB运行）
            stop_app_services
            
            # 4. 启动应用服务
            if start_backend && start_frontend; then
                echo ""
                print_success "🎉 所有服务已启动!"
                echo ""
                print_info "🔗 访问地址："
                echo "  • 前端应用: http://localhost:$FRONTEND_PORT"
                echo "  • 后端API文档: http://localhost:$BACKEND_PORT/docs"
                echo ""
                print_info "📊 服务启动顺序："
                echo "  ✅ 1. MongoDB数据库 (端口: $MONGODB_PORT)"
                echo "  ✅ 2. Python后端API (端口: $BACKEND_PORT)"
                echo "  ✅ 3. React前端应用 (端口: $FRONTEND_PORT)"
            else
                print_error "应用服务启动失败"
            fi
            ;;
            
        2)
            install_python_deps
            install_frontend_deps
            ;;
            
        3)
            check_mongodb || exit 1
            start_backend
            ;;
            
        4)
            start_frontend
            ;;
            
        5)
            check_mongodb || exit 1
            import_sample_data
            ;;
            
        6)
            stop_app_services
            ;;
            
        7)
            stop_all
            ;;
            
        8)
            check_service_status
            ;;
            
        9)
            print_header "端口占用情况"
            echo ""
            print_info "检查核心端口："
            for port in $MONGODB_PORT $BACKEND_PORT $FRONTEND_PORT; do
                echo -n "端口 $port: "
                if lsof -Pi :$port -sTCP:LISTEN >/dev/null 2>&1; then
                    echo "被占用"
                    lsof -Pi :$port -sTCP:LISTEN
                else
                    echo "可用"
                fi
                echo ""
            done
            ;;
            
        10)
            print_header "查看日志"
            echo ""
            echo "1) 后端日志 (实时)"
            echo "2) 前端日志 (实时)"
            echo "3) 后端日志 (最近50行)"
            echo "4) 前端日志 (最近50行)"
            echo ""
            read -p "选择日志类型 (1-4): " log_choice
            
            case $log_choice in
                1) tail -f backend.log 2>/dev/null || echo "后端日志文件不存在" ;;
                2) tail -f frontend.log 2>/dev/null || echo "前端日志文件不存在" ;;
                3) tail -n 50 backend.log 2>/dev/null || echo "后端日志文件不存在" ;;
                4) tail -n 50 frontend.log 2>/dev/null || echo "前端日志文件不存在" ;;
                *) print_error "无效选项" ;;
            esac
            ;;
            
        0)
            print_info "再见!"
            exit 0
            ;;
            
        *)
            print_error "无效选项"
            ;;
    esac
}

# 主程序
cd "$(dirname "$0")"

# 显示端口配置信息
print_header "服务端口配置"
echo ""
echo "🔧 核心服务端口："
echo "  • MongoDB数据库: $MONGODB_PORT"
echo "  • Python后端API: $BACKEND_PORT (修改为8001避免冲突)"  
echo "  • React前端应用: $FRONTEND_PORT"
echo ""
echo "🌐 外部AI助手服务："
echo "  • 客服助手: https://ai.wiseocean.cn (ID: 9714d9bc)"
echo "  • 资讯助手: https://ai.wiseocean.cn (ID: 158ab70e)"
echo "  • 交易助手: https://ai.wiseocean.cn (ID: 1e72acc1)"
echo ""

# 检查必要的命令
if ! command_exists python3; then
    print_error "Python3未安装"
    exit 1
fi

if ! command_exists npm; then
    print_error "npm未安装"
    exit 1
fi

# 显示菜单
while true; do
    main_menu
    echo ""
    read -p "按回车键继续..." dummy
done 