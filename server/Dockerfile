FROM python:3.11.3-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install pdm==2.4.9

COPY pyproject.toml /app/.
COPY pdm.lock /app/.

RUN pdm install
COPY . .



