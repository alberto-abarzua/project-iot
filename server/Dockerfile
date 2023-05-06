FROM python:3.11.3-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install pdm==2.5.5

COPY pyproject.toml /app/.
COPY pdm.lock /app/.

RUN pdm install
COPY . .



