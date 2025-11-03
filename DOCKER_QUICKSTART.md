# Docker 快速部署

## 🚀 三种部署方式

### 方式 1: 克隆后使用 docker-compose（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/PDFMathTranslate.git
cd PDFMathTranslate

# 2. 启动服务
docker-compose -f docker-compose.fastapi.yml up -d

# 3. 访问 API
# http://localhost:8000/docs
```

### 方式 2: 直接从 GitHub 构建

```bash
# 无需克隆仓库，直接从 GitHub 构建
docker build \
  -f Dockerfile.fastapi \
  -t pdf2zh-api:latest \
  https://github.com/YOUR_USERNAME/PDFMathTranslate.git

# 运行
docker run -d -p 8000:8000 --name pdf2zh-api pdf2zh-api:latest

# 访问 API
# http://localhost:8000/docs
```

### 方式 3: 使用预构建镜像（最快）

```bash
# 直接拉取并运行
docker pull ghcr.io/YOUR_USERNAME/pdf2zh-api:latest
docker run -d -p 8000:8000 ghcr.io/YOUR_USERNAME/pdf2zh-api:latest

# 访问 API
# http://localhost:8000/docs
```

---

## ✅ 验证部署

```bash
# 健康检查
curl http://localhost:8000/health

# 预期响应
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "PDFMathTranslate API"
}

# 查看 API 文档
# 打开浏览器: http://localhost:8000/docs
```

---

## 📝 配置环境变量

创建 `.env` 文件：

```bash
# .env
OPENAI_API_KEY=sk-your-key-here
DEEPL_AUTH_KEY=your-deepl-key
```

使用 docker-compose：

```yaml
services:
  pdf2zh-api:
    env_file:
      - .env
```

或使用 docker run：

```bash
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-xxx \
  -e DEEPL_AUTH_KEY=xxx \
  pdf2zh-api:latest
```

---

## 🔧 常用命令

```bash
# 查看日志
docker logs -f pdf2zh-api

# 重启服务
docker restart pdf2zh-api

# 停止服务
docker stop pdf2zh-api

# 移除容器
docker rm pdf2zh-api

# 更新镜像
docker pull ghcr.io/YOUR_USERNAME/pdf2zh-api:latest
docker stop pdf2zh-api && docker rm pdf2zh-api
docker run -d -p 8000:8000 ghcr.io/YOUR_USERNAME/pdf2zh-api:latest
```

---

## 📚 更多信息

- 详细部署文档: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- API 使用文档: [docs/FASTAPI.md](docs/FASTAPI.md)
- 快速开始: [FASTAPI_QUICKSTART.md](FASTAPI_QUICKSTART.md)

---

## 🎯 测试翻译

```bash
# 下载测试 PDF
curl -o test.pdf https://example.com/sample.pdf

# 翻译
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@test.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=google" \
  --output translated.pdf

# 打开翻译后的文件
# translated.pdf
```

---

## 💡 提示

- **端口占用**: 如果 8000 端口被占用，使用 `-p 9000:8000` 更换端口
- **内存限制**: 大文件翻译可能需要增加容器内存限制
- **GPU 支持**: 目前不需要 GPU，CPU 即可运行
- **持久化**: 使用 volume 挂载 `/root/.cache/pdf2zh` 以缓存翻译结果

---

## ⚙️ GitHub Actions 自动构建

推送代码到 GitHub 后，Actions 会自动构建 Docker 镜像并发布到 GHCR。

查看构建状态: [Actions](https://github.com/YOUR_USERNAME/PDFMathTranslate/actions)

---

## 🐳 Docker Hub 发布（可选）

```bash
# 登录 Docker Hub
docker login

# 构建并推送
docker build -f Dockerfile.fastapi -t YOUR_USERNAME/pdf2zh-api:latest .
docker push YOUR_USERNAME/pdf2zh-api:latest

# 使用
docker pull YOUR_USERNAME/pdf2zh-api:latest
docker run -d -p 8000:8000 YOUR_USERNAME/pdf2zh-api:latest
```
