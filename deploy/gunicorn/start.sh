#!/bin/bash
# FastAPIX 应用启动脚本
# Created by: tao-xiaoxin

set -e

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 确保日志目录存在
mkdir -p logs

echo "🚀 启动 FastAPIX 应用..."

# 设置环境变量(可根据需要调整)
# export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
# export LOG_LEVEL=info

# 使用 gunicorn 启动应用
gunicorn -c deploy/gunicorn/gunicorn_conf.py main:app 