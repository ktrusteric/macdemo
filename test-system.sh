#!/bin/bash

# 系统测试脚本

echo "=== 能源信息服务系统测试 ==="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 测试MongoDB连接
echo -n "测试MongoDB连接... "
if python3 -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); client.admin.command('ping')" 2>/dev/null; then
    echo -e "${GREEN}✓ 成功${NC}"
else
    echo -e "${RED}✗ 失败${NC}"
    echo "请确保MongoDB正在运行"
fi

# 测试后端API
echo -n "测试后端API... "
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 成功${NC}"
    echo "  API文档: http://localhost:8000/docs"
else
    echo -e "${RED}✗ 失败${NC}"
    echo "  请确保后端服务正在运行"
fi

# 测试前端服务
echo -n "测试前端服务... "
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 成功${NC}"
    echo "  前端地址: http://localhost:5173"
else
    echo -e "${RED}✗ 失败${NC}"
    echo "  请确保前端服务正在运行"
fi

echo ""
echo "测试完成！" 