# Docker 部署错误修复指南

## 错误信息

```
failed to resolve source metadata for docker.io/library/python:3.11-slim
remote error: tls: unrecognized name
```

---

## 原因分析

从错误 `registry-1.abcio.xyz` 看，您的服务器配置了自定义 Docker 镜像源，但该源：
1. ❌ 无法正常访问
2. ❌ TLS 证书配置有问题
3. ❌ 或者域名解析失败

---

## 解决方案

### 方案 1: 配置国内镜像源（推荐，最快）

#### 步骤 1: 上传脚本到服务器

将 `setup-docker-mirror.sh` 上传到服务器，或直接在服务器执行：

```bash
# 方法 1: 创建并执行脚本
cat > setup-docker-mirror.sh << 'EOF'
#!/bin/bash
echo "配置 Docker 国内镜像源..."

# 备份原配置
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.backup 2>/dev/null || true

# 创建或更新配置
sudo tee /etc/docker/daemon.json > /dev/null <<JSON
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.ccs.tencentyun.com",
    "https://registry.docker-cn.com"
  ],
  "dns": ["8.8.8.8", "114.114.114.114"]
}
JSON

# 重启 Docker
echo "重启 Docker 服务..."
sudo systemctl daemon-reload
sudo systemctl restart docker

echo "✅ Docker 镜像源配置完成！"
docker info | grep -A 4 "Registry Mirrors"
EOF

chmod +x setup-docker-mirror.sh
sudo ./setup-docker-mirror.sh
```

#### 步骤 2: 验证配置

```bash
# 检查配置
docker info | grep -A 4 "Registry Mirrors"

# 预期输出
# Registry Mirrors:
#  https://docker.mirrors.ustc.edu.cn/
#  https://hub-mirror.c.163.com/
```

#### 步骤 3: 测试拉取镜像

```bash
docker pull python:3.11-slim
```

#### 步骤 4: 重新构建

```bash
cd /www/wwwroot/pdf2zh/pdf_translate2pdf_api-main
docker-compose -f docker-compose.fastapi.yml up -d --build
```

---

### 方案 2: 手动配置 Docker daemon（同方案1）

```bash
# 1. 编辑 Docker 配置
sudo vim /etc/docker/daemon.json

# 2. 添加以下内容（如果文件已存在，合并配置）
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.ccs.tencentyun.com"
  ]
}

# 3. 重启 Docker
sudo systemctl daemon-reload
sudo systemctl restart docker

# 4. 验证
docker info | grep -A 4 "Registry Mirrors"
```

---

### 方案 3: 预先拉取镜像

如果镜像源配置失败，可以先手动拉取镜像：

```bash
# 1. 从其他可用源拉取
docker pull python:3.11-slim

# 如果上述失败，尝试国内镜像
docker pull docker.mirrors.ustc.edu.cn/library/python:3.11-slim

# 重新打标签
docker tag docker.mirrors.ustc.edu.cn/library/python:3.11-slim python:3.11-slim

# 2. 然后构建
docker-compose -f docker-compose.fastapi.yml build --no-cache

# 3. 启动
docker-compose -f docker-compose.fastapi.yml up -d
```

---

### 方案 4: 修改 Dockerfile 使用国内源

编辑 `Dockerfile.fastapi`，修改基础镜像源：

```dockerfile
# 方式 1: 使用阿里云镜像
FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim

# 或方式 2: 使用腾讯云镜像
FROM ccr.ccs.tencentyun.com/library/python:3.11-slim

# 剩余内容保持不变...
```

---

### 方案 5: 修复现有镜像源配置

如果您的服务器已配置了 `abcio.xyz` 镜像源但无法使用：

```bash
# 1. 检查当前配置
cat /etc/docker/daemon.json

# 2. 移除或替换问题源
sudo vim /etc/docker/daemon.json

# 3. 删除或注释掉 abcio.xyz 相关配置
# 例如：删除 "registry-mirrors": ["https://registry-1.abcio.xyz"]

# 4. 重启 Docker
sudo systemctl restart docker
```

---

## 推荐配置（完整版）

