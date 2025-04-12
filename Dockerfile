FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk update && \
    apk add --no-cache \
        build-base \
        gcc \
        musl-dev \
        postgresql-dev \
        curl \
        netcat-openbsd \
    rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.7.1
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "poetry run alembic upgrade head && poetry run uvicorn app.main:app --host=0.0.0.0 --port=8000"]
