# FastAPI REST API 使用指南

## 概述

这是一个基于 FastAPI 的轻量级 REST API 服务，用于 PDF 科学文献翻译。相比原有的 Flask+Celery+Redis 方案，此方案更加简单易用，无需额外依赖，适合小规模部署和快速集成。

### 特点

- ✅ **轻量级**: 无需 Redis 和 Celery
- ✅ **简单部署**: 一条命令启动
- ✅ **自动文档**: 内置 Swagger UI 和 ReDoc
- ✅ **同步处理**: 适合小文件快速翻译
- ✅ **RESTful**: 标准的 REST API 设计

### 适用场景

- PDF 文件 < 10MB
- 翻译时间 < 30秒
- 小规模使用（单机部署）
- 快速集成到其他应用

---

## 安装

### 1. 安装依赖

```bash
# 基础安装
pip install pdf2zh

# 安装 FastAPI 相关依赖
pip install fastapi uvicorn python-multipart
```

或者使用 `pnpm`（Windows 环境推荐）:

```bash
pip install fastapi uvicorn python-multipart
```

### 2. 验证安装

```bash
pdf2zh --version
```

---

## 启动服务

### 基础启动

```bash
pdf2zh --fastapi
```

默认端口: `8000`

### 自定义端口

```bash
pdf2zh --fastapi --apiport 9000
```

### 启动成功提示

```
INFO:     Starting FastAPI server on http://0.0.0.0:8000
INFO:     API documentation available at http://localhost:8000/docs
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## API 文档

### 在线文档

启动服务后，访问以下地址查看交互式文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API 端点列表

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 根路径，健康检查 |
| `/health` | GET | 健康检查 |
| `/services` | GET | 获取支持的翻译服务列表 |
| `/languages` | GET | 获取支持的语言列表 |
| `/translate/mono` | POST | 翻译并返回单语版本 |
| `/translate/dual` | POST | 翻译并返回双语版本 |
| `/translate` | POST | 翻译并返回JSON（含base64） |

---

## 使用示例

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

**响应:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "PDFMathTranslate API"
}
```

### 2. 获取支持的翻译服务

```bash
curl http://localhost:8000/services
```

**响应:**
```json
{
  "services": [
    "google", "bing", "deepl", "deeplx", "deepseek",
    "ollama", "openai", "azure-openai", "gemini",
    "zhipu", "silicon", "groq", "grok", "moonshot"
  ]
}
```

### 3. 翻译 PDF（单语版本）

#### 使用 Google 翻译（默认，免费）

```bash
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@example.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=google" \
  --output example-zh.pdf
```

#### 使用 OpenAI GPT-4

```bash
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@paper.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=openai" \
  -F "model=gpt-4o-mini" \
  -F "thread=8" \
  --output paper-zh.pdf
```

