# 修复：HTTP响应头中文文件名编码错误

## 问题描述

上传中文文件名的PDF翻译时报错：

```
UnicodeEncodeError: 'latin-1' codec can't encode characters in position 22-42: ordinal not in range(256)

File "/usr/local/lib/python3.11/site-packages/starlette/responses.py", line 62, in init_headers
raw_headers = [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in headers.items()]
```

**示例：** 上传文件名为 `爆炸瞬态温度测试中热电偶传感器实时补偿技术_赵化彬.pdf` 时报错。

## 原因分析

### 根本原因

HTTP响应头必须使用**ASCII或latin-1编码**，不能直接包含中文等非ASCII字符。

**错误代码（旧版）：**

```python
output_filename = file.filename.replace('.pdf', f'-{lang_out}.pdf')

return StreamingResponse(
    io.BytesIO(stream_mono),
    media_type='application/pdf',
    headers={
        'Content-Disposition': f'attachment; filename="{output_filename}"'
        # ❌ 如果output_filename包含中文，编码会失败
    }
)
```

### HTTP头编码规范

根据RFC 2616和RFC 5987：

1. **HTTP头默认编码：** ISO-8859-1（latin-1）
2. **中文文件名解决方案：** 使用RFC 5987编码

**RFC 5987格式：**
```
Content-Disposition: attachment;
    filename="fallback.pdf";
    filename*=UTF-8''%E7%88%86%E7%82%B8...
```

- `filename`: ASCII回退文件名（浏览器兼容性）
- `filename*`: UTF-8 URL编码的真实文件名

---

## ✅ 解决方案

### 修复内容

在 `pdf2zh/fastapi_server.py` 中添加了编码处理函数：

```python
from urllib.parse import quote

def encode_filename_header(filename: str) -> str:
    """
    Create a Content-Disposition header value with proper filename encoding.
    Supports both ASCII and UTF-8 filenames (RFC 5987).
    """
    # Try to encode as ASCII (for simple filenames)
    try:
        filename.encode('ascii')
        # ASCII filename, use simple format
        return f'attachment; filename="{filename}"'
    except UnicodeEncodeError:
        # Non-ASCII filename, use RFC 5987 format
        # ASCII fallback (replace non-ASCII with ?)
        ascii_filename = filename.encode('ascii', errors='replace').decode('ascii')
        # UTF-8 encoded filename (URL-encoded)
        utf8_filename = quote(filename.encode('utf-8'))
        return f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{utf8_filename}'
```

**使用方式：**

```python
return StreamingResponse(
    io.BytesIO(stream_mono),
    media_type='application/pdf',
    headers={
        'Content-Disposition': encode_filename_header(output_filename)
        # ✅ 自动处理ASCII和UTF-8文件名
    }
)
```

---

## 📊 修复效果

### 修复前

| 文件名类型 | 示例 | 结果 |
|-----------|------|------|
| 英文 | `document.pdf` | ✅ 正常 |
| 中文 | `爆炸瞬态温度测试.pdf` | ❌ 编码错误 |
| 日文 | `温度測定.pdf` | ❌ 编码错误 |
| 韩文 | `온도측정.pdf` | ❌ 编码错误 |

### 修复后

| 文件名类型 | 示例 | Content-Disposition | 结果 |
|-----------|------|---------------------|------|
| 英文 | `document.pdf` | `attachment; filename="document.pdf"` | ✅ 正常 |
| 中文 | `爆炸瞬态温度测试.pdf` | `attachment; filename="???????.pdf"; filename*=UTF-8''%E7%88%86...` | ✅ 正常 |
| 日文 | `温度測定.pdf` | `attachment; filename="????.pdf"; filename*=UTF-8''%E6%B8%A9...` | ✅ 正常 |
| 韩文 | `온도측정.pdf` | `attachment; filename="????.pdf"; filename*=UTF-8''%EC%98%A8...` | ✅ 正常 |

---

## 🚀 应用修复

### 步骤1：停止旧容器

```bash
cd D:\2024Dev\PDFMathTranslate-main
docker-compose -f docker-compose.fastapi.yml down
```

### 步骤2：重新构建

```bash
docker-compose -f docker-compose.fastapi.yml up --build -d
```

### 步骤3：测试中文文件名

```bash
# 测试中文文件名
curl -X POST http://localhost:11200/translate/mono \
  -F "file=@爆炸瞬态温度测试.pdf" \
  -F "service=google" \
  --output translated.pdf
```

