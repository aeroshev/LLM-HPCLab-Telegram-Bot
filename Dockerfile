FROM python:3.11.5-alpine3.18

# Устновка инструментов
RUN apk add curl -y && sudo apk add gcc -y
RUN curl –proto `=https` –tlsv1.2 -sSf https://sh.rustup.rs | sh && source $HOME/.cargo/env

# Установка Python зависимостей
COPY requirements.txt requirements.txt
RUN pip install -U pip && pip install -U setuptools && pip install -U wheel
RUN pip install -r requirements.txt && rm -f requirements.txt

# Создание специального пользователя для выполнения кода сервера
RUN adduser -D model-python

CMD ["python", "code/main.py"]
