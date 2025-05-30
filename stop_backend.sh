#!/bin/bash

echo "=== OpenResty 负载均衡管理平台后端停止 ==="

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

# 停止后端服务
stop_backend() {
    log_info "正在停止后端服务..."
    
    # 检查服务是否运行
    if lsof -i:8001 > /dev/null 2>&1; then
        log_info "发现运行在8001端口的服务，正在停止..."
        
        # 尝试优雅停止
        pkill -f "uvicorn.*8001" || true
        sleep 2
        
        # 检查是否还在运行
        if lsof -i:8001 > /dev/null 2>&1; then
            log_warning "服务仍在运行，强制停止..."
            pkill -9 -f "uvicorn.*8001" || true
            sleep 1
        fi
        
        # 最终检查
        if lsof -i:8001 > /dev/null 2>&1; then
            log_error "无法停止8001端口的服务"
            return 1
        else
            log_success "后端服务已停止"
        fi
    else
        log_info "后端服务未运行"
    fi
}

# 清理虚拟环境进程
cleanup_processes() {
    log_info "清理相关进程..."
    
    # 停止Python相关进程
    pkill -f "python.*uvicorn" || true
    pkill -f "python.*app.main" || true
    
    # 清理孤儿进程
    sleep 1
    
    log_success "进程清理完成"
}

# 显示服务状态
show_status() {
    log_info "检查服务状态..."
    
    if lsof -i:8001 > /dev/null 2>&1; then
        log_warning "端口8001仍被占用:"
        lsof -i:8001
    else
        log_success "端口8001已释放"
    fi
    
    # 检查相关进程
    PYTHON_PROCESSES=$(pgrep -f "python.*uvicorn" 2>/dev/null | wc -l)
    if [ "$PYTHON_PROCESSES" -gt 0 ]; then
        log_warning "仍有 $PYTHON_PROCESSES 个Python进程在运行"
        pgrep -f "python.*uvicorn" | xargs ps -p
    else
        log_success "没有相关Python进程运行"
    fi
}

# 主函数
main() {
    echo "=========================================="
    log_info "OpenResty 负载均衡管理平台后端停止"
    echo "=========================================="
    
    stop_backend
    cleanup_processes
    show_status
    
    echo ""
    log_success "后端停止操作完成"
}

# 执行主函数
main 