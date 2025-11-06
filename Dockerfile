FROM python:3.10-alpine3.22

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache gcc musl-dev postgresql-client postgresql-dev libffi-dev

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

RUN mkdir -p /files/media /files/static \
    && adduser -D -H django-user \
    && chown -R django-user /files/media /files/static \
    && chmod -R 755 /files/media /files/static

COPY . .

USER django-user

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
