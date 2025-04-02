FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.1.15
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.in-project true && \
    poetry install --no-dev --no-interaction

COPY . .

EXPOSE 8080

CMD ["poetry", "run", "sh", "-c", "alembic upgrade head && uvicorn app.main:app --host=0.0.0.0 --port=8080"]