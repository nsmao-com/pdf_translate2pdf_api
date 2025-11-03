#!/bin/bash
# Docker 镜像源配置脚本

echo "配置 Docker 国内镜像源..."

# 备份原配置
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.backup 2>/dev/null || true

# 创建或更新配置
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.ccs.tencentyun.com",
    "https://registry.docker-cn.com"
  ],
  "dns": ["8.8.8.8", "114.114.114.114"]
}
EOF

# 重启 Docker
echo "重启 Docker 服务..."
sudo systemctl daemon-reload
sudo systemctl restart docker

echo "✅ Docker 镜像源配置完成！"
echo ""
echo "测试拉取镜像："
docker pull python:3.11-slim
