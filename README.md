# PDFMathTranslate FastAPI

基于 [Byaidu/PDFMathTranslate](https://github.com/Byaidu/PDFMathTranslate) 改造的 FastAPI REST API 版本，用于科学文献PDF翻译，保留公式、图表和排版。

## 项目特点

- 🚀 **RESTful API**: 提供标准的HTTP API接口，易于集成
- 📊 **保留排版**: 翻译后保留原文的公式、图表、目录和批注
- 🌐 **多种翻译服务**: 支持Google、OpenAI、DeepL、Ollama等20+翻译服务
- 🐳 **Docker部署**: 开箱即用的Docker镜像，快速部署
- 🔄 **双语输出**: 支持纯翻译版和双语对照版PDF输出
- ⚡ **多线程翻译**: 支持并发翻译，提升处理速度
- 💾 **翻译缓存**: 自动缓存翻译结果，避免重复翻译

## 快速开始

### 使用 Docker Compose (推荐)

1. 克隆仓库
```bash
git clone <your-repo-url>
cd PDFMathTranslate-main
```

2. 配置环境变量 (编辑 `docker-compose.fastapi.yml`)
```yaml
services:
  pdf2zh-api:
    environment:
      # OpenAI配置
      - OPENAI_BASE_URL=https://api.openai.com/v1
      - OPENAI_API_KEY=sk-your-api-key-here
      - OPENAI_MODEL=gpt-4o-mini
```

3. 启动服务
```bash
docker-compose -f docker-compose.fastapi.yml up -d
```

4. 访问API文档
```
http://localhost:11200/docs
```

### 使用 Docker

```bash
# 构建镜像
docker build -f Dockerfile.fastapi -t pdf2zh-api .

# 运行容器
docker run -d \
  -p 11200:8000 \
  -e OPENAI_API_KEY=sk-your-key \
  -e OPENAI_BASE_URL=https://api.openai.com/v1 \
  pdf2zh-api
```

## API使用示例

### 翻译PDF (单语版本)

```bash
curl -X POST "http://localhost:11200/translate/mono" \
  -F "file=@document.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=openai" \
  -F "thread=4" \
  --output translated.pdf
```

### 翻译PDF (双语版本)

```bash
curl -X POST "http://localhost:11200/translate/dual" \
  -F "file=@document.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=openai:gpt-4o-mini" \
  -F "thread=4" \
  --output translated-dual.pdf
```

### Python调用示例

```python
import requests

url = "http://localhost:11200/translate/mono"
files = {"file": open("document.pdf", "rb")}
data = {
    "lang_in": "en",
    "lang_out": "zh",
    "service": "openai",
    "thread": 4
}

response = requests.post(url, files=files, data=data)
with open("translated.pdf", "wb") as f:
    f.write(response.content)
```

## 支持的翻译服务

| 服务商 | service参数 | 所需环境变量 | 说明 |
|--------|------------|--------------|------|
| **Google** | `google` | 无需配置 | 免费，无需API Key |
| **Bing** | `bing` | 无需配置 | 免费，无需API Key |
| **OpenAI** | `openai` | `OPENAI_API_KEY`<br>`OPENAI_BASE_URL`<br>`OPENAI_MODEL` | 支持GPT-4、GPT-3.5等 |
| **DeepL** | `deepl` | `DEEPL_AUTH_KEY` | 专业翻译服务 |
| **DeepLX** | `deeplx` | `DEEPLX_ENDPOINT` | DeepL API代理 |
| **Ollama** | `ollama` | `OLLAMA_HOST`<br>`OLLAMA_MODEL` | 本地大模型 |
| **Gemini** | `gemini` | `GEMINI_API_KEY`<br>`GEMINI_MODEL` | Google AI |
| **Azure OpenAI** | `azure-openai` | `AZURE_OPENAI_BASE_URL`<br>`AZURE_OPENAI_API_KEY` | Azure托管的OpenAI |
| **智谱AI** | `zhipu` | `ZHIPU_API_KEY`<br>`ZHIPU_MODEL` | 国内服务商 |
| **DeepSeek** | `deepseek` | `DEEPSEEK_API_KEY`<br>`DEEPSEEK_MODEL` | 国内服务商 |
| **硅基流动** | `silicon` | `SILICON_API_KEY`<br>`SILICON_MODEL` | 国内服务商 |
| **阿里通义千问** | `qwen-mt` | `ALI_API_KEY`<br>`ALI_MODEL` | 阿里翻译专用模型 |
| **Groq** | `groq` | `GROQ_API_KEY`<br>`GROQ_MODEL` | 高速推理服务 |
| **OpenAI兼容** | `openailiked` | `OPENAILIKED_BASE_URL`<br>`OPENAILIKED_API_KEY`<br>`OPENAILIKED_MODEL` | 任何兼容OpenAI API的服务 |

更多服务请访问 `/services` 端点查看完整列表。

## 支持的语言

| 语言 | 代码 | 语言 | 代码 |
|------|------|------|------|
| 中文 | `zh` | 英语 | `en` |
| 日语 | `ja` | 韩语 | `ko` |
| 西班牙语 | `es` | 法语 | `fr` |
| 德语 | `de` | 俄语 | `ru` |
| 葡萄牙语 | `pt` | 意大利语 | `it` |
| 阿拉伯语 | `ar` | 印地语 | `hi` |
| 泰语 | `th` | 越南语 | `vi` |
| 印尼语 | `id` | 土耳其语 | `tr` |

完整语言列表请访问 `/languages` 端点。

## 配置说明

### 方式1: Docker Compose 环境变量 (推荐)

编辑 `docker-compose.fastapi.yml`:

```yaml
services:
  pdf2zh-api:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    container_name: pdf2zh-fastapi
    ports:
      - "11200:8000"
    environment:
      # ============ OpenAI 官方 API ============
      - OPENAI_BASE_URL=https://api.openai.com/v1
      - OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
      - OPENAI_MODEL=gpt-4o-mini

      # ============ OpenAI 兼容服务(国内中转) ============
      # - OPENAI_BASE_URL=https://api.your-proxy.com/v1
      # - OPENAI_API_KEY=sk-xxxxxxxxxxxxx
      # - OPENAI_MODEL=gpt-4o-mini

      # ============ DeepSeek (国内推荐) ============
      # - DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
      # - DEEPSEEK_MODEL=deepseek-chat

      # ============ 本地 Ollama ============
      # - OLLAMA_HOST=http://host.docker.internal:11434
      # - OLLAMA_MODEL=qwen2.5:7b

      # ============ 通用 OpenAI 兼容服务 ============
      # - OPENAILIKED_BASE_URL=https://any-api.com/v1
      # - OPENAILIKED_API_KEY=your-key
      # - OPENAILIKED_MODEL=model-name
    volumes:
      - pdf2zh-cache:/root/.cache/pdf2zh
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  pdf2zh-cache:
    driver: local
```

启动服务:
```bash
docker-compose -f docker-compose.fastapi.yml up -d
```

查看日志:
```bash
docker-compose -f docker-compose.fastapi.yml logs -f
```

### 方式2: 挂载配置文件

创建 `config.json`:

```json
{
    "translators": [
        {
            "name": "openai",
            "envs": {
                "OPENAI_BASE_URL": "https://api.openai.com/v1",
                "OPENAI_API_KEY": "sk-your-api-key",
                "OPENAI_MODEL": "gpt-4o-mini"
            }
        },
        {
            "name": "deepseek",
            "envs": {
                "DEEPSEEK_API_KEY": "sk-your-deepseek-key",
                "DEEPSEEK_MODEL": "deepseek-chat"
            }
        }
    ]
}
```

修改 `docker-compose.fastapi.yml`:

```yaml
services:
  pdf2zh-api:
    volumes:
      - ./config.json:/root/.config/PDFMathTranslate/config.json:ro
      - pdf2zh-cache:/root/.cache/pdf2zh
```

### 方式3: Docker Run 直接指定

```bash
docker run -d \
  --name pdf2zh-api \
  -p 11200:8000 \
  -e OPENAI_API_KEY=sk-your-key \
  -e OPENAI_BASE_URL=https://api.openai.com/v1 \
  -e OPENAI_MODEL=gpt-4o-mini \
  -v pdf2zh-cache:/root/.cache/pdf2zh \
  --restart unless-stopped \
  pdf2zh-api:latest
```

## 常见配置场景

### 场景1: 使用国内OpenAI中转服务

```yaml
environment:
  - OPENAI_BASE_URL=https://api.chatanywhere.tech/v1
  - OPENAI_API_KEY=sk-xxxxxxxxxxxxx
  - OPENAI_MODEL=gpt-4o-mini
```

调用:
```bash
curl -X POST "http://localhost:11200/translate/mono" \
  -F "file=@test.pdf" \
  -F "service=openai"
```

### 场景2: 使用DeepSeek (国内推荐)

```yaml
environment:
  - DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
  - DEEPSEEK_MODEL=deepseek-chat
```

调用:
```bash
curl -X POST "http://localhost:11200/translate/mono" \
  -F "file=@test.pdf" \
  -F "service=deepseek"
```

### 场景3: 使用本地Ollama

```yaml
environment:
  - OLLAMA_HOST=http://host.docker.internal:11434
  - OLLAMA_MODEL=qwen2.5:7b
```

调用:
```bash
curl -X POST "http://localhost:11200/translate/mono" \
  -F "file=@test.pdf" \
  -F "service=ollama"
```

### 场景4: 配置多个服务同时使用

使用配置文件方式，可以同时配置多个服务:

```json
{
    "translators": [
        {
            "name": "openai",
            "envs": {
                "OPENAI_API_KEY": "sk-xxx",
                "OPENAI_MODEL": "gpt-4o-mini"
            }
        },
        {
            "name": "deepseek",
            "envs": {
                "DEEPSEEK_API_KEY": "sk-yyy",
                "DEEPSEEK_MODEL": "deepseek-chat"
            }
        }
    ]
}
```

调用时通过 `service` 参数切换:
```bash
# 使用OpenAI
-F "service=openai"

# 使用DeepSeek
-F "service=deepseek"
```

## API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 健康检查 |
| `/health` | GET | 健康状态 |
| `/docs` | GET | Swagger API文档 |
| `/redoc` | GET | ReDoc API文档 |
| `/services` | GET | 支持的翻译服务列表 |
| `/languages` | GET | 支持的语言列表 |
| `/translate/mono` | POST | 翻译PDF并返回单语版本 |
| `/translate/dual` | POST | 翻译PDF并返回双语版本 |
| `/translate` | POST | 翻译PDF并返回JSON(含base64) |

## 高级用法

### 指定翻译模型

```bash
curl -X POST "http://localhost:11200/translate/mono" \
  -F "file=@test.pdf" \
  -F "service=openai:gpt-4o"
```

### 调整并发线程数

```bash
curl -X POST "http://localhost:11200/translate/mono" \
  -F "file=@test.pdf" \
  -F "service=openai" \
  -F "thread=8"
```

### 健康检查

```bash
curl http://localhost:11200/health
```

## 性能优化

1. **使用缓存**: 自动缓存翻译结果，重复内容不会重新翻译
2. **调整线程数**: 根据服务器性能调整 `thread` 参数(1-16)
3. **持久化缓存**: 挂载 `/root/.cache/pdf2zh` 目录

```yaml
volumes:
  - pdf2zh-cache:/root/.cache/pdf2zh  # 缓存持久化
```

## 故障排查

### 查看容器日志
```bash
docker-compose -f docker-compose.fastapi.yml logs -f pdf2zh-api
```

### 检查服务状态
```bash
curl http://localhost:11200/health
```

### 常见问题

1. **API Key错误**: 检查环境变量配置是否正确
2. **连接超时**: 检查 `OPENAI_BASE_URL` 等URL是否可访问
3. **翻译失败**: 查看容器日志获取详细错误信息

## 技术栈

- **FastAPI**: 现代、高性能的Python Web框架
- **PyMuPDF**: PDF处理库
- **PDFMiner**: PDF解析引擎
- **DocLayout-YOLO**: 文档布局检测
- **OpenAI SDK**: 多种LLM服务集成

## 致谢

本项目基于 [Byaidu/PDFMathTranslate](https://github.com/Byaidu/PDFMathTranslate) 改造而来，在原项目的基础上增加了FastAPI接口支持，特此感谢原作者的优秀工作！

如果本项目对您有帮助，也请给原项目 [PDFMathTranslate](https://github.com/Byaidu/PDFMathTranslate) 一个 Star ⭐

## License

本项目继承原项目的开源协议。
