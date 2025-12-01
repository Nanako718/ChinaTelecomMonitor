# 使用官方 Python 镜像作为基础镜像
FROM python:3.13-alpine

# 设置工作目录
WORKDIR /app

# 只复制必要的文件，排除不必要的文件
COPY requirements.txt /app/
COPY app/ /app/app/
COPY telecom_class.py /app/

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 时区
ENV TZ="Asia/Shanghai"

# 构建版本
ARG BUILD_SHA
ARG BUILD_TAG
ENV BUILD_SHA=$BUILD_SHA
ENV BUILD_TAG=$BUILD_TAG

# 创建配置目录（用于挂载 volume）
RUN mkdir -p /app/config

# 端口
EXPOSE 10000

# 运行应用程序
CMD ["python", "./app/api_server.py"]