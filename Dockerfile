FROM python:3.11.5-alpine3.18

COPY requirements.txt requirements.txt

RUN pip install -U pip && pip install -U setuptools && pip install -U wheel
RUN pip install -r requirements.txt && rm -f requirements.txt


CMD ["python", "code/main.py"]
