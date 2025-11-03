#!/bin/bash
# Docker 服务修复脚本

echo "==================================="
echo "Docker 服务诊断和修复工具"
echo "==================================="
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    echo "用法: sudo bash fix-docker.sh"
    exit 1
fi

# 1. 检查 Docker 是否安装
echo "步骤 1: 检查 Docker 安装..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装！"
    echo "请先安装 Docker: https://docs.docker.com/engine/install/"
    exit 1
fi
echo "✅ Docker 已安装: $(docker --version)"
echo ""

# 2. 检查 Docker 服务状态
echo "步骤 2: 检查 Docker 服务状态..."
if systemctl is-active --quiet docker; then
    echo "✅ Docker 服务正在运行"
else
    echo "❌ Docker 服务未运行，尝试启动..."

    # 清理可能的问题
    rm -f /var/run/docker.pid 2>/dev/null

    # 启动 Docker
    systemctl start docker
    sleep 2

    # 再次检查
    if systemctl is-active --quiet docker; then
        echo "✅ Docker 服务启动成功！"
    else
        echo "❌ Docker 服务启动失败，查看日志："
        journalctl -u docker.service -n 20
        exit 1
    fi
fi
echo ""

# 3. 设置开机自启
echo "步骤 3: 设置开机自启动..."
systemctl enable docker
echo "✅ 已设置 Docker 开机自启动"
echo ""

# 4. 测试 Docker 功能
echo "步骤 4: 测试 Docker 功能..."
if docker ps &> /dev/null; then
    echo "✅ Docker 运行正常"
else
    echo "❌ Docker 运行异常"
    docker ps
    exit 1
fi
echo ""

# 5. 配置用户权限（可选）
echo "步骤 5: 配置用户权限..."
read -p "是否将当前用户添加到 docker 组？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CURRENT_USER=${SUDO_USER:-$USER}
    usermod -aG docker $CURRENT_USER
    echo "✅ 用户 $CURRENT_USER 已添加到 docker 组"
    echo "⚠️  请注销并重新登录以使权限生效"
fi
echo ""

# 6. 显示 Docker 信息
echo "步骤 6: Docker 信息..."
echo "----------------------------------------"
docker info | head -20
echo "----------------------------------------"
echo ""

# 完成
echo "==================================="
echo "✅ Docker 服务修复完成！"
echo "==================================="
echo ""
echo "后续步骤："
echo "1. 如果修改了用户组，请注销并重新登录"
echo "2. 运行: docker ps 测试"
echo "3. 继续部署: docker-compose -f docker-compose.fastapi.yml up -d"
echo ""
