# 快速修复指南：Translation failed - 'str' object is not callable

## 问题描述

调用API翻译PDF时报错：

```json
{
  "error": "Translation failed: 'str' object is not callable",
  "detail": "'str' object is not callable"
}
```

## 原因分析

### 问题根源

在 `pdf2zh/fastapi_server.py` 中，`callback` 参数被定义为字符串类型：

```python
callback: Optional[str] = Form(None, description="Custom prompt callback")
```

但在 `pdf2zh/high_level.py` 的 `translate_stream` 函数中，`callback` 被期望为可调用的函数对象：

```python
def translate_stream(
    ...
    callback: object = None,  # 期望是函数对象
    ...
):
    ...
    if callback:
        callback(progress)  # 这里会调用callback
```

当传入字符串时，代码尝试 `callback(progress)`，相当于 `"some_string"(progress)`，Python就会报错 `'str' object is not callable`。

### 为什么有这个参数？

`callback` 参数主要用于GUI模式的进度条更新，在API模式下并不需要。

---

## ✅ 解决方案（已修复）

### 修复内容

已在 `pdf2zh/fastapi_server.py` 中移除所有翻译端点的 `callback` 参数：

**修改的端点：**
1. `/translate/mono` - 单语翻译
2. `/translate/dual` - 双语翻译
3. `/translate` - 完整翻译（返回JSON）

**修改前：**
```python
async def translate_mono(
    ...
    callback: Optional[str] = Form(None, description="Custom prompt callback")
):
    ...
    if callback:
        translate_params['callback'] = callback  # 错误：传递字符串
```

**修改后：**
```python
async def translate_mono(
    ...
    # callback 参数已移除
):
    ...
    # 不再传递 callback 参数
```

---

## 🚀 如何应用修复

### 步骤1：停止旧容器

```bash
cd D:\2024Dev\PDFMathTranslate-main
docker-compose -f docker-compose.fastapi.yml down
```

### 步骤2：重新构建并启动

```bash
docker-compose -f docker-compose.fastapi.yml up --build -d
```

### 步骤3：验证修复

```bash
# 查看日志
docker logs pdf2zh-fastapi

# 测试翻译（不传递callback参数）
curl -X POST http://localhost:11200/translate/mono \
  -F "file=@test.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=google" \
  --output translated.pdf
```

---

## 📋 正确的API参数列表

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `file` | File | ✅ | - | 要翻译的PDF文件 |
| `lang_in` | String | ❌ | `en` | 源语言代码 |
| `lang_out` | String | ❌ | `zh` | 目标语言代码 |
| `service` | String | ❌ | `google` | 翻译服务名称 |
| `model` | String | ❌ | `None` | LLM模型名（如gpt-4o-mini） |
| `thread` | Integer | ❌ | `4` | 并发线程数（1-16） |
| ~~`callback`~~ | ~~String~~ | ❌ | - | ❌ **已移除** |

---

## 🔍 API调用示例

### ✅ 正确示例

```bash
# 基础翻译
curl -X POST http://localhost:11200/translate/mono \
  -F "file=@document.pdf" \
  -F "lang_out=zh" \
  --output translated.pdf

# 使用OpenAI翻译
curl -X POST http://localhost:11200/translate/mono \
  -F "file=@document.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=openai" \
  -F "model=gpt-4o-mini" \
  -F "thread=8" \
  --output translated.pdf

# 双语版本
curl -X POST http://localhost:11200/translate/dual \
  -F "file=@document.pdf" \
  -F "lang_out=zh" \
  --output translated_dual.pdf
```

### ❌ 错误示例（旧版本）

```bash
# 不要传递 callback 参数！
curl -X POST http://localhost:11200/translate/mono \
  -F "file=@document.pdf" \
  -F "callback=some_callback" \  # ❌ 错误：会导致报错
  --output translated.pdf
```

---

## 🐍 Python调用示例

### ✅ 正确代码

