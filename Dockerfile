FROM alpine:latest

# Core
RUN apk update
RUN apk add python3-dev musl-dev libffi-dev py3-pip gcc openssl-dev
RUN pip3 install python-telegram-bot --upgrade

# Modules
RUN pip3 install requests

# zac-bot
RUN mkdir /home/zac-bot
WORKDIR /home/zac-bot
COPY . .

CMD ./main.py
