# Docker 镜像加速器配置指南（中国大陆用户）

## 问题说明

由于网络原因，中国大陆用户直接从 Docker Hub 拉取镜像可能会遇到速度慢或超时的问题。

## 解决方案：配置镜像加速器

### Windows 用户（Docker Desktop）

1. 打开 Docker Desktop
2. 点击右上角的设置图标（齿轮）
3. 选择 **Docker Engine**
4. 在JSON配置中添加以下内容：

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn",
    "https://mirror.ccs.tencentyun.com"
  ]
}
```

5. 点击 **Apply & Restart**

### Linux 用户

编辑或创建 `/etc/docker/daemon.json`：

```bash
sudo nano /etc/docker/daemon.json
```

添加以下内容：

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn",
    "https://mirror.ccs.tencentyun.com"
  ]
}
```

保存后重启Docker：

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### macOS 用户（Docker Desktop）

与Windows用户操作相同：

1. Docker Desktop → Settings → Docker Engine
2. 添加上述JSON配置
3. Apply & Restart

## 可用的Docker镜像加速器（2025年）

| 镜像源 | 地址 | 说明 | 稳定性 |
|--------|------|------|--------|
| DaoCloud | `https://docker.m.daocloud.io` | 推荐使用 | ⭐⭐⭐⭐⭐ |
| 南京大学 | `https://docker.nju.edu.cn` | 教育网速度快 | ⭐⭐⭐⭐⭐ |
| 腾讯云 | `https://mirror.ccs.tencentyun.com` | 稳定 | ⭐⭐⭐⭐ |
| 上海交大 | `https://docker.mirrors.sjtug.sjtu.edu.cn` | 教育网 | ⭐⭐⭐⭐ |

**注意：** 部分镜像源可能有访问限制或不定期维护，建议配置多个镜像源作为备用。

## 验证配置是否生效

```bash
# 查看Docker配置
docker info

# 找到以下输出，确认镜像源已配置：
# Registry Mirrors:
#  https://docker.m.daocloud.io/
#  https://docker.nju.edu.cn/
```

## 测试拉取速度

配置完成后，测试拉取Python镜像：

```bash
# 清除之前的下载缓存
docker rmi python:3.11-slim

# 重新拉取并计时
time docker pull python:3.11-slim
```

**预期结果：**
- 未配置加速器：5-10分钟或超时
- 配置加速器后：30秒-2分钟

## 构建 PDFMathTranslate 镜像

配置好加速器后，即可正常构建：

```bash
cd PDFMathTranslate
docker build -t pdf2zh-api -f Dockerfile.fastapi .
```

或使用 docker-compose：

```bash
docker-compose -f docker-compose.fastapi.yml up --build -d
```

## 常见问题

### Q1: 配置后仍然很慢怎么办？

**A:** 尝试以下方法：
1. 更换镜像源顺序（将最快的放在最前面）
2. 只保留1-2个最快的镜像源
3. 使用VPN或代理

### Q2: 是否所有镜像都能加速？

**A:** 镜像加速器主要加速 Docker Hub 官方镜像。对于第三方镜像（如 `ghcr.io`、`quay.io`），需要其他方案：

```bash
# 使用代理构建
docker build \
  --build-arg HTTP_PROXY=http://127.0.0.1:7890 \
  --build-arg HTTPS_PROXY=http://127.0.0.1:7890 \
  -t pdf2zh-api -f Dockerfile.fastapi .
```

### Q3: 镜像源失效了怎么办？

**A:** 及时更新配置，删除失效的镜像源，查找最新可用的镜像源地址。

## 相关链接

- [Docker官方文档](https://docs.docker.com/)
- [DaoCloud镜像站](https://www.daocloud.io/mirror)
- [南京大学镜像站](https://doc.nju.edu.cn/books/35f4a)

---

**更新日期：** 2025-11-03
