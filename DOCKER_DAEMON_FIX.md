# Docker Daemon 未运行错误修复

## 错误信息

```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
Is the docker daemon running?
```

---

## ⚡ 快速修复（复制执行）

```bash
# 方式 1: 手动命令（推荐）
sudo systemctl start docker
sudo systemctl enable docker
sudo systemctl status docker

# 方式 2: 使用修复脚本
sudo bash fix-docker.sh

# 方式 3: 一键修复
sudo bash -c 'systemctl start docker && systemctl enable docker && docker ps'
```

---

## 🔍 问题诊断

### 步骤 1: 检查 Docker 服务状态

```bash
sudo systemctl status docker
```

#### 可能的输出及含义

**情况 A: 服务未运行**
```
● docker.service - Docker Application Container Engine
   Loaded: loaded
   Active: inactive (dead)
```
**解决**: `sudo systemctl start docker`

**情况 B: 服务失败**
```
● docker.service - Docker Application Container Engine
   Loaded: loaded
   Active: failed
```
**解决**: 查看日志 `sudo journalctl -u docker.service -n 50`

**情况 C: 服务正常**
```
● docker.service - Docker Application Container Engine
   Loaded: loaded
   Active: active (running)
```
**解决**: 检查权限问题（见下文）

---

## 🛠️ 解决方案

### 方案 1: 启动 Docker 服务（最常见）

```bash
# 1. 启动服务
sudo systemctl start docker

# 2. 检查状态
sudo systemctl status docker

# 3. 设置开机自启
sudo systemctl enable docker

# 4. 测试
sudo docker ps
```

### 方案 2: 重启 Docker 服务

```bash
# 完全重启
sudo systemctl restart docker

# 或者
sudo systemctl stop docker
sudo systemctl start docker
```

### 方案 3: 检查并修复 Docker Socket

```bash
# 检查 socket 文件
ls -l /var/run/docker.sock

# 如果不存在或权限错误
sudo systemctl restart docker

# 修复权限
sudo chmod 666 /var/run/docker.sock
```

### 方案 4: 用户权限问题

如果 Docker 服务正常但仍然报错：

```bash
# 1. 检查当前用户
whoami

# 2. 查看 docker 组成员
getent group docker

# 3. 将当前用户加入 docker 组
sudo usermod -aG docker $USER

# 4. 刷新组成员（或注销重新登录）
newgrp docker

# 5. 验证（不需要 sudo）
docker ps
```

### 方案 5: 完全重置 Docker

```bash
# 停止 Docker
sudo systemctl stop docker

# 清理残留文件
sudo rm -f /var/run/docker.pid
sudo rm -f /var/run/docker.sock

# 重新启动
sudo systemctl start docker

# 检查状态
sudo systemctl status docker
```

---

## 📋 使用修复脚本

### 上传并执行修复脚本

```bash
# 1. 上传 fix-docker.sh 到服务器

# 2. 添加执行权限
chmod +x fix-docker.sh

# 3. 执行修复
sudo bash fix-docker.sh
```

### 脚本功能

脚本会自动：
- ✅ 检查 Docker 安装
- ✅ 检查服务状态
- ✅ 启动 Docker 服务
- ✅ 设置开机自启动
- ✅ 配置用户权限
- ✅ 测试 Docker 功能

---

## 🔧 高级排查

### 1. 查看 Docker 日志

```bash
# 查看最近日志
sudo journalctl -u docker.service -n 100

# 实时查看日志
sudo journalctl -u docker.service -f

# 查看所有 Docker 日志
sudo tail -f /var/log/docker.log
```

### 2. 检查 Docker 配置

```bash
# 查看配置文件
cat /etc/docker/daemon.json

# 检查配置语法
sudo dockerd --validate --config-file=/etc/docker/daemon.json
```

### 3. 检查系统资源

```bash
# 检查磁盘空间
df -h

# 检查内存
free -h

# 检查进程
ps aux | grep docker
```

### 4. 检查网络

```bash
# 检查端口占用
sudo netstat -tulnp | grep docker

# 检查 Docker 网络
docker network ls
```

---

## 📊 常见错误类型

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `daemon not running` | Docker 服务未启动 | `systemctl start docker` |
| `permission denied` | 用户权限不足 | 加入 docker 组 |
| `socket not found` | socket 文件缺失 | 重启 Docker 服务 |
| `failed to start` | 配置错误或资源不足 | 查看日志修复 |

---

## 🎯 完整部署流程（修复后）

```bash
# 1. 确保 Docker 运行
sudo systemctl start docker
sudo systemctl enable docker

# 2. 验证 Docker
sudo docker ps

# 3. 配置镜像源（如果需要）
sudo bash setup-docker-mirror.sh

# 4. 进入项目目录
cd /www/wwwroot/pdf2zh/pdf_translate2pdf_api-main

# 5. 部署应用
docker-compose -f docker-compose.fastapi.yml up -d --build

# 6. 查看日志
docker-compose -f docker-compose.fastapi.yml logs -f

# 7. 验证服务
curl http://localhost:8000/health
```

---

## ⚠️ 注意事项

### 用户组刷新

将用户加入 docker 组后，需要：

**方式 1: 刷新当前会话**
```bash
newgrp docker
```

**方式 2: 重新登录**
```bash
# 注销当前 SSH 连接
exit

# 重新登录
ssh user@server
```

**方式 3: 使用 sudo（临时）**
```bash
# 在权限生效前使用 sudo
sudo docker ps
```

### 开机自启动

确保设置了开机自启：
```bash
sudo systemctl enable docker
```

验证：
```bash
sudo systemctl is-enabled docker
# 应该输出: enabled
```

---

## 🚀 快速测试

```bash
# 测试 1: Docker 版本
docker --version

# 测试 2: Docker 信息
docker info

# 测试 3: 运行测试容器
docker run hello-world

# 测试 4: 查看容器
docker ps -a

# 测试 5: 清理测试容器
docker rm $(docker ps -aq --filter "ancestor=hello-world")
```

---

## 💡 预防措施

### 设置 Docker 服务自动重启

```bash
# 编辑服务配置
sudo systemctl edit docker.service

# 添加以下内容
[Service]
Restart=always
RestartSec=10s

# 保存并重载
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 监控 Docker 状态

```bash
# 创建监控脚本
cat > /usr/local/bin/check-docker.sh << 'EOF'
#!/bin/bash
if ! systemctl is-active --quiet docker; then
    echo "Docker is down, restarting..."
    systemctl start docker
fi
EOF

chmod +x /usr/local/bin/check-docker.sh

# 添加到 crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/check-docker.sh") | crontab -
```

---

## 📞 需要帮助？

如果以上方案都无法解决，请提供以下信息：

```bash
# 1. 系统信息
uname -a
cat /etc/os-release

# 2. Docker 版本
docker --version

# 3. 服务状态
sudo systemctl status docker

# 4. 日志信息
sudo journalctl -u docker.service -n 50

# 5. 配置信息
cat /etc/docker/daemon.json
```

---

## 🎉 成功验证

修复成功后，应该能看到：

```bash
$ docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES

$ docker info
Client:
 Context:    default
 Debug Mode: false

Server:
 Containers: 0
  Running: 0
  Paused: 0
  Stopped: 0
 Images: 0
```

---

## 相关文档

- [DOCKER_ERROR_FIX.md](DOCKER_ERROR_FIX.md) - 镜像源问题
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - 完整部署指南
- [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - 快速开始

---

**立即执行快速修复命令，问题就能解决！** 🚀
