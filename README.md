# Django Airport Service

API сервіс для керування аеропортом на Django REST Framework.

## Основні можливості
- Аутентифікація через JWT
- CRUD для сутностей аеропорту: аеропорти, типи літаків, літаки, маршрути, екіпажі, рейси, замовлення, квитки
- Документація API через drf-spectacular (Swagger)
- Асинхронні задачі через Celery

## Стек
- Python 3.10+
- Django 5.2
- Django REST Framework
- SimpleJWT
- drf-spectacular
- PostgreSQL
- Celery + Redis

## Структура проєкту
- `accounts` — користувачі, профіль, JWT
- `airport_service` — доменні моделі та API
- `config` — налаштування Django, Celery, URL
- `templates`, `files` — додаткові ресурси

## Запуск через Docker
1. Створити `.env` за прикладом (див. `.env` у корені).
2. `docker-compose up --build`
3. Сервер застосунку `app` стартує всередині Docker і доступний на `http://localhost:8000/`.

## Управління застосунком у Docker
- Міграції:
  - `docker-compose exec app python manage.py migrate`
- Суперкористувач:
  - `docker-compose exec app python manage.py createsuperuser`

## Основні URL
- Адмінка: `http://localhost:8000/admin/`
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

## Аутентифікація
- Отримати токен: `POST /api/user/token/`
- Оновити токен: `POST /api/user/token/refresh/`
- Перевірити токен: `POST /api/user/token/verify/`

## Ендпоїнти API
Базовий префікс: `/api/airport_service/`

- `crews/`
- `orders/`
- `tickets/`
- `airports/`
- `flights/`
- `routes/`
- `airplane_types/`

## Нотатки
- Для Celery потрібен Redis.
- В проєкті використовується PostgreSQL (див. `docker-compose.yml`).
