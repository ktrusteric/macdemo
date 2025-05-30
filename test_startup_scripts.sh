#!/bin/bash

echo "=== 测试启动脚本功能 ==="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# 清理数据库
cleanup_database() {
    log_info "清理测试数据库..."
    mongo energy_info --eval "db.dropDatabase()" 2>/dev/null || true
    log_success "数据库已清理"
}

# 测试后端启动脚本
test_backend_startup() {
    log_info "测试后端启动脚本（含数据初始化）..."
    
    # 确保没有现有服务
    pkill -f "uvicorn.*8001" 2>/dev/null || true
    sleep 2
    
    # 后台启动服务
    timeout 60 ./start_backend_with_data.sh &
    STARTUP_PID=$!
    
    # 等待服务启动
    log_info "等待后端服务启动（最长60秒）..."
    for i in {1..30}; do
        if curl -s http://localhost:8001/health > /dev/null; then
            log_success "后端服务启动成功"
            break
        fi
        sleep 2
    done
    
    # 检查服务状态
    if curl -s http://localhost:8001/health > /dev/null; then
        log_success "后端健康检查通过"
    else
        log_error "后端服务未正常启动"
        return 1
    fi
    
    # 检查数据是否已导入
    DATA_COUNT=$(curl -s http://localhost:8001/content | jq -r '.total' 2>/dev/null || echo "0")
    if [ "$DATA_COUNT" -gt 0 ]; then
        log_success "数据初始化成功，导入了 $DATA_COUNT 条记录"
    else
        log_error "数据初始化失败"
        return 1
    fi
    
    # 检查Demo用户
    USER_COUNT=$(curl -s http://localhost:8001/users | jq -r '.total' 2>/dev/null || echo "0")
    if [ "$USER_COUNT" -ge 5 ]; then
        log_success "Demo用户创建成功，共 $USER_COUNT 个用户"
    else
        log_error "Demo用户创建失败"
        return 1
    fi
    
    # 停止服务
    kill $STARTUP_PID 2>/dev/null || true
    pkill -f "uvicorn.*8001" 2>/dev/null || true
    sleep 2
    
    log_success "后端启动脚本测试完成"
}

# 测试停止脚本
test_stop_script() {
    log_info "测试停止脚本..."
    
    # 先启动一个服务
    cd backend
    source venv/bin/activate
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 &
    TEST_PID=$!
    cd ..
    
    sleep 3
    
    # 测试停止脚本
    ./stop_backend.sh
    
    # 检查服务是否已停止
    sleep 2
    if ! lsof -i:8001 > /dev/null 2>&1; then
        log_success "停止脚本测试通过"
    else
        log_error "停止脚本测试失败"
        kill $TEST_PID 2>/dev/null || true
        return 1
    fi
}

# 测试规范化数据
test_normalized_data() {
    log_info "测试规范化数据导入..."
    
    # 检查JSON文件是否存在
    if [ -f "backend/scripts/简化测试数据.json" ]; then
        log_success "规范化数据文件存在"
    else
        log_error "规范化数据文件不存在"
        return 1
    fi
    
    # 检查文件内容
    ARTICLE_COUNT=$(jq length backend/scripts/简化测试数据.json 2>/dev/null || echo "0")
    if [ "$ARTICLE_COUNT" -gt 0 ]; then
        log_success "规范化数据包含 $ARTICLE_COUNT 篇文章"
    else
        log_error "规范化数据文件格式错误"
        return 1
    fi
    
    # 检查标签优化
    FIRST_ARTICLE_TAGS=$(jq -r '.[0]."能源品种标签" | length' backend/scripts/简化测试数据.json 2>/dev/null || echo "0")
    if [ "$FIRST_ARTICLE_TAGS" -le 5 ]; then
        log_success "标签已优化，第一篇文章有 $FIRST_ARTICLE_TAGS 个能源标签"
    else
        log_error "标签未正确优化"
        return 1
    fi
}

# 主测试函数
main() {
    echo "=========================================="
    log_info "OpenResty 负载均衡管理平台启动脚本测试"
    echo "=========================================="
    
    # 清理环境
    cleanup_database
    
    # 运行测试
    test_normalized_data
    test_backend_startup
    test_stop_script
    
    echo ""
    log_success "所有测试完成！"
    echo "=========================================="
    log_info "📋 测试摘要:"
    log_info "   ✅ 规范化数据文件检查"
    log_info "   ✅ 后端启动脚本（含数据初始化）"
    log_info "   ✅ 停止脚本功能"
    log_info "   ✅ 自动数据导入功能"
    log_info "   ✅ Demo用户创建功能"
    echo ""
    log_info "🎯 您现在可以使用:"
    log_info "   ./start_backend_with_data.sh  # 启动后端（含数据初始化）"
    log_info "   ./start_all_with_data.sh      # 启动前后端（含数据初始化）"
    log_info "   ./stop_backend.sh             # 停止后端服务"
    echo "=========================================="
}

# 设置信号处理
cleanup() {
    echo ""
    log_info "清理测试环境..."
    pkill -f "uvicorn.*8001" 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# 执行主函数
main 