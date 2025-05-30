#!/bin/bash

echo "🔧 修复pip网络连接问题..."

# 1. 清除可能存在的代理设置
echo "清除代理环境变量..."
unset HTTP_PROXY
unset HTTPS_PROXY
unset http_proxy
unset https_proxy
unset ALL_PROXY
unset all_proxy

# 2. 清除pip缓存
echo "清除pip缓存..."
python3 -m pip cache purge 2>/dev/null || true

# 3. 配置pip使用国内镜像源（提高连接成功率）
echo "配置pip镜像源..."
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 60
retries = 3
EOF

# 4. 测试pip连接
echo "测试pip连接..."
python3 -m pip --version

# 5. 重新安装依赖（使用国内源）
if [ -f "requirements.txt" ]; then
    echo "重新安装Python依赖..."
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt --force-reinstall
    echo "✅ 依赖安装完成"
else
    echo "⚠️ 未找到requirements.txt文件"
fi

echo "🎉 pip网络问题修复完成！" 