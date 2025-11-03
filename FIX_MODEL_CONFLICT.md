# 根本问题修复：'str' object has no attribute 'predict'

## 🔍 问题根源分析

### 错误信息
```json
{
  "error": "Translation failed: 'str' object has no attribute 'predict'",
  "status_code": 500
}
```

### 根本原因：参数名冲突

在PDFMathTranslate项目中，存在**两个不同用途的`model`参数**：

#### 1. 文档布局检测的`model`（OnnxModel对象）

在 `pdf2zh/high_level.py` 的 `translate_stream` 函数中：

```python
def translate_stream(
    ...
    model: OnnxModel = None,  # ONNX模型对象，用于文档布局检测
    ...
):
    ...
```

在 `translate_patch` 函数中被使用：

```python
page_layout = model.predict(image, imgsz=int(pix.height / 32) * 32)[0]
#             ^^^^^^^^^^^^^^^
#             这里调用OnnxModel的predict方法
```

#### 2. LLM的模型名（字符串）

但在旧版FastAPI中，我们错误地定义了：

```python
async def translate_mono(
    ...
    model: Optional[str] = Form(None, description="Model name (for LLM services)"),
    ...
):
    ...
    translate_params['model'] = model  # ❌ 字符串覆盖了OnnxModel参数
```

当传递 `model="gpt-4o-mini"` 时，字符串覆盖了 `OnnxModel` 参数，导致代码尝试：

```python
"gpt-4o-mini".predict(image, ...)  # ❌ 字符串没有predict方法！
```

---

## ✅ 正确的设计

### LLM模型名的正确传递方式

在 `pdf2zh/converter.py` 第157-165行，揭示了正确的设计：

```python
# LLM模型名通过service参数传递，格式为 "service_name:model_name"
# 例如：
#   - "google"                 (无需模型名)
#   - "openai:gpt-4o-mini"    (OpenAI + 模型名)
#   - "ollama:gemma2:9b"      (Ollama + 模型名)

param = service.split(":", 1)
service_name = param[0]           # "openai"
service_model = param[1] if len(param) > 1 else None  # "gpt-4o-mini"

# 模型名传递给translator
self.translator = translator(lang_in, lang_out, service_model, ...)
```

### 参数职责分离

| 参数 | 类型 | 用途 | 传递位置 |
|------|------|------|----------|
| `service` | `str` | 指定翻译服务和LLM模型 | API参数 |
| `model` | `OnnxModel` | 文档布局检测模型 | 内部自动初始化 |

**关键点：**
- ✅ `service` 参数可以包含模型名（用冒号分隔）
- ✅ `model` 参数应该由内部代码自动初始化，不应该从API传递
- ❌ 不应该有单独的 `model: str` API参数

---

## 🔧 修复内容

### 1. 移除错误的`model`参数

**修改前（错误）：**
```python
async def translate_mono(
    file: UploadFile = File(...),
    lang_in: str = Form("en"),
    lang_out: str = Form("zh"),
    service: str = Form("google"),
    model: Optional[str] = Form(None),  # ❌ 错误的参数
    thread: int = Form(4)
):
    translate_params = {
        'lang_in': lang_in,
        'lang_out': lang_out,
        'service': service,
        'thread': thread,
    }
    if model:
        translate_params['model'] = model  # ❌ 覆盖OnnxModel参数
```

**修改后（正确）：**
```python
async def translate_mono(
    file: UploadFile = File(...),
    lang_in: str = Form("en"),
    lang_out: str = Form("zh"),
    service: str = Form("google", description="Translation service (e.g., 'google', 'openai:gpt-4o-mini')"),
    thread: int = Form(4)
):
    translate_params = {
        'lang_in': lang_in,
        'lang_out': lang_out,
        'service': service,  # ✅ 模型名在service中
        'thread': thread,
    }
    # ✅ 不再传递model参数
```

### 2. 更新的API端点

所有3个端点已修复：
- ✅ `/translate/mono` - 单语翻译
- ✅ `/translate/dual` - 双语翻译
- ✅ `/translate` - 完整翻译（返回JSON）

---

## 📚 API使用指南

### 正确的API参数

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `file` | ✅ | - | PDF文件 |
| `lang_in` | ❌ | `en` | 源语言代码 |
| `lang_out` | ❌ | `zh` | 目标语言代码 |
| `service` | ❌ | `google` | 翻译服务（可包含模型名） |
| `thread` | ❌ | `4` | 并发线程数（1-16） |

### service参数格式

**简单服务（无需模型名）：**
```bash
service=google
service=bing
service=deepl
```

**LLM服务（需要模型名）：**
```bash
service=openai:gpt-4o-mini
service=openai:gpt-4
service=ollama:gemma2:9b
service=ollama:llama3:8b
service=gemini:gemini-pro
service=zhipu:glm-4
```

---

## 🚀 使用示例

### 示例1：使用Google翻译（免费）

```bash
curl -X POST http://localhost:11200/translate/mono \
  -F "file=@document.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=google" \
  --output translated.pdf
```

