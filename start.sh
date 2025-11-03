#!/bin/bash
# FastAPI 启动脚本
# 文件位置: /www/wwwroot/pdf2zh/pdf_translate2pdf_api-main/start.sh

cd /www/wwwroot/pdf2zh/pdf_translate2pdf_api-main

# 激活虚拟环境
source venv/bin/activate

# 启动 FastAPI 服务
python -m pdf2zh --fastapi --apiport 8000

# 或者使用 uvicorn 直接启动
# uvicorn pdf2zh.fastapi_server:app --host 0.0.0.0 --port 8000
