# PDFMathTranslate Docker 部署指南

> 专业的科学PDF文档翻译工具 - Docker容器化部署完整文档

[![Docker Image](https://img.shields.io/docker/pulls/byaidu/pdf2zh)](https://hub.docker.com/r/byaidu/pdf2zh)
[![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%7C3.11%7C3.12-blue.svg)](https://www.python.org/)

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [部署方式](#部署方式)
  - [方式一：GUI Web界面（推荐）](#方式一gui-web界面推荐)
  - [方式二：FastAPI REST API](#方式二fastapi-rest-api)
  - [方式三：GUI + API 组合部署](#方式三gui--api-组合部署)
- [API使用说明](#api使用说明)
- [配置说明](#配置说明)
- [常见问题与解决方案](#常见问题与解决方案)
- [性能优化建议](#性能优化建议)
- [故障排查](#故障排查)

---

## 项目简介

**PDFMathTranslate (pdf2zh)** 是一个开源的科学PDF文档翻译工具，专门用于翻译包含数学公式、表格、图表的学术论文和技术文档。

**核心优势：**
- 保留PDF原始排版和格式
- 数学公式完美保持不变
- 支持16种语言互译
- 支持20+种翻译服务（Google、OpenAI、DeepL等）
- 提供单语/双语对照翻译

**项目信息：**
- 版本：v1.9.11
- Python要求：3.10 <= version < 3.14
- 许可证：AGPL-3.0
- 官方仓库：https://github.com/Byaidu/PDFMathTranslate

---

## 功能特性

### 支持的翻译服务

**免费服务：**
```
google, bing, deepl, deeplx, ollama, argos
```

**付费云服务：**
```
azure, tencent, deepseek, azure-openai
```

**LLM服务：**
```
openai, gemini, zhipu, silicon, groq, grok, moonshot,
qwen, anthropic, dify, anythingllm, modelscope, xinference
```

### 支持的语言（16种）

| 代码 | 语言 | 代码 | 语言 |
|------|------|------|------|
| `zh` | 中文 | `en` | English |
| `ja` | 日本語 | `ko` | 한국어 |
| `es` | Español | `fr` | Français |
| `de` | Deutsch | `ru` | Русский |
| `pt` | Português | `it` | Italiano |
| `ar` | العربية | `hi` | हिन्दी |
| `th` | ไทย | `vi` | Tiếng Việt |
| `id` | Indonesia | `tr` | Türkçe |

### 输出格式

- **单语版本（Mono）**：原文替换为译文
- **双语版本（Dual）**：原文和译文对照显示

---

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+ (可选)
- 至少 4GB 可用内存
- 至少 5GB 可用磁盘空间

### 快速部署（30秒启动）

**GUI模式（推荐新手）：**
```bash
docker pull byaidu/pdf2zh
docker run -d -p 7860:7860 --name pdf2zh byaidu/pdf2zh
```

访问：http://localhost:7860

**API模式（推荐开发者）：**
```bash
git clone https://github.com/Byaidu/PDFMathTranslate.git
cd PDFMathTranslate
docker-compose -f docker-compose.fastapi.yml up -d
```

访问：http://localhost:8000/docs

---

## 部署方式

### 方式一：GUI Web界面（推荐）

#### 1.1 使用预构建镜像

```bash
# 拉取最新镜像（Docker Hub）
docker pull byaidu/pdf2zh

# 或使用 GitHub Container Registry（推荐国内用户）
docker pull ghcr.io/byaidu/pdfmathtranslate

# 启动容器
docker run -d \
  --name pdf2zh-gui \
  -p 7860:7860 \
  --restart unless-stopped \
  -v pdf2zh-cache:/root/.cache/pdf2zh \
  byaidu/pdf2zh
```

#### 1.2 使用 docker-compose（推荐）

```bash
# 下载项目
git clone https://github.com/Byaidu/PDFMathTranslate.git
cd PDFMathTranslate

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

#### 1.3 自定义构建

```bash
# 构建镜像
docker build -t pdf2zh-custom -f Dockerfile .

# 运行容器
docker run -d -p 7860:7860 --name pdf2zh pdf2zh-custom
```

**访问地址：** http://localhost:7860

---

### 方式二：FastAPI REST API

#### 2.1 快速启动（docker-compose）

```bash
# 启动 FastAPI 服务
docker-compose -f docker-compose.fastapi.yml up -d

# 查看服务状态
docker-compose -f docker-compose.fastapi.yml ps

# 查看实时日志
docker-compose -f docker-compose.fastapi.yml logs -f pdf2zh-api
```

#### 2.2 使用 Docker 命令

```bash
# 构建镜像
docker build -t pdf2zh-api -f Dockerfile.fastapi .

# 运行容器
docker run -d \
  --name pdf2zh-api \
  -p 8000:8000 \
  --restart unless-stopped \
  -v pdf2zh-cache:/root/.cache/pdf2zh \
  -v $(pwd)/config.json:/root/.config/PDFMathTranslate/config.json:ro \
  pdf2zh-api
```

#### 2.3 配置 API 密钥（环境变量方式）

创建 `.env` 文件：

```bash
# .env
OPENAI_API_KEY=sk-your-openai-api-key
DEEPL_AUTH_KEY=your-deepl-auth-key
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
```

修改 `docker-compose.fastapi.yml`：

```yaml
services:
  pdf2zh-api:
    # ...
    env_file:
      - .env
    environment:
      - PYTHONUNBUFFERED=1
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEEPL_AUTH_KEY=${DEEPL_AUTH_KEY}
```

#### 2.4 API文档访问

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

---

### 方式三：GUI + API 组合部署

同时启动Web界面和API服务：

```bash
# 启动 API + GUI
docker-compose -f docker-compose.fastapi.yml --profile gui up -d

# 验证服务
curl http://localhost:8000/health  # API健康检查
curl http://localhost:7860         # GUI访问
```

**服务端口：**
- GUI: http://localhost:7860
- API: http://localhost:8000

---

## API使用说明

### API端点列表

| 端点 | 方法 | 功能 | 返回格式 |
|------|------|------|----------|
| `/` | GET | 根路径健康检查 | JSON |
| `/health` | GET | 健康检查 | JSON |
| `/services` | GET | 获取支持的翻译服务 | JSON |
| `/languages` | GET | 获取支持的语言 | JSON |
| `/translate/mono` | POST | 翻译PDF（单语版） | PDF文件 |
| `/translate/dual` | POST | 翻译PDF（双语版） | PDF文件 |
| `/translate` | POST | 翻译PDF（返回JSON含base64） | JSON |

### 示例1：健康检查

```bash
curl http://localhost:8000/health
```

**响应：**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "PDFMathTranslate API"
}
```

### 示例2：获取支持的服务

```bash
curl http://localhost:8000/services
```

**响应：**
```json
{
  "services": [
    "google", "bing", "deepl", "deeplx", "deepseek",
    "ollama", "openai", "azure-openai", "gemini",
    "zhipu", "silicon", "groq", "grok", "moonshot",
    "qwen", "tencent", "azure", "dify", "anythingllm",
    "modelscope", "xinference", "anthropic", "argos"
  ]
}
```

### 示例3：翻译PDF（单语版）

```bash
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@example.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=google" \
  -F "thread=4" \
  --output translated.pdf
```

**参数说明：**
- `file`: PDF文件（必需）
- `lang_in`: 源语言，默认 `en`
- `lang_out`: 目标语言，默认 `zh`
- `service`: 翻译服务，默认 `google`
- `thread`: 并发线程数（1-16），默认 `4`
- `model`: LLM模型名（可选，用于OpenAI等）
- `callback`: 自定义提示词（可选）

### 示例4：翻译PDF（双语版）

```bash
curl -X POST http://localhost:8000/translate/dual \
  -F "file=@research_paper.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=openai" \
  -F "model=gpt-4o-mini" \
  --output paper_dual.pdf
```

### 示例5：使用Python调用API

```python
import requests

# 翻译PDF（单语版）
with open('example.pdf', 'rb') as f:
    files = {'file': f}
    data = {
        'lang_in': 'en',
        'lang_out': 'zh',
        'service': 'google',
        'thread': 4
    }

    response = requests.post(
        'http://localhost:8000/translate/mono',
        files=files,
        data=data
    )

    if response.status_code == 200:
        with open('output.pdf', 'wb') as out:
            out.write(response.content)
        print("翻译成功！")
    else:
        print(f"错误: {response.json()}")
```

### 示例6：批量翻译脚本

```python
import requests
import os
from pathlib import Path

def translate_pdf(input_file, output_file, service='google', lang_out='zh'):
    """翻译单个PDF文件"""
    url = 'http://localhost:8000/translate/mono'

    with open(input_file, 'rb') as f:
        files = {'file': f}
        data = {
            'lang_in': 'en',
            'lang_out': lang_out,
            'service': service,
            'thread': 8
        }

        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            with open(output_file, 'wb') as out:
                out.write(response.content)
            return True
        else:
            print(f"翻译失败: {response.json()}")
            return False

# 批量翻译目录下所有PDF
input_dir = Path('pdfs')
output_dir = Path('translated')
output_dir.mkdir(exist_ok=True)

for pdf_file in input_dir.glob('*.pdf'):
    output_file = output_dir / f"{pdf_file.stem}_zh.pdf"
    print(f"翻译: {pdf_file.name}")

    if translate_pdf(pdf_file, output_file):
        print(f"  ✓ 完成: {output_file.name}")
    else:
        print(f"  ✗ 失败: {pdf_file.name}")
```

---

## 配置说明

### 配置文件位置

容器内配置文件路径：`/root/.config/PDFMathTranslate/config.json`

### 创建配置文件

创建 `config.json`：

```json
{
  "openai": {
    "api_key": "sk-your-openai-api-key",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4o-mini"
  },
  "deepl": {
    "auth_key": "your-deepl-auth-key"
  },
  "azure-openai": {
    "api_key": "your-azure-key",
    "endpoint": "https://your-resource.openai.azure.com",
    "api_version": "2024-02-15-preview",
    "deployment_name": "gpt-4"
  },
  "gemini": {
    "api_key": "your-gemini-api-key"
  },
  "zhipu": {
    "api_key": "your-zhipu-api-key"
  }
}
```

### 挂载配置文件

**方法1：Docker命令挂载**

```bash
docker run -d \
  --name pdf2zh-api \
  -p 8000:8000 \
  -v $(pwd)/config.json:/root/.config/PDFMathTranslate/config.json:ro \
  -v pdf2zh-cache:/root/.cache/pdf2zh \
  pdf2zh-api
```

**方法2：docker-compose挂载**

修改 `docker-compose.fastapi.yml`：

```yaml
services:
  pdf2zh-api:
    volumes:
      - ./config.json:/root/.config/PDFMathTranslate/config.json:ro
      - pdf2zh-cache:/root/.cache/pdf2zh
```

### 使用环境变量（推荐）

无需配置文件，直接传递环境变量：

```bash
docker run -d \
  --name pdf2zh-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-your-key \
  -e DEEPL_AUTH_KEY=your-key \
  pdf2zh-api
```

---

## 常见问题与解决方案

### 问题1：国内网络无法拉取镜像

**问题现象：**
```
Error response from daemon: Get "https://ghcr.io/v2/": dial tcp: i/o timeout
```

**解决方案：**

**方案A：使用阿里云镜像（推荐）**

```bash
# 使用 Dockerfile.fastapi（已配置阿里云源）
docker build -t pdf2zh-api -f Dockerfile.fastapi .
```

**方案B：配置Docker镜像加速器**

编辑 `/etc/docker/daemon.json`（Linux）或 Docker Desktop设置（Windows/Mac）：

```json
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
```

重启Docker：
```bash
sudo systemctl restart docker
```

**方案C：使用代理**

```bash
docker build -t pdf2zh-api \
  --build-arg HTTP_PROXY=http://127.0.0.1:7890 \
  --build-arg HTTPS_PROXY=http://127.0.0.1:7890 \
  -f Dockerfile.fastapi .
```

### 问题2：模型下载失败（babeldoc、ONNX模型）

**问题现象：**
```
Error downloading model from huggingface.co
```

**解决方案：**

**方案A：使用HuggingFace镜像站**

```bash
docker run -d \
  --name pdf2zh-api \
  -p 8000:8000 \
  -e HF_ENDPOINT=https://hf-mirror.com \
  pdf2zh-api
```

**方案B：预下载模型并挂载**

```bash
# 1. 在宿主机预下载模型
mkdir -p models
# 手动下载模型文件到 models/ 目录

# 2. 挂载模型目录
docker run -d \
  --name pdf2zh-api \
  -p 8000:8000 \
  -v $(pwd)/models:/root/.cache/huggingface \
  pdf2zh-api
```

### 问题3：API密钥未生效

**问题现象：**
```json
{
  "error": "Translation failed",
  "detail": "API key not configured"
}
```

**解决方案：**

**检查配置是否正确挂载：**

```bash
# 进入容器检查
docker exec -it pdf2zh-api bash
cat /root/.config/PDFMathTranslate/config.json

# 检查环境变量
docker exec -it pdf2zh-api env | grep API
```

**确保文件权限正确：**

```bash
chmod 644 config.json
```

### 问题4：健康检查失败

**问题现象：**
```
Health check failed: Connection refused
```

**解决方案：**

**检查服务是否启动：**

```bash
docker logs pdf2zh-api

# 应该看到类似输出：
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**手动测试健康检查：**

```bash
docker exec -it pdf2zh-api curl http://localhost:8000/health
```

**增加启动等待时间：**

修改 `docker-compose.fastapi.yml` 的 `start_period`：

```yaml
healthcheck:
  start_period: 120s  # 增加到120秒
```

### 问题5：翻译速度慢或超时

**问题现象：**
```
Translation takes too long or timeout
```

**解决方案：**

**增加线程数（API参数）：**

```bash
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@large.pdf" \
  -F "thread=16" \  # 增加到最大值
  --output output.pdf
```

**增加容器资源限制：**

```yaml
services:
  pdf2zh-api:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 2G
```

**使用更快的翻译服务：**

- 免费服务速度：`google` > `bing` > `deepl`
- 付费服务速度：`openai` (gpt-4o-mini) > `deepl-pro` > `azure`

### 问题6：PDF翻译后格式错乱

**问题现象：**
翻译后的PDF排版混乱，文字重叠

**解决方案：**

**检查源PDF质量：**
- 确保源PDF不是扫描版（需要是文字版）
- 使用 `pdfminer.six` 测试PDF文本提取

**使用双语版本查看：**

```bash
# 双语版本可以更好地保留原始布局
curl -X POST http://localhost:8000/translate/dual \
  -F "file=@example.pdf" \
  --output output_dual.pdf
```

**调整翻译模型（使用更好的LLM）：**

```bash
# 使用GPT-4o-mini（格式保留更好）
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@example.pdf" \
  -F "service=openai" \
  -F "model=gpt-4o-mini" \
  --output output.pdf
```

### 问题7：容器启动失败

**问题现象：**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**解决方案：**

**端口被占用，更换端口：**

```bash
# 更换为其他端口
docker run -d -p 8888:8000 --name pdf2zh-api pdf2zh-api
```

**或停止占用端口的服务：**

```bash
# 查找占用8000端口的进程
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# 停止进程
kill -9 <PID>
```

---

## 性能优化建议

### 1. 启用缓存（提升重复翻译速度）

挂载缓存volume：

```yaml
volumes:
  - pdf2zh-cache:/root/.cache/pdf2zh
```

缓存效果：
- 首次翻译：30秒
- 重复翻译：<5秒（从缓存读取）

### 2. 增加并发线程

**API调用时设置：**

```bash
# 小文件：thread=4（默认）
# 中等文件：thread=8
# 大文件：thread=16（最大）
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@large.pdf" \
  -F "thread=16"
```

**注意：** 线程数过高可能导致翻译服务限流（如Google限制QPS）

### 3. 选择合适的翻译服务

**速度优先：**
```
google > bing > deepl（免费）
openai (gpt-4o-mini) > gemini（付费）
```

**质量优先：**
```
gpt-4o > claude-3.5-sonnet > deepl-pro > google
```

**成本优先：**
```
google/bing（免费）> deepseek > moonshot > openai
```

### 4. 资源限制配置

```yaml
services:
  pdf2zh-api:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 4G
        reservations:
          cpus: '2.0'
          memory: 2G
    restart: unless-stopped
```

### 5. 网络优化（国内用户）

**配置 HuggingFace 镜像：**

```bash
docker run -d \
  -e HF_ENDPOINT=https://hf-mirror.com \
  -e TRANSFORMERS_OFFLINE=0 \
  pdf2zh-api
```

**使用国内翻译服务：**
- 腾讯翻译君：`tencent`
- 阿里翻译：`azure` (Azure中国区)
- 百度翻译：需自行接入

---

## 故障排查

### 查看日志

```bash
# Docker Compose
docker-compose -f docker-compose.fastapi.yml logs -f pdf2zh-api

# Docker
docker logs -f pdf2zh-api

# 查看最近100行
docker logs --tail 100 pdf2zh-api
```

### 进入容器调试

```bash
# 进入容器
docker exec -it pdf2zh-api bash

# 检查Python环境
python --version
pip list | grep pdf2zh

# 测试翻译核心功能
python -c "from pdf2zh import translate_stream; print('Import OK')"

# 测试API服务
curl http://localhost:8000/health
```

### 检查资源使用

```bash
# 查看容器资源占用
docker stats pdf2zh-api

# 输出示例：
# CONTAINER       CPU %    MEM USAGE / LIMIT     MEM %
# pdf2zh-api      15.2%    1.2GiB / 4GiB        30%
```

### 重置容器

```bash
# 停止并删除容器
docker-compose -f docker-compose.fastapi.yml down

# 删除缓存（可选）
docker volume rm pdf2zh-cache

# 重新构建并启动
docker-compose -f docker-compose.fastapi.yml up --build -d
```

---

## 部署问题分析总结

### 已知问题

| 问题 | 严重性 | 状态 | 解决方案 |
|------|--------|------|----------|
| 国内网络拉取镜像慢 | 中 | ✅ 已解决 | 使用Dockerfile.fastapi（阿里云源） |
| HuggingFace模型下载被墙 | 高 | ✅ 已解决 | 设置HF_ENDPOINT镜像 |
| API密钥配置不便 | 低 | ✅ 已解决 | 支持环境变量 |
| 缓存未持久化 | 中 | ✅ 已解决 | docker-compose配置volume |
| 健康检查依赖curl | 低 | ✅ 已解决 | Dockerfile已安装curl |

### API功能验证

**验证项：**
- [x] `/health` 健康检查端点可用
- [x] `/services` 返回完整服务列表
- [x] `/translate/mono` 单语翻译功能正常
- [x] `/translate/dual` 双语翻译功能正常
- [x] 支持多线程并发翻译（1-16线程）
- [x] CORS已启用，支持跨域请求
- [x] 参数验证完善（语言、服务、文件类型）
- [x] 错误处理完善（HTTPException处理）

**结论：** ✅ **Docker部署后API可以正常使用，PDF翻译功能完整可用**

---

## 生产环境部署建议

### 1. 使用反向代理（Nginx）

**Nginx配置示例：**

```nginx
server {
    listen 80;
    server_name pdf-translate.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # 增加超时时间（翻译可能需要较长时间）
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;

        # 增加上传文件大小限制
        client_max_body_size 100M;
    }
}
```

### 2. 配置HTTPS（Let's Encrypt）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d pdf-translate.example.com

# 自动续期
sudo certbot renew --dry-run
```

### 3. 监控和日志

**使用 Prometheus + Grafana 监控：**

```yaml
services:
  pdf2zh-api:
    labels:
      - "prometheus.io/scrape=true"
      - "prometheus.io/port=8000"
```

**日志聚合（ELK）：**

```yaml
services:
  pdf2zh-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 4. 高可用部署

**使用 Docker Swarm 或 Kubernetes：**

```yaml
# docker-compose.yml (Swarm模式)
version: "3.8"
services:
  pdf2zh-api:
    image: pdf2zh-api
    deploy:
      replicas: 3  # 3个副本
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
```

---

## 许可证

本项目采用 AGPL-3.0 许可证，详见 [LICENSE](LICENSE) 文件。

使用本项目时，请遵守以下约定：
- 商业使用需开源代码
- 网络服务形式使用需提供源码
- 修改后的代码必须开源

---

## 支持与社区

- **GitHub Issues**: https://github.com/Byaidu/PDFMathTranslate/issues
- **官方文档**: https://github.com/Byaidu/PDFMathTranslate/tree/main/docs
- **Email**: byaidux@gmail.com

---

## 更新日志

### v1.9.11 (2025-01)
- ✅ 优化FastAPI服务器性能
- ✅ 增加健康检查端点
- ✅ 改进Docker镜像构建
- ✅ 修复国内网络访问问题
- ✅ 增加更多翻译服务支持

---

## 致谢

感谢以下开源项目：
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF处理
- [FastAPI](https://github.com/tiangolo/fastapi) - Web框架
- [Gradio](https://github.com/gradio-app/gradio) - GUI框架
- [BabelDoc](https://github.com/jaaack-wang/BabelDoc) - 文档翻译后端

---

**部署愉快！如有问题欢迎提Issue。**
