#!/bin/bash
# Docker 启动失败诊断脚本

echo "=========================================="
echo "Docker 启动失败诊断工具"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用 sudo 运行此脚本${NC}"
    exit 1
fi

echo "正在收集诊断信息..."
echo ""

# 1. 查看服务状态
echo "=========================================="
echo "1. Docker 服务状态"
echo "=========================================="
systemctl status docker.service -l --no-pager
echo ""

# 2. 查看最近的日志
echo "=========================================="
echo "2. Docker 服务日志（最近50行）"
echo "=========================================="
journalctl -u docker.service -n 50 --no-pager
echo ""

# 3. 检查配置文件
echo "=========================================="
echo "3. Docker 配置文件"
echo "=========================================="
if [ -f /etc/docker/daemon.json ]; then
    echo "配置文件存在，内容如下："
    cat /etc/docker/daemon.json
    echo ""

    # 检查 JSON 语法
    echo "检查 JSON 语法..."
    if command -v python3 &> /dev/null; then
        if python3 -m json.tool /etc/docker/daemon.json &> /dev/null; then
            echo -e "${GREEN}✅ JSON 语法正确${NC}"
        else
            echo -e "${RED}❌ JSON 语法错误！${NC}"
            echo "错误详情："
            python3 -m json.tool /etc/docker/daemon.json
        fi
    fi
else
    echo -e "${YELLOW}⚠️  配置文件不存在${NC}"
fi
echo ""

# 4. 检查端口占用
echo "=========================================="
echo "4. Docker 端口占用情况"
echo "=========================================="
netstat -tulnp | grep -E '(2375|2376|2377)' || echo "无端口占用"
echo ""

# 5. 检查磁盘空间
echo "=========================================="
echo "5. 磁盘空间"
echo "=========================================="
df -h | grep -E '(Filesystem|/var|/$)'
echo ""

# 6. 检查 Docker 进程
echo "=========================================="
echo "6. Docker 相关进程"
echo "=========================================="
ps aux | grep docker | grep -v grep || echo "无 Docker 进程运行"
echo ""

# 7. 检查关键文件
echo "=========================================="
echo "7. Docker 关键文件"
echo "=========================================="
ls -l /var/run/docker.sock 2>/dev/null && echo "✅ docker.sock 存在" || echo "❌ docker.sock 不存在"
ls -l /var/run/docker.pid 2>/dev/null && echo "⚠️  docker.pid 存在（可能需要清理）" || echo "✅ docker.pid 不存在"
echo ""

# 8. 检查系统日志中的错误
echo "=========================================="
echo "8. 系统错误日志（与 Docker 相关）"
echo "=========================================="
journalctl -p err -n 20 --no-pager | grep -i docker || echo "无相关错误"
echo ""

# 生成诊断建议
echo "=========================================="
echo "9. 诊断建议"
echo "=========================================="

# 检查配置文件语法
if [ -f /etc/docker/daemon.json ]; then
    if command -v python3 &> /dev/null; then
        if ! python3 -m json.tool /etc/docker/daemon.json &> /dev/null; then
            echo -e "${RED}❌ 问题: daemon.json 配置文件语法错误${NC}"
            echo "建议修复："
            echo "  sudo rm /etc/docker/daemon.json"
            echo "  sudo systemctl start docker"
            echo ""
        fi
    fi
fi

# 检查残留文件
if [ -f /var/run/docker.pid ]; then
    echo -e "${YELLOW}⚠️  发现残留的 docker.pid 文件${NC}"
    echo "建议修复："
    echo "  sudo rm -f /var/run/docker.pid"
    echo "  sudo rm -f /var/run/docker.sock"
    echo "  sudo systemctl start docker"
    echo ""
fi

# 检查磁盘空间
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo -e "${RED}❌ 问题: 磁盘空间不足（已使用 ${DISK_USAGE}%）${NC}"
    echo "建议清理："
    echo "  docker system prune -a --volumes"
    echo ""
fi

echo "=========================================="
echo "诊断完成！"
echo "=========================================="
echo ""
echo "常见修复方案："
echo ""
echo "方案 1: 移除配置文件重试"
echo "  sudo mv /etc/docker/daemon.json /etc/docker/daemon.json.backup"
echo "  sudo systemctl start docker"
echo ""
echo "方案 2: 清理残留文件"
echo "  sudo pkill docker"
echo "  sudo rm -f /var/run/docker.pid /var/run/docker.sock"
echo "  sudo systemctl start docker"
echo ""
echo "方案 3: 完全重置 Docker"
echo "  sudo systemctl stop docker"
echo "  sudo rm -rf /var/lib/docker"
echo "  sudo systemctl start docker"
echo "  (警告：会删除所有容器和镜像！)"
echo ""
