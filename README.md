

# Портал управления компетенциями и расписанием

Внутренний портал отдела цифровизации строительства.

## Архитектура

```
├── backend/      FastAPI + SQLAlchemy + Alembic + PostgreSQL
├── frontend/     React 18 + TypeScript + Ant Design + react-big-calendar
├── analytics/    Python-скрипт аналитики (Pandas + Matplotlib + Seaborn)
├── reports/      Сгенерированные отчёты (PNG/PDF)
├── hf/           Конфигурация для Hugging Face Spaces (nginx, supervisor)
├── Dockerfile    Сборка для Hugging Face Spaces
└── docker-compose.yml  Локальная разработка
```

---

## Локальный запуск (Docker Compose)

### Требования
- Docker Desktop 4.x+

```bash
git clone https://github.com/nikolajcikstas/Practice-for-BelNeft.git
cd Practice-for-BelNeft
docker compose up --build
```

| Сервис | Адрес |
|--------|-------|
| Фронтенд | http://localhost:3000 |
| API (Swagger) | http://localhost:8000/docs |

### Аналитика

```bash
docker compose --profile analytics run --rm analytics
# PDF вариант:
docker compose --profile analytics run --rm analytics python analytics.py --pdf
```

Отчёты сохраняются в папку `reports/`.

## Структура API

### Сотрудники

| Метод | Путь | Описание |
|-------|------|----------|
| GET | /employees | Список с пагинацией |
| POST | /employees | Добавить сотрудника |
| GET | /employees/{id} | Получить сотрудника |
| PATCH | /employees/{id} | Редактировать |
| DELETE | /employees/{id} | Удалить (только admin) |
| POST | /employees/{id}/skills | Назначить навык |
| PATCH | /employees/{id}/skills/{skill_id} | Изменить уровень |
| GET | /employees/{id}/skills | Навыки сотрудника |

### Навыки

| Метод | Путь | Описание |
|-------|------|----------|
| GET | /skills | Список навыков |
| POST | /skills | Добавить навык |
| DELETE | /skills/{id} | Удалить навык |

### Бронирования

| Метод | Путь | Описание |
|-------|------|----------|
| GET | /bookings?date=YYYY-MM-DD | Список за день |
| POST | /bookings | Создать бронирование |
| DELETE | /bookings/{id} | Отменить |

Конфликт по времени → **409 Conflict**.

---

## Авторизация

Упрощённая идентификация через заголовок `X-User-Id`.
Администраторы задаются через переменную окружения `ADMIN_USER_IDS` (по умолчанию `1`).

## Переменные окружения

| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| `DATABASE_URL` | `postgresql://portal:portal@db:5432/portal` | Подключение к PostgreSQL |
| `ADMIN_USER_IDS` | `1` | ID администраторов через запятую |
