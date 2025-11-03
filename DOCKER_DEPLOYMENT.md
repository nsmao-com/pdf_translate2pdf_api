# Docker 部署指南

## 快速开始

### 方式 1: 使用 docker-compose（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/PDFMathTranslate.git
cd PDFMathTranslate

# 2. 启动 FastAPI 服务
docker-compose -f docker-compose.fastapi.yml up -d

# 3. 查看日志
docker-compose -f docker-compose.fastapi.yml logs -f

# 4. 测试服务
curl http://localhost:8000/health
```

### 方式 2: 使用 Docker 命令

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/PDFMathTranslate.git
cd PDFMathTranslate

# 2. 构建镜像
docker build -f Dockerfile.fastapi -t pdf2zh-api:latest .

# 3. 运行容器
docker run -d \
  --name pdf2zh-api \
  -p 8000:8000 \
  --restart unless-stopped \
  pdf2zh-api:latest

# 4. 查看日志
docker logs -f pdf2zh-api

# 5. 测试服务
curl http://localhost:8000/health
```

### 方式 3: 直接从 GitHub 构建（无需克隆）

```bash
# 直接从 GitHub 仓库构建
docker build \
  -f Dockerfile.fastapi \
  -t pdf2zh-api:latest \
  https://github.com/YOUR_USERNAME/PDFMathTranslate.git

# 运行
docker run -d -p 8000:8000 pdf2zh-api:latest
```

---

## 详细配置

### 1. 环境变量配置

创建 `.env` 文件：

```bash
# .env
# OpenAI
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# DeepL
DEEPL_AUTH_KEY=your-deepl-key-here

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

修改 `docker-compose.fastapi.yml`：

```yaml
services:
  pdf2zh-api:
    # ... 其他配置
    env_file:
      - .env  # 加载环境变量
```

### 2. 配置文件挂载

创建 `config.json`：

```json
{
  "openai": {
    "api_key": "sk-...",
    "base_url": "https://api.openai.com/v1"
  },
  "deepl": {
    "auth_key": "..."
  }
}
```

修改 docker-compose.yml 挂载配置：

```yaml
volumes:
  - ./config.json:/root/.config/PDFMathTranslate/config.json:ro
```

### 3. 持久化缓存

```yaml
volumes:
  - pdf2zh-cache:/root/.cache/pdf2zh  # 缓存翻译结果
```

---

## Docker Compose 完整配置

### docker-compose.fastapi.yml

```yaml
version: '3.8'

services:
  pdf2zh-api:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    container_name: pdf2zh-fastapi
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    env_file:
      - .env  # 可选：环境变量
    volumes:
      - ./config.json:/root/.config/PDFMathTranslate/config.json:ro  # 可选
      - pdf2zh-cache:/root/.cache/pdf2zh  # 缓存
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks:
      - pdf2zh-network

volumes:
  pdf2zh-cache:
    driver: local

networks:
  pdf2zh-network:
    driver: bridge
```

---

## 使用场景

### 场景 1: 开发环境

```bash
# 启动服务（前台运行，可以看到日志）
docker-compose -f docker-compose.fastapi.yml up

# Ctrl+C 停止
```

### 场景 2: 生产环境

```bash
# 后台启动
docker-compose -f docker-compose.fastapi.yml up -d

# 查看日志
docker-compose -f docker-compose.fastapi.yml logs -f

# 重启服务
docker-compose -f docker-compose.fastapi.yml restart

# 停止并移除
docker-compose -f docker-compose.fastapi.yml down
```

### 场景 3: 同时启动 API 和 GUI

```bash
# 启动 API 和 GUI
docker-compose -f docker-compose.fastapi.yml --profile gui up -d

