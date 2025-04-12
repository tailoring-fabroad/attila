FROM python:3.11-alpine AS builder

ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.7.1
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

RUN apk update && apk add --no-cache \
    build-base \
    gcc \
    musl-dev \
    postgresql-dev \
    curl \
    netcat-openbsd \
    libffi-dev \
    openssl-dev \
    python3-dev

RUN pip install --upgrade pip && pip install poetry==1.7.1

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi && \
    poetry cache clear --all pypi

COPY . .

FROM python:3.11-alpine AS final

ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

RUN apk update && apk add --no-cache \
    postgresql-dev \
    curl \
    netcat-openbsd \
    libffi \
    openssl

COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

EXPOSE 8000

CMD ["sh", "-c", "poetry run alembic upgrade head && poetry run uvicorn app.main:app --host=0.0.0.0 --port=8000"]
