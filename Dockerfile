FROM python:3.11-alpine AS builder

ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.7.1
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

RUN apk update && apk add --no-cache build-base gcc musl-dev postgresql-dev curl netcat-openbsd libffi-dev openssl-dev python3-dev

RUN pip install --upgrade pip && pip install poetry==$POETRY_VERSION

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi
COPY . .

FROM python:3.11-alpine AS final

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk update && apk add --no-cache postgresql-dev curl netcat-openbsd libffi openssl

COPY --from=builder /app /app

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host=0.0.0.0 --port=8000"]
