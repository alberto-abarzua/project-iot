FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app

RUN pip install pdm==2.5.2

RUN pdm install

