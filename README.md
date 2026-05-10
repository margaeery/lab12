# Лабораторная работа №12: AI-ассистированная разработка

**Студент:** Ражина Маргарита Александровна  
**Группа:** 220032-11  
**Вариант:** 18 — Система управления гостиницей (Задания средней сложности)

## Описание проекта

REST API для управления номерами гостиницы, построенное на **FastAPI** с использованием **SQLAlchemy** и **PostgreSQL**. Реализованы CRUD-операции для номеров, валидация данных, миграции через Alembic.

Кроме API, проект включает модуль `room_cost_calculator` — калькулятор итоговой стоимости номера с учётом сезонных коэффициентов, количества гостей, дополнительных услуг и скидок за длительность.

---

## Стек технологий

| Технология | Версия | Назначение |
|------------|--------|------------|
| Python | 3.12+ | Язык программирования |
| FastAPI | 0.115.0 | Веб-фреймворк |
| Uvicorn | 0.32.0 | ASGI-сервер |
| SQLAlchemy | 2.0.36 | ORM |
| PostgreSQL | 18 | База данных |
| Pydantic | 2.9.2 | Валидация данных |
| Alembic | 1.14.0 | Миграции БД |
| Pytest | 8.3.3 | Тестирование |
| Docker | — | Контейнеризация |

---

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `DB_HOST` | Хост базы данных | `localhost` |
| `DB_PORT` | Порт PostgreSQL | `5432` |
| `DB_USER` | Имя пользователя БД | `hotel_user` |
| `DB_PASSWORD` | Пароль пользователя БД | `hotel_pass` |
| `DB_NAME` | Название базы данных | `hotel_db` |

---

## Установка и запуск

### Быстрый старт через Docker (рекомендуется)

```bash
# 1. Скопировать шаблон переменных окружения
cp .env.example .env

# 2. Запустить контейнеры
docker-compose up --build

# 3. API доступно по адресу: http://localhost:8000
#    Swagger UI: http://localhost:8000/docs
#    PostgreSQL: localhost:5432
```

Миграции Alembic применяются автоматически перед стартом приложения через `entrypoint.sh`.

**Остановка:**
```bash
docker-compose down
```

**Остановка с удалением данных:**
```bash
docker-compose down -v
```

---

### Локальный запуск (без Docker)

#### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

#### 2. Настройка PostgreSQL

```bash
psql -U postgres
```

```sql
CREATE DATABASE hotel_db;
CREATE USER hotel_user WITH PASSWORD 'hotel_pass';
GRANT ALL PRIVILEGES ON DATABASE hotel_db TO hotel_user;
ALTER DATABASE hotel_db OWNER TO hotel_user;
\c hotel_db
GRANT ALL ON SCHEMA public TO hotel_user;
```

#### 3. Настройка переменных окружения

```bash
cp .env.example .env
```

Отредактируйте `.env` при необходимости.

#### 4. Запуск приложения

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

---

### Запуск тестов

Тесты используют SQLite для изоляции.

```bash
pytest --cov=app --cov=room_cost_calculator --cov-report=term-missing
```

---

## API Endpoints

### Общая информация

- Базовый URL: `http://localhost:8000`
- Формат данных: JSON
- Документация: `/docs` (Swagger UI)

### Модель данных Room

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | `integer` | Уникальный идентификатор | автоинкремент |
| `room_number` | `string` | Номер комнаты | уникальный, обязательный |
| `room_type` | `enum` | Тип номера | `standard`, `suite`, `family` |
| `price_per_night` | `float` | Цена за ночь | `> 0` |
| `floor` | `integer` | Этаж | обязательный |
| `capacity` | `integer` | Вместимость | `> 0` |

---

### 1. Получить все номера

```http
GET /rooms
```

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/rooms" \
  -H "accept: application/json"
```

**Пример ответа (200 OK):**
```json
[
  {
    "id": 1,
    "room_number": "101",
    "room_type": "standard",
    "price_per_night": 2500.0,
    "floor": 1,
    "capacity": 2
  },
  {
    "id": 2,
    "room_number": "202",
    "room_type": "suite",
    "price_per_night": 5000.0,
    "floor": 2,
    "capacity": 4
  }
]
```

---

### 2. Создать новый номер

```http
POST /rooms
```

**Тело запроса (RoomCreate):**

| Поле | Тип | Обязательное | Ограничения |
|------|-----|-------------|-------------|
| `room_number` | `string` | да | `min_length=1`, уникальный |
| `room_type` | `enum` | да | `standard`, `suite`, `family` |
| `price_per_night` | `float` | да | `> 0` |
| `floor` | `integer` | да | — |
| `capacity` | `integer` | да | `> 0` |

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/rooms" \
  -H "Content-Type: application/json" \
  -H "accept: application/json" \
  -d '{
    "room_number": "101",
    "room_type": "standard",
    "price_per_night": 2500.0,
    "floor": 1,
    "capacity": 2
  }'
```

**Пример ответа (201 Created):**
```json
{
  "id": 1,
  "room_number": "101",
  "room_type": "standard",
  "price_per_night": 2500.0,
  "floor": 1,
  "capacity": 2
}
```

**Ошибка (409 Conflict) — номер уже существует:**
```json
{
  "detail": "Room with this room_number already exists"
}
```

**Ошибка (422 Unprocessable Entity) — невалидные данные:**
```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "price_per_night"],
      "msg": "Input should be greater than 0",
      "input": -100
    }
  ]
}
```

---

### 3. Получить номер по ID

```http
GET /rooms/{room_id}
```

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `room_id` | `integer` | ID номера |

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/rooms/1" \
  -H "accept: application/json"