# API: http://localhost:8000/docs
# GUI: http://localhost:7860
```

---

## 常用命令

### 查看服务状态

```bash
docker-compose -f docker-compose.fastapi.yml ps
```

### 查看实时日志

```bash
docker-compose -f docker-compose.fastapi.yml logs -f pdf2zh-api
```

### 进入容器调试

```bash
docker exec -it pdf2zh-fastapi bash
```

### 重新构建镜像

```bash
docker-compose -f docker-compose.fastapi.yml build --no-cache
```

### 更新并重启

```bash
# 拉取最新代码（如果使用 git）
git pull

# 重新构建并启动
docker-compose -f docker-compose.fastapi.yml up -d --build
```

---

## 从 GitHub 直接部署

### 方式 1: 使用 docker build

```bash
# 从 GitHub 主分支构建
docker build \
  -f Dockerfile.fastapi \
  -t pdf2zh-api:latest \
  https://github.com/YOUR_USERNAME/PDFMathTranslate.git#main

# 运行
docker run -d -p 8000:8000 --name pdf2zh-api pdf2zh-api:latest
```

### 方式 2: 使用 docker-compose

创建一个新目录，只需要 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  pdf2zh-api:
    image: ghcr.io/YOUR_USERNAME/pdf2zh-api:latest  # 使用已发布的镜像
    container_name: pdf2zh-fastapi
    ports:
      - "8000:8000"
    restart: unless-stopped
```

```bash
docker-compose up -d
```

---

## 发布到 GitHub Container Registry (GHCR)

### 1. 登录 GHCR

```bash
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

### 2. 构建并推送镜像

```bash
# 构建
docker build -f Dockerfile.fastapi -t ghcr.io/YOUR_USERNAME/pdf2zh-api:latest .

# 推送
docker push ghcr.io/YOUR_USERNAME/pdf2zh-api:latest
```

### 3. 设置 GitHub Actions 自动构建

创建 `.github/workflows/docker-publish.yml`：

```yaml
name: Docker Image CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Log in to GitHub Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./Dockerfile.fastapi
        push: true
        tags: |
          ghcr.io/${{ github.repository_owner }}/pdf2zh-api:latest
          ghcr.io/${{ github.repository_owner }}/pdf2zh-api:${{ github.sha }}
```

### 4. 使用发布的镜像

```bash
docker pull ghcr.io/YOUR_USERNAME/pdf2zh-api:latest
docker run -d -p 8000:8000 ghcr.io/YOUR_USERNAME/pdf2zh-api:latest
```

---

## 测试部署

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

**预期响应**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "PDFMathTranslate API"
}
```

### 2. 查看 API 文档

打开浏览器访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. 测试翻译

```bash
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@test.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=google" \
  --output translated.pdf
```

---

## 性能优化

### 1. 使用多阶段构建（优化镜像大小）

修改 `Dockerfile.fastapi`：

```dockerfile
# 构建阶段
FROM python:3.11-slim AS builder

WORKDIR /app
COPY pyproject.toml README.md ./
COPY pdf2zh ./pdf2zh

RUN pip install --user --no-cache-dir -e . && \
    pip install --user --no-cache-dir fastapi uvicorn python-multipart

# 运行阶段
FROM python:3.11-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    libgl1 libglib2.0-0 curl && \
    rm -rf /var/lib/apt/lists/*

# 从构建阶段复制
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000
CMD ["python", "-m", "pdf2zh", "--fastapi", "--apiport", "8000"]
```

### 2. 使用 Nginx 反向代理

创建 `docker-compose.nginx.yml`：

```yaml
version: '3.8'

services:
  pdf2zh-api:
    # ... API 配置
    expose:
      - "8000"  # 不直接暴露到主机

  nginx:
    image: nginx:alpine
    container_name: pdf2zh-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro  # SSL 证书
    depends_on:
      - pdf2zh-api
    restart: unless-stopped
    networks:
      - pdf2zh-network
```

`nginx.conf`:

```nginx
upstream pdf2zh {
    server pdf2zh-api:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://pdf2zh;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # 文件上传限制
        client_max_body_size 50M;
    }
}
```

---

## 监控和日志

### 1. 查看容器资源使用