### 示例2：使用OpenAI GPT-4o-mini

```bash
curl -X POST http://localhost:11200/translate/mono \
  -F "file=@document.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=openai:gpt-4o-mini" \
  -F "thread=8" \
  --output translated.pdf
```

### 示例3：使用Ollama本地模型

```bash
curl -X POST http://localhost:11200/translate/mono \
  -F "file=@document.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=ollama:gemma2:9b" \
  --output translated.pdf
```

### 示例4：双语版本

```bash
curl -X POST http://localhost:11200/translate/dual \
  -F "file=@document.pdf" \
  -F "service=openai:gpt-4o-mini" \
  --output translated_dual.pdf
```

---

## 🐍 Python调用示例

### 正确的Python代码

```python
import requests

def translate_pdf(
    input_file: str,
    output_file: str,
    service: str = "google",
    lang_in: str = "en",
    lang_out: str = "zh",
    thread: int = 4
):
    """
    翻译PDF文件

    Args:
        input_file: 输入PDF路径
        output_file: 输出PDF路径
        service: 翻译服务，格式：
            - 简单: "google", "bing", "deepl"
            - LLM: "openai:gpt-4o-mini", "ollama:gemma2:9b"
        lang_in: 源语言
        lang_out: 目标语言
        thread: 线程数
    """
    url = 'http://localhost:11200/translate/mono'

    with open(input_file, 'rb') as f:
        files = {'file': f}
        data = {
            'lang_in': lang_in,
            'lang_out': lang_out,
            'service': service,  # ✅ 模型名在service中
            'thread': thread,
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
translate_pdf('paper.pdf', 'paper_zh.pdf', service='google')
translate_pdf('paper.pdf', 'paper_zh_gpt.pdf', service='openai:gpt-4o-mini')
translate_pdf('paper.pdf', 'paper_zh_local.pdf', service='ollama:gemma2:9b')
```

### ❌ 错误示例（旧版本）

```python
# ❌ 不要这样做！
data = {
    'lang_in': 'en',
    'lang_out': 'zh',
    'service': 'openai',      # ❌ 错误：分离了服务和模型
    'model': 'gpt-4o-mini',   # ❌ 错误：model参数已移除
    'thread': 4,
}
```

---

## 🔧 应用修复

### 步骤1：停止旧容器

```bash
cd D:\2024Dev\PDFMathTranslate-main
docker-compose -f docker-compose.fastapi.yml down
```

### 步骤2：重新构建

```bash
docker-compose -f docker-compose.fastapi.yml up --build -d
```

### 步骤3：验证修复

```bash
# 健康检查
curl http://localhost:11200/health

# 测试Google翻译
curl -X POST http://localhost:11200/translate/mono \
  -F "file=@test.pdf" \
  -F "service=google" \
  --output test_zh.pdf

# 测试OpenAI翻译（需要配置API密钥）
curl -X POST http://localhost:11200/translate/mono \
  -F "file=@test.pdf" \
  -F "service=openai:gpt-4o-mini" \
  --output test_zh_gpt.pdf
```

---

## 📊 支持的服务和模型

### 免费服务
- `google` - Google翻译
- `bing` - Microsoft Bing翻译
- `deepl` - DeepL翻译（免费版）
- `deeplx` - DeepL X

### LLM服务（需要API密钥）

| 服务 | 格式示例 | 说明 |
|------|----------|------|
| OpenAI | `openai:gpt-4o-mini` | 需要OPENAI_API_KEY |
| Gemini | `gemini:gemini-pro` | 需要GEMINI_API_KEY |
| Anthropic | `anthropic:claude-3-haiku` | 需要ANTHROPIC_API_KEY |
| Zhipu | `zhipu:glm-4` | 需要ZHIPU_API_KEY |
| DeepSeek | `deepseek:deepseek-chat` | 需要DEEPSEEK_API_KEY |
| Ollama | `ollama:gemma2:9b` | 需要本地Ollama服务 |

### 配置API密钥

通过环境变量或配置文件：

```bash
# 环境变量方式
docker run -d \
  -p 11200:8000 \
  -e OPENAI_API_KEY=sk-your-key \
  -e GEMINI_API_KEY=your-key \
  pdf2zh-api
```

或使用配置文件：`~/.config/PDFMathTranslate/config.json`

---

## ✅ 修复清单

- [x] 移除所有端点的 `model` 参数
- [x] 更新 `service` 参数说明（支持冒号分隔的模型名）
- [x] 移除 `translate_params` 中的model处理逻辑
- [x] 更新API文档说明
- [x] 创建详细的修复指南

---

## 🎉 总结

**核心问题：** 参数名冲突导致字符串覆盖OnnxModel对象

**根本解决：** 移除独立的`model`参数，通过`service`参数传递LLM模型名

**正确格式：** `service="service_name:model_name"`

**修复后：** API更简洁，参数职责更清晰，不再有冲突

---

**修复完成日期：** 2025-11-03
**修复版本：** v1.9.11+fix3

如有其他问题，请参考 `DOCKER_DEPLOYMENT_README.md`。
