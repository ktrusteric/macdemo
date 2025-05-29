#!/bin/bash

# 同步开发代码到demo环境

echo "=== 同步代码到Demo环境 ==="
echo ""

# 源目录和目标目录
SRC_DIR="/root/energy-trading-system"
DEST_DIR="/home/demo/energy-trading-system"

# 需要排除的文件和目录
EXCLUDES=(
    "--exclude=node_modules"
    "--exclude=.git"
    "--exclude=*.pyc"
    "--exclude=__pycache__"
    "--exclude=.env"
    "--exclude=backend.log"
    "--exclude=frontend.log"
    "--exclude=*.pid"
    "--exclude=backend/.deps_installed"
    "--exclude=frontend/.port_configured"
    "--exclude=vite.config.ts"  # 保留demo环境的端口配置
)

# 执行同步
echo "正在同步文件..."
sudo rsync -av --delete "${EXCLUDES[@]}" "$SRC_DIR/" "$DEST_DIR/"

# 修复权限
echo "修复文件权限..."
sudo chown -R demo:demo "$DEST_DIR"

# 保持脚本可执行
sudo chmod +x "$DEST_DIR"/*.sh
sudo chmod +x "$DEST_DIR"/backend/scripts/*.py 2>/dev/null || true

echo ""
echo "✅ 同步完成！"
echo ""
echo "提示："
echo "1. 代码已同步到: $DEST_DIR"
echo "2. 环境配置文件(.env)未同步，保持各自独立"
echo "3. 运行服务: /root/run-as-demo.sh" 