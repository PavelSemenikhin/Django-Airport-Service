FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libffi-dev \
    build-essential \
    curl \
    netcat-traditional \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

RUN mkdir -p /files/media /files/static \
    && useradd -m django-user \
    && chown -R django-user /files/media /files/static \
    && chmod -R 755 /files/media /files/static

COPY . .

USER django-user

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
