# 快速修复指南：No module named pdf2zh.__main__

## 问题描述

部署后容器日志出现以下错误：

```
/usr/local/bin/python: No module named pdf2zh.__main__;
'pdf2zh' is a package and cannot be directly executed
```

## 原因

旧版本的 `Dockerfile.fastapi` 使用 `python -m pdf2zh` 启动服务，但 `pdf2zh` 包缺少 `__main__.py` 文件，导致无法以模块方式执行。

## ✅ 解决方案（已修复）

### 修复1：Dockerfile 启动命令已更新

**旧命令（错误）：**
```dockerfile
CMD ["python", "-m", "pdf2zh", "--fastapi", "--apiport", "8000"]
```

**新命令（正确）：**
```dockerfile
CMD ["uvicorn", "pdf2zh.fastapi_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 修复2：添加了 `__main__.py` 文件

在 `pdf2zh/__main__.py` 中添加了入口文件，使得 `python -m pdf2zh` 也能正常工作。

---

## 🚀 如何应用修复

### 步骤1：停止旧容器

```bash
cd D:\2024Dev\PDFMathTranslate-main
docker-compose -f docker-compose.fastapi.yml down
```

### 步骤2：删除旧镜像（可选）

```bash
# 查看镜像
docker images | grep pdf2zh

# 删除旧镜像
docker rmi pdf2zh-api
docker rmi pdmmathtranslate-main-pdf2zh-api  # 如果有的话
```

### 步骤3：重新构建并启动

```bash
docker-compose -f docker-compose.fastapi.yml up --build -d
```

### 步骤4：验证修复成功

```bash
# 查看日志
docker logs pdf2zh-fastapi

# 应该看到以下成功启动的信息：
# INFO:     Started server process [1]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 步骤5：测试API

```bash
# 健康检查
curl http://localhost:11200/health

# 预期响应
# {"status":"healthy","version":"1.0.0","service":"PDFMathTranslate API"}
```

---

## 🔍 故障排查

### 如果仍然看到错误

1. **确认文件已更新：**
   ```bash
   # Windows
   type "D:\2024Dev\PDFMathTranslate-main\Dockerfile.fastapi" | findstr uvicorn

   # 应该看到包含 uvicorn 的命令行
   ```

2. **强制重新构建（不使用缓存）：**
   ```bash
   docker-compose -f docker-compose.fastapi.yml build --no-cache
   docker-compose -f docker-compose.fastapi.yml up -d
   ```

3. **检查是否有多个容器运行：**
   ```bash
   docker ps -a | grep pdf2zh

   # 停止所有相关容器
   docker stop $(docker ps -a -q --filter name=pdf2zh)
   docker rm $(docker ps -a -q --filter name=pdf2zh)
   ```

4. **手动测试启动命令：**
   ```bash
   # 进入容器测试
   docker run -it --rm pdf2zh-api bash

   # 在容器内测试
   uvicorn pdf2zh.fastapi_server:app --host 0.0.0.0 --port 8000
   ```

---

## 📋 三种启动方式对比

| 方式 | 命令 | 状态 | 说明 |
|------|------|------|------|
| ❌ 方式1 | `python -m pdf2zh --fastapi` | 旧版错误 | 缺少`__main__.py` |
| ✅ 方式2 | `uvicorn pdf2zh.fastapi_server:app` | **推荐** | 直接启动FastAPI |
| ✅ 方式3 | `pdf2zh --fastapi` | 可用 | 使用CLI工具 |

**当前Dockerfile使用：方式2（推荐）**

---

## 🎯 验证清单

- [ ] 停止旧容器: `docker-compose down`
- [ ] 更新代码: 确认 `Dockerfile.fastapi` 包含 `uvicorn` 命令
- [ ] 重新构建: `docker-compose up --build -d`
- [ ] 查看日志: `docker logs pdf2zh-fastapi` 没有错误
- [ ] 健康检查: `curl http://localhost:11200/health` 返回正常
- [ ] API文档: 浏览器打开 `http://localhost:11200/docs` 可访问

---

## 📚 相关文件

| 文件 | 修改内容 |
|------|---------|
| `Dockerfile.fastapi` | 启动命令改为 `uvicorn` |
| `pdf2zh/__main__.py` | 新增入口文件（备用） |
| `DOCKER_DEPLOYMENT_README.md` | 添加问题8的说明 |

---

## 💡 额外说明

### 为什么使用 uvicorn 启动？

1. **直接启动**：不依赖CLI接口，更简单直接
2. **性能更好**：uvicorn是高性能ASGI服务器
3. **标准做法**：FastAPI官方推荐的启动方式
4. **日志清晰**：uvicorn提供更好的日志输出

### 如果你想使用CLI方式启动

修改 `Dockerfile.fastapi` 最后一行：

```dockerfile
# 方式A: 使用uvicorn（推荐）
CMD ["uvicorn", "pdf2zh.fastapi_server:app", "--host", "0.0.0.0", "--port", "8000"]

# 方式B: 使用CLI工具（需要确保已安装）
# CMD ["pdf2zh", "--fastapi", "--apiport", "8000"]

# 方式C: 使用python -m（需要__main__.py）
# CMD ["python", "-m", "pdf2zh", "--fastapi", "--apiport", "8000"]
```

---

**修复完成日期：** 2025-11-03
**修复版本：** v1.9.11+fix

如有其他问题，请查看 `DOCKER_DEPLOYMENT_README.md` 中的完整故障排查章节。