### 最佳 `/etc/docker/daemon.json` 配置

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.ccs.tencentyun.com",
    "https://registry.docker-cn.com"
  ],
  "dns": ["8.8.8.8", "114.114.114.114"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

## 完整部署流程（修复后）

```bash
# 1. 配置镜像源（选择上述任一方案）
sudo ./setup-docker-mirror.sh

# 2. 验证镜像源
docker info | grep -A 4 "Registry Mirrors"

# 3. 进入项目目录
cd /www/wwwroot/pdf2zh/pdf_translate2pdf_api-main

# 4. 清理旧构建（可选）
docker-compose -f docker-compose.fastapi.yml down
docker system prune -f

# 5. 重新构建并启动
docker-compose -f docker-compose.fastapi.yml up -d --build

# 6. 查看日志
docker-compose -f docker-compose.fastapi.yml logs -f

# 7. 验证服务
curl http://localhost:8000/health
```

---

## 常用国内镜像源列表

| 镜像源 | 地址 | 说明 |
|--------|------|------|
| **中科大** | https://docker.mirrors.ustc.edu.cn | 推荐，速度快 |
| **网易** | https://hub-mirror.c.163.com | 稳定 |
| **腾讯云** | https://mirror.ccs.tencentyun.com | 商用推荐 |
| **阿里云** | https://registry.cn-hangzhou.aliyuncs.com | 需要登录 |
| **Docker CN** | https://registry.docker-cn.com | 官方中国源 |

---

## 故障排查

### 检查 1: Docker 服务状态

```bash
sudo systemctl status docker
```

### 检查 2: 网络连接

```bash
# 测试 Docker Hub 连接
curl -I https://registry-1.docker.io/v2/

# 测试国内镜像源
curl -I https://docker.mirrors.ustc.edu.cn/v2/
```

### 检查 3: DNS 解析

```bash
# 检查 DNS
nslookup registry-1.docker.io
nslookup docker.mirrors.ustc.edu.cn
```

### 检查 4: Docker 配置

```bash
# 查看完整 Docker 信息
docker info

# 查看镜像源配置
cat /etc/docker/daemon.json
```

### 检查 5: 防火墙

```bash
# 检查防火墙状态
sudo firewall-cmd --state

# 或
sudo iptables -L
```

---

## 验证部署成功

```bash
# 1. 检查容器状态
docker-compose -f docker-compose.fastapi.yml ps

# 预期输出
# NAME               IMAGE                      STATUS
# pdf2zh-fastapi     pdf2zh-api                 Up 2 minutes

# 2. 健康检查
curl http://localhost:8000/health

# 预期输出
# {"status":"healthy","version":"1.0.0","service":"PDFMathTranslate API"}

# 3. 查看 API 文档
curl http://localhost:8000/docs

# 或在浏览器访问
# http://YOUR_SERVER_IP:8000/docs
```

---

## 快速修复命令（一键执行）

```bash
# 在服务器上执行（需要 root 权限）
sudo bash -c 'cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.ccs.tencentyun.com"
  ],
  "dns": ["8.8.8.8", "114.114.114.114"]
}
EOF
systemctl daemon-reload && systemctl restart docker && docker info | grep -A 4 "Registry Mirrors"'

# 然后重新部署
cd /www/wwwroot/pdf2zh/pdf_translate2pdf_api-main
docker-compose -f docker-compose.fastapi.yml up -d --build
```

---

## 附录：阿里云镜像加速器（推荐企业用户）

### 获取专属加速地址

1. 登录阿里云控制台
2. 访问：https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors
3. 获取您的专属加速地址，例如：`https://xxxxx.mirror.aliyuncs.com`

### 配置

```bash
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://xxxxx.mirror.aliyuncs.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
EOF

sudo systemctl restart docker
```

---

## 总结

### ✅ 推荐步骤（最快解决）

1. **配置国内镜像源** → 方案 1
2. **重启 Docker** → `systemctl restart docker`
3. **验证配置** → `docker info`
4. **重新构建** → `docker-compose up -d --build`
5. **验证服务** → `curl http://localhost:8000/health`

### ⏱️ 预计修复时间

- 配置镜像源：1-2 分钟
- 拉取镜像：3-5 分钟（取决于网速）
- 构建服务：2-3 分钟
- **总计**：约 5-10 分钟

---

## 需要帮助？

如果上述方案都无法解决，请提供：

```bash
# 1. Docker 版本
docker --version

# 2. Docker Compose 版本
docker-compose --version

# 3. Docker 信息
docker info

# 4. 当前配置
cat /etc/docker/daemon.json

# 5. 网络测试
curl -I https://docker.mirrors.ustc.edu.cn/v2/
```
