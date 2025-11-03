# 网络访问问题修复指南

## 问题描述

无法从 Docker Hub 和 GHCR 拉取镜像：
- ❌ `docker.io` (Docker Hub)
- ❌ `ghcr.io` (GitHub Container Registry)

错误：`failed to fetch anonymous token: Not Found`

---

## 原因

您的服务器无法访问国际镜像源，需要使用国内可访问的镜像。

---

## ⚡ 快速修复（在服务器上执行）

### 步骤 1: 修改 Dockerfile.fastapi

```bash
cd /www/wwwroot/pdf2zh/pdf_translate2pdf_api-main

# 备份原文件
cp Dockerfile.fastapi Dockerfile.fastapi.backup

# 修改第一行，使用阿里云镜像
sed -i 's|FROM python:3.11-slim|FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim|g' Dockerfile.fastapi

# 验证修改
head -n 5 Dockerfile.fastapi
```

### 步骤 2: 添加 pip 国内源

```bash
# 在 Dockerfile.fastapi 中添加 pip 国内源配置
# 在 WORKDIR /app 后面添加

cat >> Dockerfile.fastapi.tmp << 'EOF'
# FastAPI 专用 Dockerfile
# 使用阿里云镜像源以解决国内网络访问问题

FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim

WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ \
    PIP_TRUSTED_HOST=mirrors.aliyun.com

# 安装系统依赖（OpenCV 和其他依赖）
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    libgl1 \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY pyproject.toml .
COPY README.md .
COPY pdf2zh ./pdf2zh

# 安装 Python 依赖
RUN pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip install -e . -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip install fastapi uvicorn[standard] python-multipart -i https://mirrors.aliyun.com/pypi/simple/

# 暴露端口（FastAPI 默认 8000）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动 FastAPI 服务
CMD ["python", "-m", "pdf2zh", "--fastapi", "--apiport", "8000"]
EOF

# 替换原文件
mv Dockerfile.fastapi.tmp Dockerfile.fastapi
```

### 步骤 3: 重新构建

```bash
docker-compose -f docker-compose.fastapi.yml build --no-cache
docker-compose -f docker-compose.fastapi.yml up -d
```

---

## 🚀 完整解决方案（复制执行）

```bash
# === 在服务器上执行 ===

cd /www/wwwroot/pdf2zh/pdf_translate2pdf_api-main

# 1. 创建使用国内源的 Dockerfile
cat > Dockerfile.fastapi << 'EOF'
# FastAPI 专用 Dockerfile
# 使用阿里云镜像源以解决国内网络访问问题

FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim

WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 配置 pip 使用阿里云镜像
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set install.trusted-host mirrors.aliyun.com

# 安装系统依赖
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    libgl1 \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY pyproject.toml .
COPY README.md .
COPY pdf2zh ./pdf2zh

# 安装 Python 依赖（使用阿里云 pip 源）
RUN pip install --upgrade pip && \
    pip install -e . && \
    pip install fastapi uvicorn[standard] python-multipart

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动服务
CMD ["python", "-m", "pdf2zh", "--fastapi", "--apiport", "8000"]
EOF

# 2. 构建并启动
docker-compose -f docker-compose.fastapi.yml build --no-cache
docker-compose -f docker-compose.fastapi.yml up -d

# 3. 查看日志
docker-compose -f docker-compose.fastapi.yml logs -f
```

---

## 📋 其他可用的国内镜像源

### Python 镜像源选项

```dockerfile
# 选项 1: 阿里云（推荐）
FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim

# 选项 2: 腾讯云
FROM ccr.ccs.tencentyun.com/library/python:3.11-slim

# 选项 3: 网易云
FROM hub-mirror.c.163.com/library/python:3.11-slim
```

### Pip 镜像源选项

```bash
# 阿里云
https://mirrors.aliyun.com/pypi/simple/

# 清华大学
https://pypi.tuna.tsinghua.edu.cn/simple/

# 中科大
https://pypi.mirrors.ustc.edu.cn/simple/

# 华为云
https://repo.huaweicloud.com/repository/pypi/simple/
```

---

## 🔧 方案 2: 预先拉取镜像（备选）

如果修改 Dockerfile 后仍有问题：

```bash
# 1. 从阿里云拉取基础镜像
docker pull registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim

# 2. 重新打标签
docker tag registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim python:3.11-slim

# 3. 验证
docker images | grep python

# 4. 重新构建（使用本地镜像）
docker-compose -f docker-compose.fastapi.yml build --no-cache
```

---

## 🔍 验证网络连接

```bash
# 测试 Docker Hub 连接
curl -I https://auth.docker.io/token

# 测试阿里云镜像源
curl -I https://registry.cn-hangzhou.aliyuncs.com/v2/

# 测试 pip 源
curl -I https://mirrors.aliyun.com/pypi/simple/
```

---

## 💡 推荐的完整 Dockerfile（已优化）

```dockerfile
# 使用国内镜像源
FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim

WORKDIR /app

# 环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    # 配置 pip 使用国内源
    PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ \
    PIP_TRUSTED_HOST=mirrors.aliyun.com

# 配置 apt 使用阿里云源（可选，加速系统包安装）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    libgl1 libglib2.0-0 libxext6 libsm6 libxrender1 curl && \
    rm -rf /var/lib/apt/lists/*

# 复制文件
COPY pyproject.toml README.md ./
COPY pdf2zh ./pdf2zh

# 安装依赖
RUN pip install --upgrade pip && \
    pip install -e . && \
    pip install fastapi uvicorn[standard] python-multipart

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "pdf2zh", "--fastapi", "--apiport", "8000"]
```

---

## 🎯 故障排查

### 如果构建仍然失败

```bash
# 1. 清理所有缓存
docker system prune -a --volumes -f

# 2. 手动拉取基础镜像
docker pull registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim

# 3. 测试基础镜像
docker run --rm registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim python --version

# 4. 重新构建
docker-compose -f docker-compose.fastapi.yml build --no-cache
```

### 查看详细构建日志

```bash
# 带详细日志构建
docker-compose -f docker-compose.fastapi.yml build --no-cache --progress=plain

# 或使用 docker build
docker build -f Dockerfile.fastapi -t pdf2zh-api:latest . --no-cache --progress=plain
```

---

## ✅ 验证部署成功

```bash
# 1. 检查容器状态
docker-compose -f docker-compose.fastapi.yml ps

# 2. 查看日志
docker-compose -f docker-compose.fastapi.yml logs -f pdf2zh-api

# 3. 健康检查
curl http://localhost:8000/health

# 4. 访问 API 文档
curl http://localhost:8000/docs
```

---

## 📊 总结

**问题**: 无法访问国际镜像源
**解决**: 使用国内镜像源（阿里云、腾讯云等）

**修改点**:
1. ✅ Dockerfile 基础镜像改为阿里云
2. ✅ pip 配置改为阿里云源
3. ✅ apt 源改为阿里云（可选）

**预计时间**:
- 修改 Dockerfile: 2 分钟
- 构建镜像: 5-10 分钟
- 启动服务: 30 秒
- **总计**: 约 10-15 分钟

---

立即在服务器上执行**完整解决方案**中的命令！🚀
