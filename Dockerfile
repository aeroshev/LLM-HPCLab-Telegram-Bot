FROM python:3.11.5-alpine3.18

RUN pip install -U pip && pip install -U setuptools && pip install -U wheel
RUN pip install -r requirements

CMD ["python", "src/main.py"]