```

**Пример ответа (200 OK):**
```json
{
  "id": 1,
  "room_number": "101",
  "room_type": "standard",
  "price_per_night": 2500.0,
  "floor": 1,
  "capacity": 2
}
```

**Ошибка (404 Not Found):**
```json
{
  "detail": "Room not found"
}
```

---

### 4. Обновить номер

```http
PUT /rooms/{room_id}
```

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `room_id` | `integer` | ID номера |

**Тело запроса (RoomUpdate) — все поля опциональные:**

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `room_number` | `string` | `min_length=1` |
| `room_type` | `enum` | `standard`, `suite`, `family` |
| `price_per_night` | `float` | `> 0` |
| `floor` | `integer` | — |
| `capacity` | `integer` | `> 0` |

**Пример запроса:**
```bash
curl -X PUT "http://localhost:8000/rooms/1" \
  -H "Content-Type: application/json" \
  -H "accept: application/json" \
  -d '{
    "price_per_night": 3000.0,
    "capacity": 3
  }'
```

**Пример ответа (200 OK):**
```json
{
  "id": 1,
  "room_number": "101",
  "room_type": "standard",
  "price_per_night": 3000.0,
  "floor": 1,
  "capacity": 3
}
```

**Ошибка (409 Conflict) — номер уже существует:**
```json
{
  "detail": "Room with this room_number already exists"
}
```

**Ошибка (404 Not Found):**
```json
{
  "detail": "Room not found"
}
```

---

### 5. Удалить номер

```http
DELETE /rooms/{room_id}
```

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `room_id` | `integer` | ID номера |

**Пример запроса:**
```bash
curl -X DELETE "http://localhost:8000/rooms/1"
```

**Ответ:**
- `204 No Content` — успешное удаление (тело пустое)

**Ошибка (404 Not Found):**
```json
{
  "detail": "Room not found"
}
```

---

### Сводная таблица эндпоинтов

| Метод | Эндпоинт | Описание | Коды ответа |
|-------|----------|----------|-------------|
| `GET` | `/rooms` | Получить все номера | 200 |
| `POST` | `/rooms` | Создать новый номер | 201, 409, 422 |
| `GET` | `/rooms/{id}` | Получить номер по ID | 200, 404 |
| `PUT` | `/rooms/{id}` | Обновить номер | 200, 404, 409, 422 |
| `DELETE` | `/rooms/{id}` | Удалить номер | 204, 404 |

---

## Калькулятор стоимости проживания

Модуль `room_cost_calculator` рассчитывает итоговую стоимость номера с учётом множества факторов.

### Использование

```python
from room_cost_calculator.calculator import calculate_total_cost, Season, ExtraService

total = calculate_total_cost(
    price_per_night=2500.0,
    nights=10,
    guests=4,
    season=Season.PEAK,
    extra_service=ExtraService.BREAKFAST,
)
```

### Параметры

| Параметр | Тип | Описание |
|----------|-----|----------|
| `price_per_night` | `float` | Цена за одну ночь |
| `nights` | `int` | Количество ночей |
| `guests` | `int` | Количество гостей |
| `season` | `Season` | Сезон: `PEAK`, `SHOULDER`, `OFF_SEASON`, `NORMAL` |
| `extra_service` | `ExtraService | None` | Доп. услуга: `BREAKFAST`, `PARKING`, `SPA` |

### Сезонные коэффициенты

| Сезон | Множитель | Налог |
|-------|-----------|-------|
| `PEAK` | 1.5 | 10% |
| `SHOULDER` | 1.2 | 5% |
| `OFF_SEASON` | 0.8 | 0% |
| `NORMAL` | 1.0 | 0% |

## Рефакторинг калькулятора

### Исходная версия — `bad_calculator.py`

Функция `f(p, n, g, s, e)` содержала:
- неинформативные имена переменных (`p`, `n`, `g`, `s`, `e`)
- магические числа без пояснений (`1.5`, `500`, `0.95`)
- дублирование проверок (`g > 2`, `e == 1`) в нескольких местах
- отсутствие валидации входных данных
- побочный эффект `print()` внутри функции

### Отрефакторенная версия — `calculator.py`

- Понятные имена: `calculate_total_cost(price_per_night, nights, guests, ...)`
- Перечисления: `Season` и `ExtraService`
- Константы в словарях: `SEASON_MULTIPLIERS`, `EXTRA_BASE_FEES` и др.
- Вспомогательные функции: `_guest_tiered_surcharge`, `_duration_discount` и др.
- Валидация: проверка на положительность параметров
- Удалён `print`, функция возвращает `round(total, 2)`
- Type hints для всех параметров
---

## Структура проекта

```
lab12/
├── app/
│   ├── __init__.py
│   ├── database.py          # Подключение к БД
│   ├── enums.py             # Перечисления (RoomType)
│   ├── main.py              # FastAPI приложение
│   ├── models.py            # SQLAlchemy модели
│   └── schemas.py           # Pydantic схемы
├── room_cost_calculator/
│   ├── __init__.py
│   ├── bad_calculator.py    # Исходная "плохая" версия
│   └── calculator.py        # Отрефакторенная версия
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Фикстуры pytest
│   ├── test_calculator.py   # Тесты калькулятора
│   └── test_main.py         # Тесты API
├── alembic/                 # Миграции БД
├── .env.example             # Шаблон переменных окружения
├── docker-compose.yml       # Docker Compose
├── Dockerfile               # Образ приложения
├── entrypoint.sh            # Скрипт запуска
├── requirements.txt         # Зависимости Python
├── explanation.md           # Объяснение бизнес-логики
└── README.md                # Документация
```

---
