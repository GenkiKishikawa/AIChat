FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  git \
  curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN git config --global --add safe.directory /app

RUN pip install --upgrade pip && \
  pip install poetry

COPY pyproject.toml* poetry.lock* ./

RUN poetry config virtualenvs.in-project true
RUN if [ -f pyproject.toml ]; then poetry install --no-root; fi