```bash
docker stats pdf2zh-fastapi
```

### 2. 持久化日志

修改 docker-compose.yml：

```yaml
services:
  pdf2zh-api:
    # ... 其他配置
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 3. 集成 Prometheus 监控（可选）

安装 prometheus-fastapi-instrumentator：

```dockerfile
RUN pip install prometheus-fastapi-instrumentator
```

修改 `fastapi_server.py`：

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(...)
Instrumentator().instrument(app).expose(app)
```

---

## 故障排查

### 问题 1: 容器启动失败

```bash
# 查看详细日志
docker logs pdf2zh-fastapi

# 检查容器状态
docker inspect pdf2zh-fastapi
```

### 问题 2: 端口被占用

```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# 更换端口
docker run -p 9000:8000 pdf2zh-api:latest
```

### 问题 3: 依赖安装失败

```bash
# 重新构建（不使用缓存）
docker build --no-cache -f Dockerfile.fastapi -t pdf2zh-api:latest .
```

### 问题 4: 内存不足

修改 docker-compose.yml：

```yaml
services:
  pdf2zh-api:
    # ... 其他配置
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

---

## 安全建议

### 1. 不要在镜像中硬编码密钥

✅ **使用环境变量**:
```yaml
environment:
  - OPENAI_API_KEY=${OPENAI_API_KEY}
```

❌ **不要这样做**:
```dockerfile
ENV OPENAI_API_KEY=sk-xxxxx  # 危险！
```

### 2. 使用 Docker Secrets（Swarm）

```yaml
services:
  pdf2zh-api:
    secrets:
      - openai_key
    environment:
      - OPENAI_API_KEY=/run/secrets/openai_key

secrets:
  openai_key:
    external: true
```

### 3. 限制容器权限

```yaml
services:
  pdf2zh-api:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
```

---

## 生产环境检查清单

- [ ] 使用环境变量管理密钥
- [ ] 配置健康检查
- [ ] 设置资源限制
- [ ] 启用日志轮转
- [ ] 配置重启策略
- [ ] 使用 HTTPS（通过 Nginx）
- [ ] 设置防火墙规则
- [ ] 定期备份缓存数据
- [ ] 监控容器性能
- [ ] 配置自动更新

---

## 快速参考

| 命令 | 说明 |
|------|------|
| `docker-compose up -d` | 后台启动 |
| `docker-compose logs -f` | 查看日志 |
| `docker-compose ps` | 查看状态 |
| `docker-compose restart` | 重启服务 |
| `docker-compose down` | 停止并移除 |
| `docker-compose build --no-cache` | 重新构建 |
| `docker exec -it <container> bash` | 进入容器 |
| `docker stats` | 查看资源使用 |

---

## 总结

### ✅ 直接从 GitHub 使用 Docker

**可以！** 有以下方式：

1. **克隆后构建** (推荐)
   ```bash
   git clone https://github.com/YOUR_USERNAME/PDFMathTranslate.git
   cd PDFMathTranslate
   docker-compose -f docker-compose.fastapi.yml up -d
   ```

2. **直接构建**
   ```bash
   docker build -f Dockerfile.fastapi \
     -t pdf2zh-api:latest \
     https://github.com/YOUR_USERNAME/PDFMathTranslate.git
   ```

3. **使用发布的镜像**
   ```bash
   docker pull ghcr.io/YOUR_USERNAME/pdf2zh-api:latest
   docker run -d -p 8000:8000 ghcr.io/YOUR_USERNAME/pdf2zh-api:latest
   ```

### 推荐部署流程

1. 推送代码到 GitHub
2. 配置 GitHub Actions 自动构建
3. 发布到 GHCR
4. 在服务器上直接使用发布的镜像

---

## 相关文档

- [FastAPI 使用文档](docs/FASTAPI.md)
- [快速开始指南](FASTAPI_QUICKSTART.md)
- [演示版 vs 生产版对比](演示版vs生产版对比.md)
