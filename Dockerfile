FROM pytorch/pytorch:2.4.0-cuda11.8-cudnn9-runtime
LABEL author="liuyaowen"
LABEL version="1.0.0"

COPY . /app
# 设置时区
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone
# 修改 APT 镜像源为清华大学镜像
RUN sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
# 更新源并安装必要的包
RUN apt-get update && apt-get install -f && apt-get install -y  x11-common libsm6 python3-dev ffmpeg

WORKDIR /app
# 安装 Python 依赖并使用国内 pip 源
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

EXPOSE 12345

CMD ["fastapi", "run", "/app/endpoint/server.py","--host", "0.0.0.0", "--port", "12345"]
