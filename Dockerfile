FROM pytorch/pytorch:2.4.0-cuda11.8-cudnn9-runtime
LABEL author="liuyaowen"
LABEL version="1"

COPY . /app
# 设置时区
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone


WORKDIR /app
RUN pip install -r requirements.txt


EXPOSE 12345
CMD ["fastapi", "run", "/app/endpoint/server.py","--host", "0.0.0.0", "--port", "12345"]