```python
import requests

def translate_pdf(input_file, output_file, service='google'):
    """翻译PDF文件"""
    url = 'http://localhost:11200/translate/mono'

    with open(input_file, 'rb') as f:
        files = {'file': f}
        data = {
            'lang_in': 'en',
            'lang_out': 'zh',
            'service': service,
            'thread': 8,
            # 不要添加 callback 参数
        }

        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            with open(output_file, 'wb') as out:
                out.write(response.content)
            print(f"✅ 翻译成功: {output_file}")
            return True
        else:
            print(f"❌ 翻译失败: {response.json()}")
            return False

# 使用示例
translate_pdf('research.pdf', 'research_zh.pdf')
```

### ❌ 错误代码（旧版本）

```python
# 不要这样做！
data = {
    'lang_in': 'en',
    'lang_out': 'zh',
    'service': 'google',
    'callback': 'my_callback'  # ❌ 错误：会导致 'str' object is not callable
}
```

---

## 🔧 故障排查

### 问题1：重新构建后仍报错

**解决方案：**

```bash
# 完全清理并重建
docker-compose -f docker-compose.fastapi.yml down
docker rmi pdf2zh-api pdmmathtranslate-main-pdf2zh-api
docker-compose -f docker-compose.fastapi.yml build --no-cache
docker-compose -f docker-compose.fastapi.yml up -d
```

### 问题2：如何确认代码已更新？

```bash
# 检查 fastapi_server.py 是否已修复
type "D:\2024Dev\PDFMathTranslate-main\pdf2zh\fastapi_server.py" | findstr callback

# 应该只在注释或文档字符串中看到 callback，函数参数中不应该有
```

### 问题3：API文档中仍显示callback参数

这是正常的，重启容器后访问 `http://localhost:11200/docs` 会自动更新。

---

## 📊 修复前后对比

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| **参数数量** | 7个 | 6个 |
| **callback参数** | ❌ 存在（String） | ✅ 已移除 |
| **调用callback** | ❌ 会报错 | ✅ 不再调用 |
| **API稳定性** | ❌ 可能报错 | ✅ 稳定 |
| **进度反馈** | ❌ 不可用 | N/A（API模式不需要） |

---

## 💡 技术说明

### 为什么不能传递字符串？

在Python中：

```python
# 正确：callback 是函数
def my_callback(progress):
    print(f"Progress: {progress}")

callback = my_callback
callback(50)  # ✅ 正常工作

# 错误：callback 是字符串
callback = "my_callback"
callback(50)  # ❌ TypeError: 'str' object is not callable
```

### 为什么GUI模式需要callback？

GUI模式使用callback更新进度条：

```python
import gradio as gr

def progress_callback(progress):
    gr.Progress()(progress.n / progress.total, desc="Translating...")

translate_stream(
    ...,
    callback=progress_callback  # 函数对象，不是字符串
)
```

### API模式为什么不需要？

API是无状态的HTTP请求：
1. 客户端发送请求
2. 服务器处理（无法实时推送进度）
3. 服务器返回结果

如果需要进度反馈，应该使用WebSocket或轮询机制，而不是callback。

---

## 📚 相关文件

| 文件 | 修改内容 |
|------|---------|
| `pdf2zh/fastapi_server.py` | 移除所有端点的callback参数 |
| `DOCKER_DEPLOYMENT_README.md` | 添加问题8的说明 |
| `FIX_CALLBACK_ERROR.md` | 本修复指南 |

---

## ✅ 验证清单

执行以下步骤确认修复成功：

- [ ] 停止旧容器: `docker-compose down`
- [ ] 重新构建: `docker-compose up --build -d`
- [ ] 查看日志: `docker logs pdf2zh-fastapi` 无错误
- [ ] 健康检查: `curl http://localhost:11200/health` 正常
- [ ] API文档: 访问 `http://localhost:11200/docs` 确认callback参数已移除
- [ ] 测试翻译: 上传PDF文件，成功翻译并下载

---

**修复完成日期：** 2025-11-03
**修复版本：** v1.9.11+fix2

如有其他问题，请参考 `DOCKER_DEPLOYMENT_README.md` 的完整故障排查章节。
