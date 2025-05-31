#!/bin/bash

echo "=== OpenResty 负载均衡管理平台后端启动（含数据初始化）==="

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
    exit 1
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        error_exit "Python3 未安装"
    fi
    log_success "Python3: $(python3 --version)"
    
    # 检查MongoDB
    if ! pgrep mongod > /dev/null; then
        log_warning "MongoDB 未运行，尝试启动..."
        if command -v brew &> /dev/null; then
            brew services start mongodb-community || log_warning "MongoDB启动失败，请手动启动"
        else
            log_warning "请手动启动MongoDB服务"
        fi
    else
        log_success "MongoDB 服务正在运行"
    fi
    
    # 检查端口占用
    if lsof -i:8001 > /dev/null 2>&1; then
        log_warning "端口8001已被占用，将尝试停止现有服务"
        pkill -f "uvicorn.*8001" || true
        sleep 2
    fi
}

# 设置Python环境
setup_python_env() {
    log_info "设置Python环境..."
    
    cd backend
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 检查并安装依赖
    if [ ! -f "venv/installed" ]; then
        log_info "安装Python依赖..."
        pip install --upgrade pip
        pip install -r requirements.txt
        touch venv/installed
        log_success "依赖安装完成"
    else
        log_info "Python依赖已存在，跳过安装"
    fi
}

# 数据库初始化
init_database() {
    log_info "初始化数据库..."
    
    # 检查数据库连接
    python3 -c "
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_connection():
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        await client.admin.command('ping')
        print('数据库连接成功')
        client.close()
        return True
    except Exception as e:
        print(f'数据库连接失败: {e}')
        return False

result = asyncio.run(test_connection())
exit(0 if result else 1)
" || error_exit "无法连接到MongoDB数据库"
    
    # 检查是否已有数据
    CONTENT_COUNT=$(python3 -c "
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def check_data():
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client.energy_info
        count = await db.content.count_documents({})
        client.close()
        return count
    except:
        return 0

count = asyncio.run(check_data())
print(count)
")
    
    if [ "$CONTENT_COUNT" -eq 0 ]; then
        log_info "数据库为空，开始导入整合数据..."
        
        # 导入整合的v1+v2数据
        cd scripts
        log_info "使用v3版本导入脚本: integrated_import_v3.py"
        log_info "数据来源: 统一v3版本 (45篇文章，简化维护)"
        
        # 执行数据导入
        python3 integrated_import_v3.py || error_exit "数据导入失败"
        
        log_success "整合数据导入完成"
        cd ..
    else
        log_info "数据库已有 $CONTENT_COUNT 条记录，跳过数据导入"
    fi
}

# 启动后端服务
start_backend() {
    log_info "启动后端服务..."
    
    # 设置环境变量
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    
    # 启动服务
    log_info "后端服务启动在 http://localhost:8001"
    log_info "API文档地址: http://localhost:8001/docs"
    log_info "按 Ctrl+C 停止服务"
    
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
}

# 主函数
main() {
    echo "=========================================="
    log_info "OpenResty 负载均衡管理平台后端启动"
    log_info "包含自动数据初始化功能"
    echo "=========================================="
    
    check_dependencies
    setup_python_env
    init_database
    start_backend
}

# 信号处理
cleanup() {
    echo ""
    log_info "正在停止后端服务..."
    pkill -f "uvicorn.*8001" || true
    log_success "后端服务已停止"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 执行主函数
main 