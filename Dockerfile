FROM python:3.11.5-bullseye

ENV PATH="${HOME}/venv/bin:$PATH"
ENV PYTHONPATH="${PYTHNONPATH}/code/src/telegram:${PYTHNONPATH}/code/src/model"
ENV PIP_NO_CACHE_DIR=1

WORKDIR /code
# Перенос файла зависимостей
COPY requirements.txt requirements.txt
# Перенос кода
# COPY src src

# Создание виртуального окружения
RUN python -m venv venv 

# Установка Python зависимостей
RUN python -m pip install -U pip && \
    python -m pip install -U setuptools && \
    python -m pip install -U wheel
RUN python -m pip install -r requirements.txt && rm -f requirements.txt

# Точка входа в образ
CMD ["python", "src/main.py"]
