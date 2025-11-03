# FastAPI 快速启动指南

## 一键启动

### 1. 安装依赖

```bash
pip install -r requirements-fastapi.txt
```

### 2. 启动服务

```bash
pdf2zh --fastapi
```

### 3. 访问文档

打开浏览器访问: http://localhost:8000/docs

---

## 快速测试

### 使用 curl 测试

```bash
# 健康检查
curl http://localhost:8000/health

# 翻译 PDF
curl -X POST http://localhost:8000/translate/mono \
  -F "file=@example.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=google" \
  --output example-zh.pdf
```

### 使用 Python 测试

```python
import requests

with open('example.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/translate/mono',
        files={'file': f},
        data={'lang_in': 'en', 'lang_out': 'zh', 'service': 'google'}
    )

with open('example-zh.pdf', 'wb') as f:
    f.write(response.content)
```

---

## 配置选项

```bash
# 自定义端口
pdf2zh --fastapi --apiport 9000

# 指定配置文件
pdf2zh --fastapi --config config.json

# 调试模式
pdf2zh --fastapi --debug
```

---

## 详细文档

查看完整文档: [docs/FASTAPI.md](docs/FASTAPI.md)

## 支持的翻译服务

- **免费**: google, bing, argos
- **付费**: deepl, openai, azure-openai, gemini
- **本地**: ollama, xinference

完整列表: http://localhost:8000/services
