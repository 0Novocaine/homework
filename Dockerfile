FROM ubuntu:latest
LABEL authors="samsungs26"

ENTRYPOINT ["top", "-b"]

FROM python:3.13-slim

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/
COPY . /app

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

RUN mkdir -p /app/storage

CMD ["python", "main.py"]