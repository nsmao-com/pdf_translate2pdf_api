# 演示版本 vs 生产版本对比说明

## ❌ 演示版本 (fastapi_demo.py) - 您当前测试的版本

### 返回内容
```json
{
  "status": "demo_mode",
  "message": "This is a demo API. Actual translation requires full pdf2zh installation.",
  "request_info": {
    "filename": "鼠标指针使用方法.pdf",
    "file_size_bytes": 282501,
    "lang_in": "en",
    "lang_out": "zh",
    "service": "google",
    "thread": 4
  },
  "note": "In production, this endpoint would return the translated PDF file"
}
```

### 代码逻辑（演示版）
```python
# 演示版本 - 仅返回 JSON
@app.post("/translate/mono")
async def translate_mono(file: UploadFile = File(...), ...):
    content = await file.read()
    file_size = len(content)

    # 只返回请求信息，不做任何翻译
    return JSONResponse({
        "status": "demo_mode",
        "message": "This is a demo API...",
        "request_info": {...}
    })
```

---

## ✅ 生产版本 (pdf2zh/fastapi_server.py) - 真实环境

### 返回内容
**直接返回翻译后的 PDF 文件**，不是 JSON！

```
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="鼠标指针使用方法-zh.pdf"

%PDF-1.4
[实际的 PDF 二进制数据...]
```

### 代码逻辑（生产版）
```python
# 生产版本 - 返回真实的 PDF 文件
@app.post("/translate/mono")
async def translate_mono(file: UploadFile = File(...), ...):
    # 1. 读取 PDF
    pdf_bytes = await file.read()

    # 2. 调用真实的翻译函数
    stream_mono, stream_dual = translate_stream(
        stream=pdf_bytes,
        lang_in=lang_in,
        lang_out=lang_out,
        service=service,
        thread=thread
    )

    # 3. 返回翻译后的 PDF 文件（不是 JSON！）
    return StreamingResponse(
        io.BytesIO(stream_mono),
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="...-zh.pdf"'
        }
    )
```

---

## 核心区别

| 项目 | 演示版本 | 生产版本 |
|------|---------|---------|
| **文件名** | `fastapi_demo.py` | `pdf2zh/fastapi_server.py` |
| **返回类型** | JSON 消息 | PDF 文件 |
| **Content-Type** | `application/json` | `application/pdf` |
| **翻译功能** | ❌ 不翻译 | ✅ 真实翻译 |
| **依赖** | 仅 FastAPI | 完整 pdf2zh |
| **用途** | 测试 API 结构 | 生产环境 |

---

## 生产环境实际使用场景

### 场景 1: 使用 cURL

```bash
# 请求
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@鼠标指针使用方法.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=google" \
  --output 鼠标指针使用方法-zh.pdf

# 响应（生产版本）
# 直接下载到本地的 PDF 文件，可以用 Adobe Reader 打开！
```

### 场景 2: 使用 Python requests

```python
import requests

with open('鼠标指针使用方法.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/translate/mono',
        files={'file': f},
        data={'lang_in': 'en', 'lang_out': 'zh', 'service': 'google'}
    )

# 生产版本：response.content 是真实的 PDF 二进制数据
with open('translated.pdf', 'wb') as f:
    f.write(response.content)  # 可以直接打开的 PDF！

print(f"文件大小: {len(response.content)} bytes")
print(f"Content-Type: {response.headers['Content-Type']}")  # application/pdf
```

### 场景 3: 浏览器中使用

```javascript
// 生产版本
async function translatePDF(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('lang_in', 'en');
    formData.append('lang_out', 'zh');
    formData.append('service', 'google');

    const response = await fetch('http://localhost:8000/translate/mono', {
        method: 'POST',
        body: formData
    });

    // 生产版本：直接下载 PDF 文件！
    const blob = await response.blob();  // 这是真实的 PDF blob
    const url = URL.createObjectURL(blob);

    // 触发下载
    const a = document.createElement('a');
    a.href = url;
    a.download = 'translated.pdf';
    a.click();
}
```

---

## 如何切换到生产版本

### 前提条件
1. Python 3.10-3.12（不是 3.13）
2. 安装完整 pdf2zh 及依赖

### 启动方式

```bash
# 方式 1: 使用命令行工具（推荐）
pdf2zh --fastapi --apiport 8000

# 方式 2: 直接运行模块
python -m pdf2zh.fastapi_server

# 方式 3: 使用 uvicorn
uvicorn pdf2zh.fastapi_server:app --host 0.0.0.0 --port 8000
```

### 验证是否是生产版本

```bash
# 测试请求
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@test.pdf" \
  -F "service=google" \
  --output result.pdf

# 检查结果
file result.pdf
# 生产版本输出: result.pdf: PDF document, version 1.x
# 演示版本输出: result.pdf: JSON data
```

---

## 当前环境问题

您当前环境的限制：
```
Python 3.13.3 (需要 3.10-3.12)
缺少 pdf2zh 核心依赖
依赖版本冲突
```

### 解决方案

**方案 A: 使用兼容 Python 版本**
```bash
# 安装 Python 3.11
conda create -n pdf2zh python=3.11
conda activate pdf2zh

# 安装依赖
pip install pdf2zh
pip install fastapi uvicorn python-multipart

# 启动生产版本
pdf2zh --fastapi
```

**方案 B: 使用 Docker**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install pdf2zh fastapi uvicorn python-multipart

EXPOSE 8000
CMD ["pdf2zh", "--fastapi", "--apiport", "8000"]
```

```bash
docker build -t pdf2zh-api .
docker run -p 8000:8000 pdf2zh-api

# 此时就是真正的生产版本！
```

---

## 总结

| 问题 | 回答 |
|------|------|
| 生产环境也返回 demo_mode 吗？ | ❌ 不会！返回真实的 PDF 文件 |
| 当前测试的是什么版本？ | 演示版本（仅测试 API 结构） |
| 如何使用生产版本？ | 需要兼容 Python 版本 + 完整依赖 |
| 生产版本返回什么？ | `application/pdf` 二进制文件 |

**演示版本**仅用于验证 API 设计是否合理，**不包含实际翻译功能**。

**生产版本**会调用 `translate_stream()` 函数，执行真正的 PDF 翻译，并返回可以直接打开的 PDF 文件！