**注意**: OpenAI 需要配置 API Key，参见[配置章节](#配置翻译服务)

### 4. 翻译 PDF（双语版本）

```bash
curl -X POST http://localhost:8000/translate/dual \
  -F "file=@example.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=google" \
  --output example-dual-zh.pdf
```

**双语版本**: 保留原文并在下方显示翻译

### 5. 获取 JSON 响应（含 Base64）

```bash
curl -X POST http://localhost:8000/translate \
  -F "file=@example.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=google"
```

**响应:**
```json
{
  "status": "success",
  "message": "Translation completed successfully",
  "original_filename": "example.pdf",
  "mono_filename": "example-zh.pdf",
  "dual_filename": "example-dual-zh.pdf",
  "mono_size_bytes": 245678,
  "dual_size_bytes": 489012,
  "mono_base64": "JVBERi0xLjQKJeLjz9MK...",
  "dual_base64": "JVBERi0xLjQKJeLjz9MK...",
  "note": "Use /translate/mono or /translate/dual endpoints to download PDF directly"
}
```

---

## 参数说明

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `file` | File | ✅ | - | PDF 文件 |
| `lang_in` | String | ❌ | `en` | 源语言代码 |
| `lang_out` | String | ❌ | `zh` | 目标语言代码 |
| `service` | String | ❌ | `google` | 翻译服务 |
| `model` | String | ❌ | - | 模型名称（LLM服务） |
| `thread` | Integer | ❌ | `4` | 并发线程数（1-16） |
| `callback` | String | ❌ | - | 自定义提示词模板 |

### 语言代码

支持的语言代码（ISO 639-1）:

| 代码 | 语言 | 代码 | 语言 |
|------|------|------|------|
| `en` | English | `zh` | 中文 |
| `ja` | 日本語 | `ko` | 한국어 |
| `es` | Español | `fr` | Français |
| `de` | Deutsch | `ru` | Русский |
| `pt` | Português | `it` | Italiano |
| `ar` | العربية | `hi` | हिन्दी |
| `th` | ไทย | `vi` | Tiếng Việt |
| `id` | Indonesia | `tr` | Türkçe |

### 翻译服务

#### 免费服务
- `google` - Google 翻译（推荐，无需配置）
- `bing` - Bing 翻译
- `argos` - Argos Translate（本地）

#### 付费云服务
- `deepl` - DeepL
- `deeplx` - DeepL API
- `azure` - Azure Translator
- `tencent` - 腾讯云翻译
- `azure-openai` - Azure OpenAI

#### LLM 服务
- `openai` - OpenAI (GPT-4, GPT-3.5)
- `gemini` - Google Gemini
- `zhipu` - 智谱 AI
- `silicon` - Silicon Flow
- `groq` - Groq
- `grok` - xAI Grok
- `moonshot` - Moonshot AI
- `qwen` - 阿里通义千问
- `deepseek` - DeepSeek
- `anthropic` - Anthropic Claude

#### 本地 LLM
- `ollama` - Ollama（本地部署）
- `xinference` - Xorbits Inference

---

## 配置翻译服务

### 方式1: 环境变量

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.openai.com/v1"

# DeepL
export DEEPL_AUTH_KEY="..."

# Azure OpenAI
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="..."
```

### 方式2: 配置文件

创建配置文件 `~/.config/PDFMathTranslate/config.json`:

```json
{
  "openai": {
    "api_key": "sk-...",
    "base_url": "https://api.openai.com/v1"
  },
  "deepl": {
    "auth_key": "..."
  },
  "azure-openai": {
    "api_key": "...",
    "endpoint": "..."
  }
}
```

### 方式3: 启动时指定配置

```bash
pdf2zh --fastapi --config /path/to/config.json
```

---

## Python 客户端示例

### 使用 requests 库

```python
import requests

# 1. 基础翻译（Google）
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
        with open('example-zh.pdf', 'wb') as out:
            out.write(response.content)
        print("翻译完成!")
    else:
        print(f"翻译失败: {response.json()}")
```

### 使用 httpx (异步)

```python
import httpx
import asyncio

async def translate_pdf(file_path: str, output_path: str):
    async with httpx.AsyncClient(timeout=300.0) as client:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'lang_in': 'en',
                'lang_out': 'zh',
                'service': 'google'
            }
            response = await client.post(
                'http://localhost:8000/translate/mono',
                files=files,
                data=data
            )

            if response.status_code == 200:
                with open(output_path, 'wb') as out:
                    out.write(response.content)
                print("翻译完成!")
            else:
                print(f"翻译失败: {response.json()}")

# 运行
asyncio.run(translate_pdf('example.pdf', 'example-zh.pdf'))
```

### 完整示例（带错误处理）

```python
import requests
from typing import Optional