---

## 🔍 技术细节

### RFC 5987 编码示例

**原始文件名：**
```
爆炸瞬态温度测试_赵化彬.pdf
```

**编码步骤：**

1. **ASCII回退：** `??????_???.pdf`（非ASCII字符替换为`?`）
2. **UTF-8编码：** `爆炸瞬态温度测试_赵化彬.pdf` → UTF-8字节序列
3. **URL编码：** `%E7%88%86%E7%82%B8%E7%9E%AC%E6%80%81%E6%B8%A9%E5%BA%A6%E6%B5%8B%E8%AF%95_%E8%B5%B5%E5%8C%96%E5%BD%AC.pdf`

**最终HTTP头：**
```
Content-Disposition: attachment;
    filename="??????_???.pdf";
    filename*=UTF-8''%E7%88%86%E7%82%B8%E7%9E%AC%E6%80%81%E6%B8%A9%E5%BA%A6%E6%B5%8B%E8%AF%95_%E8%B5%B5%E5%8C%96%E5%BD%AC.pdf
```

### 浏览器兼容性

| 浏览器 | 支持RFC 5987 | 下载文件名 |
|--------|-------------|-----------|
| Chrome 90+ | ✅ | `爆炸瞬态温度测试_赵化彬.pdf` |
| Firefox 80+ | ✅ | `爆炸瞬态温度测试_赵化彬.pdf` |
| Safari 14+ | ✅ | `爆炸瞬态温度测试_赵化彬.pdf` |
| Edge 90+ | ✅ | `爆炸瞬态温度测试_赵化彬.pdf` |
| 旧浏览器 | ❌ | `??????_???.pdf` (回退) |

---

## 🐛 相关问题

### Q1: 下载的文件名显示乱码？

**可能原因：**
- 浏览器太旧，不支持RFC 5987
- 使用了不支持的工具（如某些curl版本）

**解决方案：**
- 使用现代浏览器
- 手动重命名下载的文件

### Q2: curl下载后文件名不正确？

**正常现象：** curl不解析`filename*`参数，会使用ASCII回退文件名。

**解决方案：** 使用`-o`参数指定文件名

```bash
curl -X POST http://localhost:11200/translate/mono \
  -F "file=@中文.pdf" \
  -o "中文-en.pdf"  # 手动指定文件名
```

### Q3: Python requests如何获取正确文件名？

```python
import requests
from urllib.parse import unquote

response = requests.post(...)

# 从Content-Disposition头解析文件名
content_disp = response.headers.get('Content-Disposition', '')
if "filename*=UTF-8''" in content_disp:
    # 提取UTF-8编码的文件名
    encoded_name = content_disp.split("filename*=UTF-8''")[1]
    filename = unquote(encoded_name)
else:
    # 回退到普通filename
    filename = content_disp.split('filename="')[1].split('"')[0]

# 保存文件
with open(filename, 'wb') as f:
    f.write(response.content)
```

---

## ✅ 修复影响范围

### 修改的文件

| 文件 | 修改内容 |
|------|---------|
| `pdf2zh/fastapi_server.py` | 添加`encode_filename_header`函数 |
| `pdf2zh/fastapi_server.py` | 修改`/translate/mono`端点 |
| `pdf2zh/fastapi_server.py` | 修改`/translate/dual`端点 |

### 受影响的API端点

| 端点 | 影响 | 修复状态 |
|------|------|---------|
| `/translate/mono` | ✅ 修复 | 支持中文文件名 |
| `/translate/dual` | ✅ 修复 | 支持中文文件名 |
| `/translate` | ❌ 不受影响 | 返回JSON，无文件名 |

---

## 📚 参考资料

- **RFC 2616**: HTTP/1.1协议（已过时，但仍广泛使用）
- **RFC 5987**: HTTP头参数的字符集和语言编码
- **RFC 6266**: Content-Disposition头的使用
- **MDN**: [Content-Disposition](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition)

---

## 🎯 总结

**问题：** HTTP响应头不能直接包含中文文件名

**原因：** HTTP头必须是ASCII/latin-1编码

**修复：** 使用RFC 5987编码（`filename*=UTF-8''...`）

**效果：** 所有语言的文件名都能正确下载

---

**修复完成日期：** 2025-11-03
**修复版本：** v1.9.11+fix6

如有其他问题，请查看 `DOCKER_DEPLOYMENT_README.md` 或提交Issue。
