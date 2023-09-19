FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# Переменные для сборки вместе с GPU
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV NVIDIA_REQUIRE_CUDA="cuda>=12.2"

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && \
    apt install --no-install-recommends -y build-essential software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install --no-install-recommends -y python3.11 python3-pip python3-setuptools python3.11-venv && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Перенос файла зависимостей
COPY requirements.txt requirements.txt

# Создание виртуального окружения
RUN python3.11 -m venv venv
ENV PATH="${HOME}/venv/bin:$PATH"

# Установка Python зависимостей
ENV PIP_NO_CACHE_DIR=1
RUN python -m pip install -U pip && \
    python -m pip install -U setuptools && \
    python -m pip install -U wheel
RUN python -m pip install -r requirements.txt && rm -f requirements.txt

# Точка входа в образ
CMD ["python3.11", "code/main.py"]