def translate_pdf(
    file_path: str,
    output_path: str,
    lang_in: str = 'en',
    lang_out: str = 'zh',
    service: str = 'google',
    model: Optional[str] = None,
    thread: int = 4,
    api_url: str = 'http://localhost:8000'
) -> bool:
    """
    翻译 PDF 文件

    Args:
        file_path: 输入 PDF 路径
        output_path: 输出 PDF 路径
        lang_in: 源语言代码
        lang_out: 目标语言代码
        service: 翻译服务
        model: 模型名称（可选）
        thread: 线程数
        api_url: API 地址

    Returns:
        bool: 是否成功
    """
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'application/pdf')}
            data = {
                'lang_in': lang_in,
                'lang_out': lang_out,
                'service': service,
                'thread': thread
            }

            if model:
                data['model'] = model

            print(f"正在翻译 {file_path}...")
            print(f"翻译服务: {service}")
            print(f"源语言: {lang_in} -> 目标语言: {lang_out}")

            response = requests.post(
                f'{api_url}/translate/mono',
                files=files,
                data=data,
                timeout=300  # 5分钟超时
            )

            if response.status_code == 200:
                with open(output_path, 'wb') as out:
                    out.write(response.content)
                print(f"✅ 翻译成功! 输出文件: {output_path}")
                return True
            else:
                error_data = response.json()
                print(f"❌ 翻译失败: {error_data.get('error', '未知错误')}")
                print(f"详情: {error_data.get('detail', '')}")
                return False

    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请稍后重试")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 API 服务器，请检查服务是否启动")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return False

# 使用示例
if __name__ == '__main__':
    # 示例1: 使用 Google 翻译
    translate_pdf('paper.pdf', 'paper-zh.pdf')

    # 示例2: 使用 OpenAI GPT-4
    translate_pdf(
        'paper.pdf',
        'paper-zh-gpt4.pdf',
        service='openai',
        model='gpt-4o-mini',
        thread=8
    )
```

---

## JavaScript/Node.js 示例

### 使用 axios

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function translatePDF(filePath, outputPath, options = {}) {
    const {
        langIn = 'en',
        langOut = 'zh',
        service = 'google',
        model = null,
        thread = 4,
        apiUrl = 'http://localhost:8000'
    } = options;

    try {
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));
        form.append('lang_in', langIn);
        form.append('lang_out', langOut);
        form.append('service', service);
        form.append('thread', thread);

        if (model) {
            form.append('model', model);
        }

        console.log(`正在翻译 ${filePath}...`);

        const response = await axios.post(
            `${apiUrl}/translate/mono`,
            form,
            {
                headers: form.getHeaders(),
                responseType: 'arraybuffer',
                timeout: 300000 // 5分钟
            }
        );

        fs.writeFileSync(outputPath, response.data);
        console.log(`✅ 翻译成功! 输出文件: ${outputPath}`);
        return true;

    } catch (error) {
        if (error.response) {
            console.error('❌ 翻译失败:', error.response.data.toString());
        } else {
            console.error('❌ 发生错误:', error.message);
        }
        return false;
    }
}

// 使用示例
translatePDF('example.pdf', 'example-zh.pdf', {
    langIn: 'en',
    langOut: 'zh',
    service: 'google',
    thread: 4
});
```

### 使用 fetch (Browser/Node 18+)

```javascript
async function translatePDF(file, options = {}) {
    const {
        langIn = 'en',
        langOut = 'zh',
        service = 'google',
        thread = 4
    } = options;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('lang_in', langIn);
    formData.append('lang_out', langOut);
    formData.append('service', service);
    formData.append('thread', thread);

    try {
        const response = await fetch('http://localhost:8000/translate/mono', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }

        const blob = await response.blob();

        // 下载文件
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `translated-${langOut}.pdf`;
        a.click();

        return true;
    } catch (error) {
        console.error('翻译失败:', error);
        return false;
    }
}

// HTML 使用示例
// <input type="file" id="pdfFile" accept=".pdf">
// <button onclick="handleTranslate()">翻译</button>

async function handleTranslate() {
    const fileInput = document.getElementById('pdfFile');
    const file = fileInput.files[0];

    if (!file) {
        alert('请选择 PDF 文件');
        return;
    }

    await translatePDF(file, {
        langIn: 'en',
        langOut: 'zh',
        service: 'google'
    });
}
```

---

