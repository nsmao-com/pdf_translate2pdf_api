# 快速修复：'NoneType' object has no attribute 'predict'

## 问题描述

调用API翻译PDF时报错：

```json
{
  "error": "Translation failed: 'NoneType' object has no attribute 'predict'",
  "status_code": 500
}
```

## 原因分析

### 问题根源

OnnxModel（用于文档布局检测）没有被初始化！

在 `translate_stream` 函数中，`model` 参数默认为 `None`：

```python
def translate_stream(
    ...
    model: OnnxModel = None,  # 默认为 None
    ...
):
```

然后在 `translate_patch` 中调用：

```python
page_layout = model.predict(image, ...)  # None.predict() 报错！
```

### 为什么CLI模式正常？

在CLI模式（`pdf2zh/pdf2zh.py`）中，会先初始化模型：

```python
# 初始化全局模型实例
ModelInstance.value = OnnxModel.load_available()

# 调用translate时显式传递
translate(model=ModelInstance.value, **vars(parsed_args))
```

但在旧版FastAPI中，我们忘记了这一步！

---

## ✅ 解决方案（已修复）

### 修复内容

在 `pdf2zh/fastapi_server.py` 中添加了两个关键修改：

#### 1. 启动时初始化OnnxModel

```python
from pdf2zh.doclayout import OnnxModel, ModelInstance

# Initialize ONNX model for document layout detection
logger.info("Initializing ONNX model for document layout detection...")
try:
    ModelInstance.value = OnnxModel.load_available()
    logger.info("ONNX model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load ONNX model: {e}")
    ModelInstance.value = None
```

#### 2. 翻译时传递模型

```python
translate_params = {
    'lang_in': lang_in,
    'lang_out': lang_out,
    'service': service,
    'thread': thread,
    'model': ModelInstance.value,  # ✅ 传递ONNX模型
}

stream_mono, stream_dual = translate_stream(
    stream=pdf_bytes,
    **translate_params
)
```

---

## 🚀 应用修复

### 步骤1：停止旧容器

```bash
cd D:\2024Dev\PDFMathTranslate-main
docker-compose -f docker-compose.fastapi.yml down
```

### 步骤2：重新构建并启动

```bash
docker-compose -f docker-compose.fastapi.yml up --build -d
```

### 步骤3：查看日志确认模型加载

```bash
docker logs pdf2zh-fastapi

# 应该看到：
# INFO - Initializing ONNX model for document layout detection...
# INFO - ONNX model loaded successfully
# INFO - Application startup complete.
```

### 步骤4：测试翻译

```bash
curl -X POST http://localhost:11200/translate/mono \
  -F "file=@test.pdf" \
  -F "service=google" \
  --output translated.pdf
```

---

## 🔍 验证修复

### 检查启动日志

```bash
docker logs pdf2zh-fastapi | grep -i onnx

# 预期输出：
# Initializing ONNX model for document layout detection...
# ONNX model loaded successfully
```

### 检查健康状态

```bash
curl http://localhost:11200/health

# 预期响应：
# {"status":"healthy","version":"1.0.0","service":"PDFMathTranslate API"}
```

### 完整测试流程

```bash
# 1. 健康检查
curl http://localhost:11200/health

# 2. 获取支持的服务
curl http://localhost:11200/services

# 3. 翻译测试
curl -X POST http://localhost:11200/translate/mono \
  -F "file=@document.pdf" \
  -F "lang_in=en" \
  -F "lang_out=zh" \
  -F "service=google" \
  -F "thread=4" \
  --output translated.pdf

# 4. 检查输出文件
ls -lh translated.pdf
```

---

## 📊 修复前后对比

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| **OnnxModel初始化** | ❌ 未初始化 | ✅ 启动时初始化 |
| **model参数传递** | ❌ None | ✅ ModelInstance.value |
| **文档布局检测** | ❌ 崩溃 | ✅ 正常工作 |
| **翻译功能** | ❌ 报错 | ✅ 正常工作 |

---

## 💡 技术说明

### OnnxModel的作用

OnnxModel是一个基于YOLO的文档布局检测模型，用于：

1. **识别文档区域类型**：
   - 正文文本
   - 公式（行内/独立）
   - 图表
   - 表格
   - 标题

2. **保留排版**：
   - 确定哪些区域需要翻译
   - 哪些区域保持原样（如数学公式）
   - 保持原始布局结构

### 为什么需要在启动时加载？

1. **模型文件较大**：下载和加载需要时间
2. **全局共享**：所有请求共享同一个模型实例
3. **避免重复加载**：提高性能

### ModelInstance是什么？

`ModelInstance` 是一个单例类，用于存储全局的OnnxModel实例：

```python
class ModelInstance:
    value: OnnxModel = None  # 全局模型实例
```

所有翻译请求共享这个实例，避免重复加载。

---

## 🐛 常见问题

### Q1: 启动时提示"Failed to load ONNX model"

**可能原因：**
- HuggingFace模型下载失败
- 网络问题

**解决方案：**

```bash
# 配置HuggingFace镜像
docker run -d \
  -p 11200:8000 \
  -e HF_ENDPOINT=https://hf-mirror.com \
  pdf2zh-api
```

### Q2: 模型加载很慢

**原因：** 首次下载模型文件（约200MB）

**解决方案：** 耐心等待，后续启动会使用缓存

### Q3: 内存不足

**原因：** ONNX模型需要约500MB-1GB内存

**解决方案：** 增加Docker内存限制

```yaml
services:
  pdf2zh-api:
    deploy:
      resources:
        limits:
          memory: 4G
```

---

## 📚 相关文件

| 文件 | 修改内容 |
|------|---------|
| `pdf2zh/fastapi_server.py` | 添加OnnxModel初始化和传递 |
| `FIX_ONNX_MODEL.md` | 本修复指南 |
| `DOCKER_DEPLOYMENT_README.md` | 需要更新（添加新问题） |

---

## ✅ 修复清单

- [x] 导入 `OnnxModel` 和 `ModelInstance`
- [x] 启动时初始化 `ModelInstance.value`
- [x] 所有翻译端点传递 `model` 参数
- [x] 添加日志记录模型加载状态
- [x] 添加异常处理

---

## 🎉 总结

**问题：** OnnxModel未初始化导致 `None.predict()` 报错

**解决：** 在FastAPI启动时初始化模型，并在调用时传递

**关键代码：**
```python
# 启动时
ModelInstance.value = OnnxModel.load_available()

# 调用时
translate_stream(..., model=ModelInstance.value)
```

---

**修复完成日期：** 2025-11-03
**修复版本：** v1.9.11+fix4

如有其他问题，请参考 `DOCKER_DEPLOYMENT_README.md`。
