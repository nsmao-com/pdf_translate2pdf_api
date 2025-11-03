# 预构建镜像部署指南

## 适用场景

当服务器**无法访问外部镜像仓库**时使用此方案。

---

## 步骤 1: 在本地构建镜像

### 在您的 Windows 电脑上执行（有网络的环境）

```powershell
# 1. 进入项目目录
cd D:\2024Dev\PDFMathTranslate-main

# 2. 确保 Docker Desktop 正在运行
docker version

# 3. 构建镜像
docker build -f Dockerfile.fastapi -t pdf2zh-api:latest .

# 4. 验证镜像
docker images | findstr pdf2zh-api

# 5. 导出镜像
docker save -o pdf2zh-api.tar pdf2zh-api:latest

# 6. 压缩镜像（可选，减小文件大小）
# 在 Windows 上可以使用 7-Zip 或其他压缩工具
# 或使用 WSL
wsl gzip pdf2zh-api.tar
```

**预期文件大小**: 约 1-2 GB（压缩后约 500-800 MB）

---

## 步骤 2: 上传到服务器

### 方式 A: 使用 SCP

```powershell
# 从 Windows 上传到服务器
scp pdf2zh-api.tar.gz root@YOUR_SERVER_IP:/tmp/

# 或者不压缩直接传
scp pdf2zh-api.tar root@YOUR_SERVER_IP:/tmp/
```

### 方式 B: 使用 FTP/SFTP 工具

使用 FileZilla、WinSCP 等工具上传：
- 源文件: `D:\2024Dev\PDFMathTranslate-main\pdf2zh-api.tar.gz`
- 目标路径: `/tmp/pdf2zh-api.tar.gz`

### 方式 C: 使用宝塔面板

如果服务器安装了宝塔面板，直接通过网页上传。

---

## 步骤 3: 在服务器导入镜像

```bash
# 登录服务器
ssh root@YOUR_SERVER_IP

# 进入上传目录
cd /tmp

# 如果压缩了，先解压
gunzip pdf2zh-api.tar.gz

# 导入镜像到 Docker
docker load -i pdf2zh-api.tar

# 验证镜像已导入
docker images | grep pdf2zh-api

# 应该看到输出
# pdf2zh-api   latest   xxxxxxxxxxxx   xxx MB
```

---

## 步骤 4: 部署应用

```bash
# 进入项目目录
cd /www/wwwroot/pdf2zh/pdf_translate2pdf_api-main

# 上传或创建 docker-compose.fastapi-prebuilt.yml
# （使用预构建镜像的配置文件）

# 启动服务
docker-compose -f docker-compose.fastapi-prebuilt.yml up -d

# 查看日志
docker-compose -f docker-compose.fastapi-prebuilt.yml logs -f

# 验证服务
curl http://localhost:8000/health
```

---

## 📋 docker-compose.fastapi-prebuilt.yml

```yaml
services:
  pdf2zh-api:
    image: pdf2zh-api:latest  # 使用本地镜像
    container_name: pdf2zh-fastapi
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - pdf2zh-cache:/root/.cache/pdf2zh
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  pdf2zh-cache:
    driver: local
```

---

## 🔧 故障排查

### 问题 1: 导入镜像失败

```bash
# 检查文件完整性
ls -lh /tmp/pdf2zh-api.tar

# 检查磁盘空间
df -h

# 清理空间后重试
docker system prune -a --volumes -f
```

### 问题 2: 镜像导入后找不到

```bash
# 列出所有镜像
docker images

# 如果没有，重新导入
docker load -i /tmp/pdf2zh-api.tar

# 查看导入日志
docker load -i /tmp/pdf2zh-api.tar 2>&1 | tee import.log
```

### 问题 3: 容器启动失败

```bash
# 查看详细日志
docker logs pdf2zh-fastapi

# 检查端口占用
netstat -tulnp | grep 8000

# 重新启动
docker-compose -f docker-compose.fastapi-prebuilt.yml restart
```

---

## 🎯 完整命令清单

### 在 Windows 本地（有网络）

```powershell
cd D:\2024Dev\PDFMathTranslate-main
docker build -f Dockerfile.fastapi -t pdf2zh-api:latest .
docker save -o pdf2zh-api.tar pdf2zh-api:latest
```

### 上传到服务器

```powershell
scp pdf2zh-api.tar root@YOUR_SERVER:/tmp/
```

### 在服务器上（无网络）

```bash
cd /tmp
docker load -i pdf2zh-api.tar
docker images | grep pdf2zh-api

cd /www/wwwroot/pdf2zh/pdf_translate2pdf_api-main
docker-compose -f docker-compose.fastapi-prebuilt.yml up -d
docker-compose -f docker-compose.fastapi-prebuilt.yml logs -f
curl http://localhost:8000/health
```

---

## ✅ 验证部署成功

```bash
# 1. 检查容器状态
docker ps | grep pdf2zh

# 2. 检查健康状态
curl http://localhost:8000/health

# 预期输出
# {"status":"healthy","version":"1.0.0","service":"PDFMathTranslate API"}

# 3. 访问 API 文档
curl http://YOUR_SERVER_IP:8000/docs

# 4. 测试翻译（需要有测试 PDF）
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@test.pdf" \
  -F "service=google" \
  --output translated.pdf
```

---

## 📊 文件大小参考

| 文件 | 大小（约） | 说明 |
|------|-----------|------|
| pdf2zh-api.tar | 1.5-2 GB | 未压缩镜像 |
| pdf2zh-api.tar.gz | 600-800 MB | 压缩后镜像 |
| 传输时间 (10Mbps) | 8-13 分钟 | 上传到服务器 |

---

## 💡 优化建议

### 减小镜像大小

在 Dockerfile.fastapi 中使用多阶段构建：

```dockerfile
# 构建阶段
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml README.md ./
COPY pdf2zh ./pdf2zh
RUN pip install --user -e . && \
    pip install --user fastapi uvicorn python-multipart

# 运行阶段
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 curl && \
    rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["python", "-m", "pdf2zh", "--fastapi", "--apiport", "8000"]
```

### 增量更新

只更新代码部分，不重新构建整个镜像：

```bash
# 方式 1: 使用 volume 挂载代码
docker run -d \
  -p 8000:8000 \
  -v /path/to/pdf2zh:/app/pdf2zh \
  pdf2zh-api:latest

# 方式 2: 直接在容器内更新
docker cp pdf2zh/ pdf2zh-fastapi:/app/
docker restart pdf2zh-fastapi
```

---

## 🔄 更新流程

当需要更新应用时：

```bash
# 1. 在本地重新构建
docker build -f Dockerfile.fastapi -t pdf2zh-api:v2 .
docker save -o pdf2zh-api-v2.tar pdf2zh-api:v2

# 2. 上传到服务器
scp pdf2zh-api-v2.tar root@SERVER:/tmp/

# 3. 在服务器导入
docker load -i /tmp/pdf2zh-api-v2.tar

# 4. 更新部署
docker-compose -f docker-compose.fastapi-prebuilt.yml down
# 修改 docker-compose 中的 image 为 pdf2zh-api:v2
docker-compose -f docker-compose.fastapi-prebuilt.yml up -d
```

---

## 📞 需要帮助？

如果遇到问题，请提供：

```bash
# 1. 镜像列表
docker images

# 2. 容器状态
docker ps -a

# 3. 容器日志
docker logs pdf2zh-fastapi

# 4. 系统信息
docker info
df -h
free -h
```

---

这是**最可靠的部署方案**，完全不依赖服务器的外网访问！