## Docker 部署

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
RUN pip install pdf2zh fastapi uvicorn python-multipart

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["pdf2zh", "--fastapi", "--apiport", "8000"]
```

### 构建和运行

```bash
# 构建镜像
docker build -t pdf2zh-api .

# 运行容器
docker run -d -p 8000:8000 pdf2zh-api

# 测试
curl http://localhost:8000/health
```

---

## 性能优化建议

### 1. 调整线程数

```bash
# 增加线程数以提高并发翻译速度（适合多核CPU）
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@large.pdf" \
  -F "thread=16"
```

### 2. 使用缓存

翻译结果会自动缓存到 `~/.cache/pdf2zh/cache.v1.db`，重复翻译相同内容时会直接使用缓存。

### 3. 选择合适的翻译服务

| 服务 | 速度 | 质量 | 成本 | 推荐场景 |
|------|------|------|------|---------|
| Google | ⭐⭐⭐⭐ | ⭐⭐⭐ | 免费 | 日常使用 |
| DeepL | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 付费 | 高质量翻译 |
| OpenAI GPT-4 | ⭐⭐ | ⭐⭐⭐⭐⭐ | 付费 | 学术论文 |
| Ollama | ⭐⭐ | ⭐⭐⭐⭐ | 免费 | 本地部署 |

---

## 故障排查

### 1. 端口被占用

```bash
# 查看端口占用 (Windows)
netstat -ano | findstr :8000

# 更换端口
pdf2zh --fastapi --apiport 9000
```

### 2. 翻译失败

检查日志输出，常见问题：
- API Key 未配置
- 网络连接问题
- PDF 文件损坏
- 不支持的语言或服务

### 3. 内存不足

对于大文件，可能需要增加系统内存或分页翻译：

```bash
# 分页翻译
pdf2zh large.pdf -p 1-10 -o output/
```

---

## API 限制

- **文件大小**: 建议 < 10MB
- **翻译时间**: 建议 < 30秒
- **并发请求**: 默认无限制（建议使用 Nginx 限流）
- **支持格式**: 仅 PDF

---

## 常见问题

### Q1: 如何翻译大文件？

A: 建议使用原有的 Flask+Celery 异步方案，或者分页翻译：

```bash
# 方式1: 异步API
pdf2zh --flask

# 方式2: 分页翻译
pdf2zh large.pdf -p 1-50 -o part1/
pdf2zh large.pdf -p 51-100 -o part2/
```

### Q2: 支持哪些翻译服务？

A: 支持20+种服务，包括 Google、OpenAI、DeepL 等。运行 `curl http://localhost:8000/services` 查看完整列表。

### Q3: 如何自定义提示词？

A: 使用 `callback` 参数传入自定义提示词模板：

```bash
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@paper.pdf" \
  -F "service=openai" \
  -F "callback=请翻译以下学术文本，保持专业术语准确：{text}"
```

### Q4: API 是否支持 HTTPS？

A: FastAPI 本身不直接支持 HTTPS，建议使用 Nginx 反向代理：

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
    }
}
```

---

## 与其他方案对比

| 特性 | FastAPI (轻量版) | Flask+Celery (重量版) |
|------|------------------|----------------------|
| 部署难度 | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| 外部依赖 | 无 | Redis |
| 适用文件大小 | < 10MB | 无限制 |
| 异步支持 | ❌ | ✅ |
| 进度查询 | ❌ | ✅ |
| 任务队列 | ❌ | ✅ |
| 自动文档 | ✅ Swagger | ❌ |
| 启动速度 | ⭐⭐⭐⭐⭐ 快 | ⭐⭐ 慢 |

---

## 更多资源

- **项目主页**: https://github.com/Byaidu/PDFMathTranslate
- **问题反馈**: https://github.com/Byaidu/PDFMathTranslate/issues
- **FastAPI 官方文档**: https://fastapi.tiangolo.com/
- **原有 API 文档**: [APIS.md](./APIS.md)

---

## 许可证

本项目遵循 MIT 许可证。
