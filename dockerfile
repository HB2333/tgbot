FROM python:3.9.19
RUN apt-get update && apt-get install ffmpeg -y
RUN mkdir /tgbot
WORKDIR /tgbot
COPY requirements.txt /tgbot
RUN python3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . /tgbot