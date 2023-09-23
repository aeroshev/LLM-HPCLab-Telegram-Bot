FROM python:3.11.5-bullseye

# Перенос файла зависимостей
COPY requirements.txt requirements.txt

# Создание виртуального окружения
RUN python -m venv venv
ENV PATH="${HOME}/venv/bin:$PATH"

# Установка Python зависимостей
ENV PIP_NO_CACHE_DIR=1
RUN python -m pip install -U pip && \
    python -m pip install -U setuptools && \
    python -m pip install -U wheel
RUN python -m pip install -r requirements.txt && rm -f requirements.txt

# Точка входа в образ
CMD ["python", "code/main.py"]
